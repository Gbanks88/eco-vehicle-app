#pragma once

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include "SecurityManager.hpp"

namespace circuit {

class AutodeskIntegration {
public:
    struct ModelMetadata {
        std::string urn;
        std::string version_id;
        std::string object_id;
        std::string file_name;
        std::string file_type;
        double file_size;
        std::string creation_date;
        std::string last_modified_date;
    };

    struct ViewerConfig {
        std::string access_token;
        std::string document_urn;
        std::vector<std::string> extensions;
        std::string environment;  // "AutodeskProduction" or "AutodeskStaging"
    };

    struct CredentialStatus {
        bool valid;
        std::string message;
        std::chrono::seconds token_lifetime;
        bool token_expired;
    };

    AutodeskIntegration(
        std::shared_ptr<SecurityManager> security_manager,
        const std::string& client_id,
        const std::string& client_secret,
        const std::string& callback_url)
        : security_manager_(security_manager),
          client_id_(client_id),
          client_secret_(client_secret),
          callback_url_(callback_url) {
        
        curl_global_init(CURL_GLOBAL_DEFAULT);
    }

    ~AutodeskIntegration() {
        curl_global_cleanup();
    }

    // Authentication
    bool authenticate() {
        try {
            CURL* curl = curl_easy_init();
            if (!curl) return false;

            std::string auth_url = "https://developer.api.autodesk.com/authentication/v1/authenticate";
            std::string post_data = 
                "client_id=" + client_id_ +
                "&client_secret=" + client_secret_ +
                "&grant_type=client_credentials" +
                "&scope=data:read data:write data:create bucket:read bucket:create";

            struct curl_slist* headers = nullptr;
            headers = curl_slist_append(headers, "Content-Type: application/x-www-form-urlencoded");

            curl_easy_setopt(curl, CURLOPT_URL, auth_url.c_str());
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_data.c_str());
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

            std::string response;
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

            CURLcode res = curl_easy_perform(curl);
            
            curl_slist_free_all(headers);
            curl_easy_cleanup(curl);

            if (res != CURLE_OK) {
                last_error_ = "Failed to connect to Autodesk API: " + 
                             std::string(curl_easy_strerror(res));
                return false;
            }

            try {
                auto json = nlohmann::json::parse(response);
                
                if (json.contains("error")) {
                    last_error_ = "Authentication failed: " + 
                                 json["error"].get<std::string>();
                    if (json.contains("error_description")) {
                        last_error_ += " - " + 
                                     json["error_description"].get<std::string>();
                    }
                    return false;
                }

                access_token_ = json["access_token"];
                token_type_ = json["token_type"];
                expires_in_ = json["expires_in"];
                token_timestamp_ = std::chrono::system_clock::now();

                return true;
            }
            catch (const std::exception& e) {
                last_error_ = "Failed to parse authentication response: " + 
                             std::string(e.what());
                return false;
            }
        }
        catch (const std::exception& e) {
            return false;
        }
    }

    CredentialStatus checkCredentials() {
        CredentialStatus status{false, "", std::chrono::seconds(0), true};

        // Check if credentials are empty
        if (client_id_.empty() || client_secret_.empty()) {
            status.message = "Client ID or Client Secret is empty";
            return status;
        }

        // Check if we already have a valid token
        if (!access_token_.empty() && !token_expired()) {
            auto remaining = getRemainingTokenTime();
            status.valid = true;
            status.message = "Valid token exists";
            status.token_lifetime = remaining;
            status.token_expired = false;
            return status;
        }

        // Try to authenticate
        if (authenticate()) {
            status.valid = true;
            status.message = "Successfully authenticated with Autodesk API";
            status.token_lifetime = std::chrono::seconds(expires_in_);
            status.token_expired = false;
        } else {
            status.message = "Authentication failed: " + last_error_;
        }

        return status;
    }

    std::string getLastError() const {
        return last_error_;
    }

    // Model Upload and Translation
    std::optional<std::string> uploadModel(
        const std::string& file_path,
        const std::string& bucket_key) {
        
        try {
            if (!isAuthenticated()) {
                if (!authenticate()) return std::nullopt;
            }

            // Create bucket if it doesn't exist
            if (!createBucket(bucket_key)) return std::nullopt;

            // Upload file to bucket
            CURL* curl = curl_easy_init();
            if (!curl) return std::nullopt;

            std::string upload_url = 
                "https://developer.api.autodesk.com/oss/v2/buckets/" + 
                bucket_key + "/objects/" + getFileName(file_path);

            struct curl_slist* headers = nullptr;
            headers = curl_slist_append(headers, 
                ("Authorization: Bearer " + access_token_).c_str());

            FILE* fd = fopen(file_path.c_str(), "rb");
            if (!fd) {
                curl_easy_cleanup(curl);
                return std::nullopt;
            }

            curl_easy_setopt(curl, CURLOPT_URL, upload_url.c_str());
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
            curl_easy_setopt(curl, CURLOPT_UPLOAD, 1L);
            curl_easy_setopt(curl, CURLOPT_READDATA, fd);

            std::string response;
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

            CURLcode res = curl_easy_perform(curl);
            
            fclose(fd);
            curl_slist_free_all(headers);
            curl_easy_cleanup(curl);

            if (res != CURLE_OK) return std::nullopt;

            auto json = nlohmann::json::parse(response);
            return json["objectId"];
        }
        catch (const std::exception& e) {
            return std::nullopt;
        }
    }

    bool translateModel(
        const std::string& object_id,
        const std::string& output_format = "svf") {
        
        try {
            if (!isAuthenticated()) {
                if (!authenticate()) return false;
            }

            CURL* curl = curl_easy_init();
            if (!curl) return false;

            std::string job_url = 
                "https://developer.api.autodesk.com/modelderivative/v2/designdata/job";

            nlohmann::json job_payload = {
                {"input", {
                    {"urn", base64Encode(object_id)}
                }},
                {"output", {
                    {"formats", {{
                        {"type", output_format},
                        {"views", {"2d", "3d"}}
                    }}}
                }}
            };

            struct curl_slist* headers = nullptr;
            headers = curl_slist_append(headers, 
                ("Authorization: Bearer " + access_token_).c_str());
            headers = curl_slist_append(headers, 
                "Content-Type: application/json");

            curl_easy_setopt(curl, CURLOPT_URL, job_url.c_str());
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, 
                           job_payload.dump().c_str());

            std::string response;
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

            CURLcode res = curl_easy_perform(curl);
            
            curl_slist_free_all(headers);
            curl_easy_cleanup(curl);

            return res == CURLE_OK;
        }
        catch (const std::exception& e) {
            return false;
        }
    }

    // Viewer Configuration
    ViewerConfig getViewerConfig(const std::string& document_urn) {
        return ViewerConfig{
            access_token_,
            document_urn,
            {"Viewing", "DrawingViewable"},
            "AutodeskProduction"
        };
    }

    // Model Metadata
    std::optional<ModelMetadata> getModelMetadata(
        const std::string& object_id) {
        
        try {
            if (!isAuthenticated()) {
                if (!authenticate()) return std::nullopt;
            }

            CURL* curl = curl_easy_init();
            if (!curl) return std::nullopt;

            std::string metadata_url = 
                "https://developer.api.autodesk.com/modelderivative/v2/designdata/" +
                base64Encode(object_id) + "/metadata";

            struct curl_slist* headers = nullptr;
            headers = curl_slist_append(headers, 
                ("Authorization: Bearer " + access_token_).c_str());

            curl_easy_setopt(curl, CURLOPT_URL, metadata_url.c_str());
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

            std::string response;
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

            CURLcode res = curl_easy_perform(curl);
            
            curl_slist_free_all(headers);
            curl_easy_cleanup(curl);

            if (res != CURLE_OK) return std::nullopt;

            auto json = nlohmann::json::parse(response);
            
            ModelMetadata metadata;
            metadata.urn = json["urn"];
            metadata.version_id = json["version_id"];
            metadata.object_id = object_id;
            metadata.file_name = json["name"];
            metadata.file_type = json["type"];
            metadata.file_size = json["size"];
            metadata.creation_date = json["created_date"];
            metadata.last_modified_date = json["modified_date"];

            return metadata;
        }
        catch (const std::exception& e) {
            return std::nullopt;
        }
    }

private:
    std::shared_ptr<SecurityManager> security_manager_;
    std::string client_id_;
    std::string client_secret_;
    std::string callback_url_;
    std::string access_token_;
    std::string token_type_;
    int expires_in_;
    std::string last_error_;
    std::chrono::system_clock::time_point token_timestamp_;

    bool isAuthenticated() const {
        return !access_token_.empty();
    }

    bool token_expired() const {
        if (access_token_.empty()) return true;
        
        auto now = std::chrono::system_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
            now - token_timestamp_).count();
        
        return elapsed >= expires_in_;
    }

    std::chrono::seconds getRemainingTokenTime() const {
        if (access_token_.empty()) return std::chrono::seconds(0);
        
        auto now = std::chrono::system_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
            now - token_timestamp_).count();
        
        return std::chrono::seconds(
            std::max(0, expires_in_ - static_cast<int>(elapsed)));
    }

    bool createBucket(const std::string& bucket_key) {
        try {
            CURL* curl = curl_easy_init();
            if (!curl) return false;

            std::string bucket_url = 
                "https://developer.api.autodesk.com/oss/v2/buckets";

            nlohmann::json bucket_payload = {
                {"bucketKey", bucket_key},
                {"policyKey", "transient"}
            };

            struct curl_slist* headers = nullptr;
            headers = curl_slist_append(headers, 
                ("Authorization: Bearer " + access_token_).c_str());
            headers = curl_slist_append(headers, 
                "Content-Type: application/json");

            curl_easy_setopt(curl, CURLOPT_URL, bucket_url.c_str());
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, 
                           bucket_payload.dump().c_str());

            std::string response;
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

            CURLcode res = curl_easy_perform(curl);
            
            curl_slist_free_all(headers);
            curl_easy_cleanup(curl);

            return res == CURLE_OK;
        }
        catch (const std::exception& e) {
            return false;
        }
    }

    static std::string getFileName(const std::string& path) {
        size_t pos = path.find_last_of("/\\");
        return pos == std::string::npos ? path : path.substr(pos + 1);
    }

    static std::string base64Encode(const std::string& input) {
        static const std::string base64_chars = 
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

        std::string encoded;
        int i = 0;
        int j = 0;
        unsigned char char_array_3[3];
        unsigned char char_array_4[4];

        for (char c : input) {
            char_array_3[i++] = c;
            if (i == 3) {
                char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
                char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + 
                                 ((char_array_3[1] & 0xf0) >> 4);
                char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + 
                                 ((char_array_3[2] & 0xc0) >> 6);
                char_array_4[3] = char_array_3[2] & 0x3f;

                for(i = 0; i < 4; i++)
                    encoded += base64_chars[char_array_4[i]];
                i = 0;
            }
        }

        if (i) {
            for(j = i; j < 3; j++)
                char_array_3[j] = '\0';

            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + 
                             ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + 
                             ((char_array_3[2] & 0xc0) >> 6);

            for (j = 0; j < i + 1; j++)
                encoded += base64_chars[char_array_4[j]];

            while((i++ < 3))
                encoded += '=';
        }

        return encoded;
    }

    static size_t WriteCallback(void* contents, 
                              size_t size, 
                              size_t nmemb, 
                              void* userp) {
        ((std::string*)userp)->append((char*)contents, size * nmemb);
        return size * nmemb;
    }
};

} // namespace circuit
