#pragma once

#include <string>
#include <vector>
#include <map>
#include <chrono>
#include <random>
#include <cstring>
#include <openssl/sha.h>
#include <openssl/evp.h>
#include <jwt-cpp/jwt.h>

namespace circuit {

class SecurityManager {
public:
    struct UserSession {
        std::string token;
        std::string user_id;
        std::chrono::system_clock::time_point expiry;
        std::string ip_address;
        std::vector<std::string> permissions;
    };

    struct SecurityAudit {
        std::string event_id;
        std::string user_id;
        std::string action;
        std::string resource;
        std::string ip_address;
        std::chrono::system_clock::time_point timestamp;
        bool success;
        std::string details;
    };

    SecurityManager(const std::string& secret_key) 
        : secret_key_(secret_key) {
        initializeSecurity();
    }

    std::string hashPassword(const std::string& password) {
        unsigned char hash[SHA256_DIGEST_LENGTH];
        std::string salt = generateSalt();
        
        // Combine password and salt
        std::string salted = password + salt;
        
        SHA256_CTX sha256;
        SHA256_Init(&sha256);
        SHA256_Update(&sha256, salted.c_str(), salted.length());
        SHA256_Final(hash, &sha256);
        
        // Convert to hex string
        std::stringstream ss;
        for(int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
            ss << std::hex << std::setw(2) << std::setfill('0') 
               << static_cast<int>(hash[i]);
        }
        
        return salt + ":" + ss.str();
    }

    bool verifyPassword(const std::string& password, 
                       const std::string& stored_hash) {
        size_t separator = stored_hash.find(':');
        if (separator == std::string::npos) return false;
        
        std::string salt = stored_hash.substr(0, separator);
        std::string hash = stored_hash.substr(separator + 1);
        
        return hashPassword(password + salt) == hash;
    }

    std::string generateToken(const std::string& user_id, 
                            const std::vector<std::string>& permissions) {
        auto token = jwt::create()
            .set_issuer("recycling_system")
            .set_type("JWS")
            .set_issued_at(std::chrono::system_clock::now())
            .set_expires_at(std::chrono::system_clock::now() + 
                          std::chrono::hours(24))
            .set_payload_claim("user_id", jwt::claim(user_id))
            .set_payload_claim("permissions", 
                             jwt::claim(permissionsToString(permissions)))
            .sign(jwt::algorithm::hs256{secret_key_});
        
        // Create session
        UserSession session;
        session.token = token;
        session.user_id = user_id;
        session.expiry = std::chrono::system_clock::now() + 
                        std::chrono::hours(24);
        session.permissions = permissions;
        
        active_sessions_[token] = session;
        
        return token;
    }

    bool validateToken(const std::string& token) {
        try {
            auto decoded = jwt::decode(token);
            auto verifier = jwt::verify()
                .allow_algorithm(jwt::algorithm::hs256{secret_key_})
                .with_issuer("recycling_system");
            
            verifier.verify(decoded);
            
            // Check if session exists and is not expired
            auto it = active_sessions_.find(token);
            if (it == active_sessions_.end()) return false;
            
            return std::chrono::system_clock::now() < it->second.expiry;
        }
        catch (const std::exception&) {
            return false;
        }
    }

    bool checkPermission(const std::string& token, 
                        const std::string& required_permission) {
        auto it = active_sessions_.find(token);
        if (it == active_sessions_.end()) return false;
        
        return std::find(it->second.permissions.begin(),
                        it->second.permissions.end(),
                        required_permission) != it->second.permissions.end();
    }

    void revokeToken(const std::string& token) {
        active_sessions_.erase(token);
    }

    void logSecurityEvent(const std::string& user_id,
                         const std::string& action,
                         const std::string& resource,
                         bool success,
                         const std::string& details) {
        SecurityAudit audit;
        audit.event_id = generateEventId();
        audit.user_id = user_id;
        audit.action = action;
        audit.resource = resource;
        audit.timestamp = std::chrono::system_clock::now();
        audit.success = success;
        audit.details = details;
        
        security_log_.push_back(audit);
        
        // If this is a security violation, take action
        if (!success) {
            handleSecurityViolation(audit);
        }
    }

    std::vector<SecurityAudit> getSecurityLog(
        const std::string& user_id = "") {
        if (user_id.empty()) {
            return security_log_;
        }
        
        std::vector<SecurityAudit> filtered_log;
        for (const auto& audit : security_log_) {
            if (audit.user_id == user_id) {
                filtered_log.push_back(audit);
            }
        }
        return filtered_log;
    }

private:
    std::string secret_key_;
    std::map<std::string, UserSession> active_sessions_;
    std::vector<SecurityAudit> security_log_;
    std::map<std::string, int> failed_attempts_;

    void initializeSecurity() {
        OpenSSL_add_all_algorithms();
    }

    std::string generateSalt() {
        const int SALT_LENGTH = 16;
        static const char alphanum[] =
            "0123456789"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz";
        
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, sizeof(alphanum) - 2);
        
        std::string salt;
        for (int i = 0; i < SALT_LENGTH; ++i) {
            salt += alphanum[dis(gen)];
        }
        
        return salt;
    }

    std::string generateEventId() {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::uniform_int_distribution<> dis(0, 15);
        static const char* digits = "0123456789abcdef";
        
        std::string uuid;
        for (int i = 0; i < 32; ++i) {
            uuid += digits[dis(gen)];
            if (i == 7 || i == 11 || i == 15 || i == 19) {
                uuid += "-";
            }
        }
        return uuid;
    }

    std::string permissionsToString(
        const std::vector<std::string>& permissions) {
        std::string result;
        for (const auto& perm : permissions) {
            if (!result.empty()) result += ",";
            result += perm;
        }
        return result;
    }

    void handleSecurityViolation(const SecurityAudit& audit) {
        // Track failed attempts
        failed_attempts_[audit.user_id]++;
        
        // If too many failed attempts, lock the account
        if (failed_attempts_[audit.user_id] >= 5) {
            // Lock account
            logSecurityEvent(audit.user_id,
                           "ACCOUNT_LOCKED",
                           "USER_ACCOUNT",
                           true,
                           "Too many failed attempts");
        }
        
        // Log severe violations
        if (audit.action == "UNAUTHORIZED_ACCESS" || 
            audit.action == "INVALID_TOKEN" ||
            audit.action == "PERMISSION_DENIED") {
            // Implement additional security measures
            // e.g., notify administrators, block IP, etc.
        }
    }
};

} // namespace circuit
