#pragma once

#include <string>
#include <vector>
#include <memory>
#include <bsoncxx/json.hpp>
#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>
#include <mongocxx/uri.hpp>
#include "SecurityManager.hpp"
#include "DatabaseManager.hpp"

namespace circuit {

class MongoDBManager {
public:
    struct MongoConfig {
        std::string uri;
        std::string database;
        std::string components_collection;
        std::string recycling_collection;
        std::string operators_collection;
        std::string metrics_collection;
        bool enable_ssl;
        std::string ssl_ca_file;
        std::string ssl_cert_file;
    };

    struct IndexConfig {
        std::string collection;
        std::string field;
        bool unique;
        bool sparse;
        int expireAfterSeconds;
    };

    MongoDBManager(std::shared_ptr<SecurityManager> security_manager,
                  const MongoConfig& config)
        : security_manager_(security_manager),
          config_(config) {
        
        mongocxx::instance::current();
        
        mongocxx::options::client client_options;
        if (config.enable_ssl) {
            mongocxx::options::ssl ssl_options;
            ssl_options.ca_file(config.ssl_ca_file);
            ssl_options.pem_file(config.ssl_cert_file);
            client_options.ssl_opts(ssl_options);
        }
        
        client_ = std::make_unique<mongocxx::client>(
            mongocxx::uri{config.uri}, client_options);
        
        db_ = (*client_)[config.database];
        
        setupCollections();
        createIndices();
    }

    // Component operations
    bool saveComponent(const DatabaseManager::ComponentRecord& component) {
        try {
            auto doc = bsoncxx::builder::stream::document{} 
                << "_id" << component.id
                << "type" << component.type
                << "manufacturer" << component.manufacturer
                << "received_date" << bsoncxx::types::b_date{
                    component.received_date}
                << "condition" << component.condition
                << "weight" << component.weight
                << bsoncxx::builder::stream::finalize;

            // Add material composition
            auto materials = bsoncxx::builder::stream::document{};
            for (const auto& [material, amount] : component.material_composition) {
                materials << material << amount;
            }
            doc.view()["material_composition"] = materials.view();

            db_[config_.components_collection].insert_one(doc.view());
            return true;
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
            return false;
        }
    }

    // Recycling record operations
    bool saveRecyclingRecord(const DatabaseManager::RecyclingRecord& record) {
        try {
            auto doc = bsoncxx::builder::stream::document{}
                << "_id" << record.id
                << "component_id" << record.component_id
                << "operator_id" << record.operator_id
                << "process_date" << bsoncxx::types::b_date{
                    record.process_date}
                << "process_type" << record.process_type
                << "success" << record.success
                << "recovery_efficiency" << record.recovery_efficiency
                << bsoncxx::builder::stream::finalize;

            // Add recovered materials
            auto materials = bsoncxx::builder::stream::document{};
            for (const auto& [material, amount] : record.recovered_materials) {
                materials << material << amount;
            }
            doc.view()["recovered_materials"] = materials.view();

            db_[config_.recycling_collection].insert_one(doc.view());
            return true;
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
            return false;
        }
    }

    // Operator operations
    bool saveOperator(const DatabaseManager::OperatorRecord& op) {
        try {
            auto doc = bsoncxx::builder::stream::document{}
                << "_id" << op.id
                << "name" << op.name
                << "certification_level" << op.certification_level
                << "last_training" << bsoncxx::types::b_date{
                    op.last_training}
                << "total_components_processed" << op.total_components_processed
                << "efficiency_rating" << op.efficiency_rating
                << bsoncxx::builder::stream::finalize;

            // Add certifications array
            auto cert_array = bsoncxx::builder::stream::array{};
            for (const auto& cert : op.certifications) {
                cert_array << cert;
            }
            doc.view()["certifications"] = cert_array.view();

            db_[config_.operators_collection].insert_one(doc.view());
            return true;
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
            return false;
        }
    }

    // Metrics and analytics
    void saveMetrics(const std::string& metric_type,
                    const std::map<std::string, double>& values,
                    const std::chrono::system_clock::time_point& timestamp) {
        try {
            auto doc = bsoncxx::builder::stream::document{}
                << "type" << metric_type
                << "timestamp" << bsoncxx::types::b_date{timestamp}
                << bsoncxx::builder::stream::finalize;

            // Add values
            auto values_doc = bsoncxx::builder::stream::document{};
            for (const auto& [key, value] : values) {
                values_doc << key << value;
            }
            doc.view()["values"] = values_doc.view();

            db_[config_.metrics_collection].insert_one(doc.view());
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
        }
    }

    // Aggregation pipeline for analytics
    std::vector<bsoncxx::document::value> runAggregation(
        const std::string& collection,
        const std::vector<bsoncxx::document::value>& pipeline) {
        
        std::vector<bsoncxx::document::value> results;
        
        try {
            auto cursor = db_[collection].aggregate(pipeline);
            for (auto&& doc : cursor) {
                results.push_back(bsoncxx::document::value(doc));
            }
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
        }
        
        return results;
    }

    std::string getLastError() const {
        return last_error_;
    }

private:
    std::shared_ptr<SecurityManager> security_manager_;
    MongoConfig config_;
    std::unique_ptr<mongocxx::client> client_;
    mongocxx::database db_;
    std::string last_error_;

    void setupCollections() {
        try {
            // Create collections if they don't exist
            if (!collectionExists(config_.components_collection)) {
                db_.create_collection(config_.components_collection);
            }
            if (!collectionExists(config_.recycling_collection)) {
                db_.create_collection(config_.recycling_collection);
            }
            if (!collectionExists(config_.operators_collection)) {
                db_.create_collection(config_.operators_collection);
            }
            if (!collectionExists(config_.metrics_collection)) {
                db_.create_collection(config_.metrics_collection);
            }
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
        }
    }

    void createIndices() {
        try {
            // Components collection indices
            createIndex({
                config_.components_collection,
                "manufacturer",
                false,
                false,
                0
            });

            // Recycling collection indices
            createIndex({
                config_.recycling_collection,
                "component_id",
                false,
                false,
                0
            });
            createIndex({
                config_.recycling_collection,
                "operator_id",
                false,
                false,
                0
            });

            // Operators collection indices
            createIndex({
                config_.operators_collection,
                "certification_level",
                false,
                false,
                0
            });

            // Metrics collection indices
            createIndex({
                config_.metrics_collection,
                "timestamp",
                false,
                false,
                7 * 24 * 60 * 60  // Expire after 1 week
            });
        }
        catch (const std::exception& e) {
            last_error_ = e.what();
        }
    }

    bool collectionExists(const std::string& name) {
        auto collections = db_.list_collections();
        return std::any_of(collections.begin(), collections.end(),
            [&name](const bsoncxx::document::view& doc) {
                return doc["name"].get_string().value == name;
            });
    }

    void createIndex(const IndexConfig& config) {
        auto index = bsoncxx::builder::stream::document{}
            << config.field << 1
            << bsoncxx::builder::stream::finalize;

        mongocxx::options::index options;
        options.unique(config.unique);
        options.sparse(config.sparse);
        
        if (config.expireAfterSeconds > 0) {
            options.expire_after(
                std::chrono::seconds(config.expireAfterSeconds));
        }

        db_[config.collection].create_index(index.view(), options);
    }
};

} // namespace circuit
