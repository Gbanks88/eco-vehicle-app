#pragma once

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <sqlite3.h>
#include <sstream>
#include <optional>
#include <filesystem>

namespace circuit {

class PersistentStorage {
public:
    struct QueryResult {
        std::vector<std::vector<std::string>> rows;
        std::vector<std::string> columns;
        bool success;
        std::string error_message;
    };

    PersistentStorage(const std::string& db_path) 
        : db_path_(db_path) {
        initializeDatabase();
    }

    ~PersistentStorage() {
        if (db_) {
            sqlite3_close(db_);
        }
    }

    bool executeQuery(const std::string& query) {
        char* error_message = nullptr;
        int result = sqlite3_exec(db_, 
                                query.c_str(), 
                                nullptr, 
                                nullptr, 
                                &error_message);
        
        if (result != SQLITE_OK) {
            last_error_ = error_message;
            sqlite3_free(error_message);
            return false;
        }
        
        return true;
    }

    QueryResult executeSelect(const std::string& query) {
        QueryResult result;
        sqlite3_stmt* stmt;
        
        int rc = sqlite3_prepare_v2(db_, 
                                  query.c_str(), 
                                  -1, 
                                  &stmt, 
                                  nullptr);
        
        if (rc != SQLITE_OK) {
            result.success = false;
            result.error_message = sqlite3_errmsg(db_);
            return result;
        }
        
        // Get column names
        int col_count = sqlite3_column_count(stmt);
        for (int i = 0; i < col_count; i++) {
            result.columns.push_back(
                sqlite3_column_name(stmt, i));
        }
        
        // Get rows
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            std::vector<std::string> row;
            for (int i = 0; i < col_count; i++) {
                const unsigned char* text = sqlite3_column_text(stmt, i);
                row.push_back(text ? reinterpret_cast<const char*>(text) : "");
            }
            result.rows.push_back(row);
        }
        
        sqlite3_finalize(stmt);
        result.success = true;
        return result;
    }

    bool beginTransaction() {
        return executeQuery("BEGIN TRANSACTION;");
    }

    bool commitTransaction() {
        return executeQuery("COMMIT;");
    }

    bool rollbackTransaction() {
        return executeQuery("ROLLBACK;");
    }

    bool backup(const std::string& backup_path) {
        sqlite3* backup_db;
        if (sqlite3_open(backup_path.c_str(), &backup_db) != SQLITE_OK) {
            last_error_ = sqlite3_errmsg(backup_db);
            sqlite3_close(backup_db);
            return false;
        }
        
        sqlite3_backup* backup = sqlite3_backup_init(backup_db, "main",
                                                   db_, "main");
        
        if (!backup) {
            last_error_ = sqlite3_errmsg(backup_db);
            sqlite3_close(backup_db);
            return false;
        }
        
        sqlite3_backup_step(backup, -1);
        sqlite3_backup_finish(backup);
        
        if (sqlite3_errcode(backup_db) != SQLITE_OK) {
            last_error_ = sqlite3_errmsg(backup_db);
            sqlite3_close(backup_db);
            return false;
        }
        
        sqlite3_close(backup_db);
        return true;
    }

    std::string getLastError() const {
        return last_error_;
    }

private:
    sqlite3* db_;
    std::string db_path_;
    std::string last_error_;

    void initializeDatabase() {
        // Open database
        if (sqlite3_open(db_path_.c_str(), &db_) != SQLITE_OK) {
            throw std::runtime_error("Failed to open database: " + 
                                   std::string(sqlite3_errmsg(db_)));
        }

        // Create tables if they don't exist
        createTables();
    }

    void createTables() {
        // Components table
        executeQuery(R"(
            CREATE TABLE IF NOT EXISTS components (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                manufacturer TEXT,
                received_date INTEGER,
                condition TEXT,
                weight REAL,
                material_composition TEXT
            );
        )");

        // Recycling records table
        executeQuery(R"(
            CREATE TABLE IF NOT EXISTS recycling_records (
                id TEXT PRIMARY KEY,
                component_id TEXT,
                operator_id TEXT,
                process_date INTEGER,
                process_type TEXT,
                success INTEGER,
                recovered_materials TEXT,
                recovery_efficiency REAL,
                FOREIGN KEY(component_id) REFERENCES components(id),
                FOREIGN KEY(operator_id) REFERENCES operators(id)
            );
        )");

        // Operators table
        executeQuery(R"(
            CREATE TABLE IF NOT EXISTS operators (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                certification_level TEXT,
                certifications TEXT,
                last_training INTEGER,
                total_components_processed INTEGER,
                efficiency_rating REAL
            );
        )");

        // Users table
        executeQuery(R"(
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at INTEGER,
                last_login INTEGER,
                is_active INTEGER
            );
        )");

        // Permissions table
        executeQuery(R"(
            CREATE TABLE IF NOT EXISTS permissions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                permission TEXT,
                granted_at INTEGER,
                granted_by TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        )");

        // Audit log table
        executeQuery(R"(
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT,
                resource TEXT,
                timestamp INTEGER,
                success INTEGER,
                details TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        )");

        // Create indices
        executeQuery("CREATE INDEX IF NOT EXISTS idx_components_type ON components(type);");
        executeQuery("CREATE INDEX IF NOT EXISTS idx_recycling_date ON recycling_records(process_date);");
        executeQuery("CREATE INDEX IF NOT EXISTS idx_operators_cert ON operators(certification_level);");
        executeQuery("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);");
    }
};

} // namespace circuit
