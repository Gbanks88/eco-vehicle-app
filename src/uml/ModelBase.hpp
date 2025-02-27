#pragma once

#include "Diagram.hpp"
#include <string>
#include <memory>
#include <map>
#include <filesystem>

namespace uml {

class ModelBase {
public:
    static ModelBase& getInstance() {
        static ModelBase instance;
        return instance;
    }

    void createDiagram(const std::string& name, DiagramType type) {
        diagrams_[name] = std::make_shared<Diagram>(name, type);
    }

    std::shared_ptr<Diagram> getDiagram(const std::string& name) const {
        auto it = diagrams_.find(name);
        return (it != diagrams_.end()) ? it->second : nullptr;
    }

    void saveDiagram(const std::string& name, const std::filesystem::path& path) {
        auto diagram = getDiagram(name);
        if (!diagram) return;

        // TODO: Implement diagram serialization
    }

    void loadDiagram(const std::filesystem::path& path) {
        // TODO: Implement diagram deserialization
    }

    void exportToXMI(const std::string& diagramName, const std::filesystem::path& path) {
        auto diagram = getDiagram(diagramName);
        if (!diagram) return;

        // TODO: Implement XMI export
    }

    void importFromXMI(const std::filesystem::path& path) {
        // TODO: Implement XMI import
    }

    const std::map<std::string, std::shared_ptr<Diagram>>& getDiagrams() const {
        return diagrams_;
    }

private:
    ModelBase() = default;
    ModelBase(const ModelBase&) = delete;
    ModelBase& operator=(const ModelBase&) = delete;

    std::map<std::string, std::shared_ptr<Diagram>> diagrams_;
};

} // namespace uml
