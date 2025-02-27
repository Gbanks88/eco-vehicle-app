-- Requirements Management Database Schema

-- Requirements Table
CREATE TABLE requirements (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    rationale TEXT,
    source VARCHAR(100),
    version VARCHAR(20),
    created_date TIMESTAMP NOT NULL,
    modified_date TIMESTAMP NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    modified_by VARCHAR(100) NOT NULL,
    CONSTRAINT chk_type CHECK (type IN ('Functional', 'Performance', 'Interface', 'Security', 'Safety', 'Environmental', 'Regulatory', 'UserInterface')),
    CONSTRAINT chk_priority CHECK (priority IN ('Critical', 'High', 'Medium', 'Low')),
    CONSTRAINT chk_status CHECK (status IN ('Draft', 'Review', 'Approved', 'Implemented', 'Verified', 'Validated', 'Rejected', 'Obsolete'))
);

-- Custom Fields Table
CREATE TABLE requirement_custom_fields (
    requirement_id VARCHAR(50),
    field_name VARCHAR(100),
    field_value TEXT,
    PRIMARY KEY (requirement_id, field_name),
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE
);

-- Dependencies Table
CREATE TABLE requirement_dependencies (
    requirement_id VARCHAR(50),
    dependent_req_id VARCHAR(50),
    dependency_type VARCHAR(50),
    PRIMARY KEY (requirement_id, dependent_req_id),
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    FOREIGN KEY (dependent_req_id) REFERENCES requirements(id) ON DELETE CASCADE
);

-- Components Table
CREATE TABLE components (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50),
    description TEXT
);

-- Component Links Table
CREATE TABLE requirement_component_links (
    requirement_id VARCHAR(50),
    component_id VARCHAR(50),
    link_type VARCHAR(50),
    created_date TIMESTAMP NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    PRIMARY KEY (requirement_id, component_id),
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE
);

-- Test Cases Table
CREATE TABLE test_cases (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    created_date TIMESTAMP NOT NULL,
    modified_date TIMESTAMP NOT NULL
);

-- Test Case Links Table
CREATE TABLE requirement_testcase_links (
    requirement_id VARCHAR(50),
    testcase_id VARCHAR(50),
    link_type VARCHAR(50),
    created_date TIMESTAMP NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    PRIMARY KEY (requirement_id, testcase_id),
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    FOREIGN KEY (testcase_id) REFERENCES test_cases(id) ON DELETE CASCADE
);

-- Use Cases Table
CREATE TABLE use_cases (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    actor VARCHAR(100),
    preconditions TEXT,
    postconditions TEXT,
    created_date TIMESTAMP NOT NULL,
    modified_date TIMESTAMP NOT NULL
);

-- Use Case Links Table
CREATE TABLE requirement_usecase_links (
    requirement_id VARCHAR(50),
    usecase_id VARCHAR(50),
    link_type VARCHAR(50),
    created_date TIMESTAMP NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    PRIMARY KEY (requirement_id, usecase_id),
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    FOREIGN KEY (usecase_id) REFERENCES use_cases(id) ON DELETE CASCADE
);

-- System V Documents Table
CREATE TABLE system_v_documents (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL,
    content TEXT,
    phase VARCHAR(50) NOT NULL,
    created_date TIMESTAMP NOT NULL,
    modified_date TIMESTAMP NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    modified_by VARCHAR(100) NOT NULL,
    CONSTRAINT chk_phase CHECK (phase IN ('Concept', 'Requirements', 'Design', 'Implementation', 'Testing', 'Deployment', 'Maintenance'))
);

-- System V Document Links Table
CREATE TABLE requirement_systemv_links (
    requirement_id VARCHAR(50),
    document_id VARCHAR(50),
    link_type VARCHAR(50),
    created_date TIMESTAMP NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    PRIMARY KEY (requirement_id, document_id),
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES system_v_documents(id) ON DELETE CASCADE
);

-- Verification Status Table
CREATE TABLE verification_status (
    requirement_id VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    verified_by VARCHAR(100),
    verified_date TIMESTAMP,
    method VARCHAR(50),
    results TEXT,
    comments TEXT,
    PRIMARY KEY (requirement_id),
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    CONSTRAINT chk_verification_status CHECK (status IN ('Not Started', 'In Progress', 'Passed', 'Failed', 'Blocked'))
);

-- Validation Status Table
CREATE TABLE validation_status (
    requirement_id VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    validated_by VARCHAR(100),
    validated_date TIMESTAMP,
    method VARCHAR(50),
    results TEXT,
    comments TEXT,
    PRIMARY KEY (requirement_id),
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    CONSTRAINT chk_validation_status CHECK (status IN ('Not Started', 'In Progress', 'Passed', 'Failed', 'Blocked'))
);

-- Change History Table
CREATE TABLE requirement_changes (
    id SERIAL PRIMARY KEY,
    requirement_id VARCHAR(50),
    change_type VARCHAR(50) NOT NULL,
    changed_by VARCHAR(100) NOT NULL,
    changed_date TIMESTAMP NOT NULL,
    old_value TEXT,
    new_value TEXT,
    comments TEXT,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_req_type ON requirements(type);
CREATE INDEX idx_req_status ON requirements(status);
CREATE INDEX idx_req_priority ON requirements(priority);
CREATE INDEX idx_req_created_date ON requirements(created_date);
CREATE INDEX idx_req_modified_date ON requirements(modified_date);
CREATE INDEX idx_component_links ON requirement_component_links(requirement_id, component_id);
CREATE INDEX idx_testcase_links ON requirement_testcase_links(requirement_id, testcase_id);
CREATE INDEX idx_usecase_links ON requirement_usecase_links(requirement_id, usecase_id);
CREATE INDEX idx_systemv_links ON requirement_systemv_links(requirement_id, document_id);
CREATE INDEX idx_verification_status ON verification_status(requirement_id, status);
CREATE INDEX idx_validation_status ON validation_status(requirement_id, status);
CREATE INDEX idx_requirement_changes ON requirement_changes(requirement_id, changed_date);
