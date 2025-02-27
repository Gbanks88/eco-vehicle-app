-- Model Repository Database Schema

-- Models Table
CREATE TABLE models (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    version VARCHAR(50) NOT NULL,
    author VARCHAR(100) NOT NULL,
    created_date TIMESTAMP NOT NULL,
    modified_date TIMESTAMP NOT NULL,
    checked_out_by VARCHAR(100),
    fusion_document_id VARCHAR(100),
    preview_image VARCHAR(200),
    is_locked BOOLEAN DEFAULT FALSE,
    CONSTRAINT chk_type CHECK (type IN ('Assembly', 'Component', 'Drawing', 'Simulation', 'Analysis', 'Manufacturing')),
    CONSTRAINT chk_status CHECK (status IN ('Draft', 'InReview', 'Approved', 'Released', 'Obsolete', 'Archived'))
);

-- Model Tags Table
CREATE TABLE model_tags (
    model_id VARCHAR(50),
    tag VARCHAR(100),
    PRIMARY KEY (model_id, tag),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Model Properties Table
CREATE TABLE model_properties (
    model_id VARCHAR(50),
    property_name VARCHAR(100),
    property_value TEXT,
    PRIMARY KEY (model_id, property_name),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Model Requirements Links Table
CREATE TABLE model_requirement_links (
    model_id VARCHAR(50),
    requirement_id VARCHAR(50),
    link_type VARCHAR(50),
    created_date TIMESTAMP NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    PRIMARY KEY (model_id, requirement_id),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Flow Models Table
CREATE TABLE flow_models (
    id VARCHAR(50) PRIMARY KEY,
    model_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    version VARCHAR(50) NOT NULL,
    created_date TIMESTAMP NOT NULL,
    modified_date TIMESTAMP NOT NULL,
    author VARCHAR(100) NOT NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Flow Activities Table
CREATE TABLE flow_activities (
    id VARCHAR(50) PRIMARY KEY,
    flow_model_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    activity_type VARCHAR(50) NOT NULL,
    x_position FLOAT NOT NULL,
    y_position FLOAT NOT NULL,
    width FLOAT NOT NULL,
    height FLOAT NOT NULL,
    properties JSON,
    FOREIGN KEY (flow_model_id) REFERENCES flow_models(id) ON DELETE CASCADE,
    CONSTRAINT chk_activity_type CHECK (activity_type IN ('Task', 'Process', 'SubProcess', 'Event', 'Gateway'))
);

-- Flow Connections Table
CREATE TABLE flow_connections (
    id VARCHAR(50) PRIMARY KEY,
    flow_model_id VARCHAR(50) NOT NULL,
    source_id VARCHAR(50) NOT NULL,
    target_id VARCHAR(50) NOT NULL,
    connection_type VARCHAR(50) NOT NULL,
    properties JSON,
    FOREIGN KEY (flow_model_id) REFERENCES flow_models(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES flow_activities(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES flow_activities(id) ON DELETE CASCADE,
    CONSTRAINT chk_connection_type CHECK (connection_type IN ('SequenceFlow', 'MessageFlow', 'DataFlow', 'Association'))
);

-- Flow Data Objects Table
CREATE TABLE flow_data_objects (
    id VARCHAR(50) PRIMARY KEY,
    flow_model_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    object_type VARCHAR(50) NOT NULL,
    x_position FLOAT NOT NULL,
    y_position FLOAT NOT NULL,
    width FLOAT NOT NULL,
    height FLOAT NOT NULL,
    properties JSON,
    FOREIGN KEY (flow_model_id) REFERENCES flow_models(id) ON DELETE CASCADE,
    CONSTRAINT chk_object_type CHECK (object_type IN ('DataObject', 'DataStore', 'Buffer', 'Parameter'))
);

-- Flow Events Table
CREATE TABLE flow_events (
    id VARCHAR(50) PRIMARY KEY,
    flow_model_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL,
    x_position FLOAT NOT NULL,
    y_position FLOAT NOT NULL,
    width FLOAT NOT NULL,
    height FLOAT NOT NULL,
    properties JSON,
    FOREIGN KEY (flow_model_id) REFERENCES flow_models(id) ON DELETE CASCADE,
    CONSTRAINT chk_event_type CHECK (event_type IN ('Start', 'End', 'Intermediate', 'Signal', 'Timer', 'Error'))
);

-- Flow Gateways Table
CREATE TABLE flow_gateways (
    id VARCHAR(50) PRIMARY KEY,
    flow_model_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    gateway_type VARCHAR(50) NOT NULL,
    x_position FLOAT NOT NULL,
    y_position FLOAT NOT NULL,
    width FLOAT NOT NULL,
    height FLOAT NOT NULL,
    properties JSON,
    FOREIGN KEY (flow_model_id) REFERENCES flow_models(id) ON DELETE CASCADE,
    CONSTRAINT chk_gateway_type CHECK (gateway_type IN ('Exclusive', 'Inclusive', 'Parallel', 'Complex'))
);

-- Flow Annotations Table
CREATE TABLE flow_annotations (
    id VARCHAR(50) PRIMARY KEY,
    flow_model_id VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    x_position FLOAT NOT NULL,
    y_position FLOAT NOT NULL,
    width FLOAT NOT NULL,
    height FLOAT NOT NULL,
    properties JSON,
    FOREIGN KEY (flow_model_id) REFERENCES flow_models(id) ON DELETE CASCADE
);

-- Flow Versions Table
CREATE TABLE flow_versions (
    id VARCHAR(50) PRIMARY KEY,
    flow_model_id VARCHAR(50) NOT NULL,
    version_number VARCHAR(50) NOT NULL,
    created_date TIMESTAMP NOT NULL,
    author VARCHAR(100) NOT NULL,
    description TEXT,
    data JSON NOT NULL,
    FOREIGN KEY (flow_model_id) REFERENCES flow_models(id) ON DELETE CASCADE
);

-- Create indexes for flow modeling tables
CREATE INDEX idx_flow_models ON flow_models(model_id);
CREATE INDEX idx_flow_activities ON flow_activities(flow_model_id);
CREATE INDEX idx_flow_connections ON flow_connections(flow_model_id);
CREATE INDEX idx_flow_data_objects ON flow_data_objects(flow_model_id);
CREATE INDEX idx_flow_events ON flow_events(flow_model_id);
CREATE INDEX idx_flow_gateways ON flow_gateways(flow_model_id);
CREATE INDEX idx_flow_annotations ON flow_annotations(flow_model_id);
CREATE INDEX idx_flow_versions ON flow_versions(flow_model_id);

-- Model Dependencies Table
CREATE TABLE model_dependencies (
    model_id VARCHAR(50),
    dependency_id VARCHAR(50),
    dependency_type VARCHAR(50),
    is_required BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (model_id, dependency_id),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    FOREIGN KEY (dependency_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Version History Table
CREATE TABLE version_history (
    model_id VARCHAR(50),
    version VARCHAR(50),
    description TEXT,
    author VARCHAR(100) NOT NULL,
    date TIMESTAMP NOT NULL,
    change_log TEXT,
    parent_version VARCHAR(50),
    is_major BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (model_id, version),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Checkout History Table
CREATE TABLE checkout_history (
    model_id VARCHAR(50),
    user_id VARCHAR(100),
    checkout_time TIMESTAMP NOT NULL,
    checkin_time TIMESTAMP,
    working_copy VARCHAR(200),
    is_exclusive BOOLEAN DEFAULT FALSE,
    comment TEXT,
    PRIMARY KEY (model_id, user_id, checkout_time),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Model Files Table
CREATE TABLE model_files (
    model_id VARCHAR(50),
    version VARCHAR(50),
    file_path VARCHAR(200) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    hash VARCHAR(64) NOT NULL,
    upload_date TIMESTAMP NOT NULL,
    PRIMARY KEY (model_id, version),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Model Preview Images Table
CREATE TABLE model_previews (
    model_id VARCHAR(50),
    version VARCHAR(50),
    preview_path VARCHAR(200) NOT NULL,
    thumbnail_path VARCHAR(200),
    generated_date TIMESTAMP NOT NULL,
    PRIMARY KEY (model_id, version),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Model Change History Table
CREATE TABLE model_changes (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(50),
    change_type VARCHAR(50) NOT NULL,
    changed_by VARCHAR(100) NOT NULL,
    changed_date TIMESTAMP NOT NULL,
    old_value TEXT,
    new_value TEXT,
    comments TEXT,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Model Access Control Table
CREATE TABLE model_access_control (
    model_id VARCHAR(50),
    user_id VARCHAR(100),
    permission_type VARCHAR(50),
    granted_by VARCHAR(100) NOT NULL,
    granted_date TIMESTAMP NOT NULL,
    expiry_date TIMESTAMP,
    PRIMARY KEY (model_id, user_id, permission_type),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Model Storage Table
CREATE TABLE model_storage (
    model_id VARCHAR(50) PRIMARY KEY,
    total_size BIGINT NOT NULL,
    last_accessed TIMESTAMP NOT NULL,
    archive_status VARCHAR(50),
    archive_date TIMESTAMP,
    archive_location VARCHAR(200),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_model_name ON models(name);
CREATE INDEX idx_model_type ON models(type);
CREATE INDEX idx_model_status ON models(status);
CREATE INDEX idx_model_version ON models(version);
CREATE INDEX idx_model_author ON models(author);
CREATE INDEX idx_model_dates ON models(created_date, modified_date);
CREATE INDEX idx_model_checkout ON models(checked_out_by);
CREATE INDEX idx_version_history ON version_history(model_id, version);
CREATE INDEX idx_checkout_history ON checkout_history(model_id, user_id);
CREATE INDEX idx_model_files ON model_files(model_id, version);
CREATE INDEX idx_model_changes ON model_changes(model_id, changed_date);
CREATE INDEX idx_model_storage ON model_storage(model_id, archive_status);
