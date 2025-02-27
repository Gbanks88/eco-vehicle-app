"""
JSON schemas for UML model validation with enhanced rules and patterns
"""

# Schema version
SCHEMA_VERSION = "1.0.0"

# Common patterns
NAME_PATTERN = "^[a-zA-Z_][a-zA-Z0-9_]*$"
TYPE_PATTERN = "^[a-zA-Z_][a-zA-Z0-9_<>,\[\]]*$"

# Common definitions
VISIBILITY_ENUM = ["public", "private", "protected", "package"]
RELATIONSHIP_TYPES = ["generalization", "realization", "dependency", "association", "composition", "aggregation"]

# Schema for metadata
METADATA_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string", "pattern": "^\d+\.\d+\.\d+$"},
        "author": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
        "description": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["version", "created_at", "updated_at"]
}

# Enhanced model schema
MODEL_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "metadata": {"$ref": "#/definitions/metadata"},
        "name": {"type": "string", "pattern": NAME_PATTERN},
        "packages": {
            "type": "array",
            "items": {"$ref": "#/definitions/package"},
            "minItems": 1
        },
        "relationships": {
            "type": "array",
            "items": {"$ref": "#/definitions/relationship"}
        }
    },
    "required": ["metadata", "name", "packages"],
    "additionalProperties": False,
    "definitions": {
        "metadata": METADATA_SCHEMA,
        "package": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "pattern": NAME_PATTERN},
                "id": {"type": "string", "format": "uuid"},
                "description": {"type": "string"},
                "stereotypes": {
                    "type": "array",
                    "items": {"type": "string", "pattern": NAME_PATTERN}
                },
                "properties": {"type": "object"},
                "elements": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/element"},
                    "minItems": 1
                }
            },
            "required": ["name", "id", "elements"],
            "additionalProperties": False
        },
        "element": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["class", "interface", "enum", "annotation"]},
                "name": {"type": "string", "pattern": NAME_PATTERN},
                "id": {"type": "string", "format": "uuid"},
                "description": {"type": "string"},
                "is_abstract": {"type": "boolean"},
                "is_interface": {"type": "boolean"},
                "is_final": {"type": "boolean"},
                "stereotypes": {
                    "type": "array",
                    "items": {"type": "string", "pattern": NAME_PATTERN}
                },
                "properties": {"type": "object"},
                "attributes": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/attribute"}
                },
                "operations": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/operation"}
                }
            },
            "required": ["type", "name", "id"],
            "additionalProperties": False,
            "allOf": [
                {
                    "if": {"properties": {"type": {"const": "interface"}}},
                    "then": {"properties": {"is_interface": {"const": true}}}
                },
                {
                    "if": {"properties": {"type": {"const": "enum"}}},
                    "then": {"properties": {"attributes": {"minItems": 1}}}
                }
            ]
        },
        "attribute": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "pattern": NAME_PATTERN},
                "type": {"type": "string", "pattern": TYPE_PATTERN},
                "visibility": {"type": "string", "enum": VISIBILITY_ENUM},
                "description": {"type": "string"},
                "is_static": {"type": "boolean"},
                "is_final": {"type": "boolean"},
                "is_transient": {"type": "boolean"},
                "default_value": {"type": ["string", "number", "boolean", "null"]},
                "multiplicity": {
                    "type": "string",
                    "pattern": "^(\\d+|\\*)(\.\.(\\d+|\\*))?$"
                }
            },
            "required": ["name", "type", "visibility"],
            "additionalProperties": False
        },
        "operation": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "pattern": NAME_PATTERN},
                "return_type": {"type": "string", "pattern": TYPE_PATTERN},
                "description": {"type": "string"},
                "parameters": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/parameter"}
                },
                "visibility": {"type": "string", "enum": VISIBILITY_ENUM},
                "is_static": {"type": "boolean"},
                "is_abstract": {"type": "boolean"},
                "is_final": {"type": "boolean"},
                "exceptions": {
                    "type": "array",
                    "items": {"type": "string", "pattern": TYPE_PATTERN}
                }
            },
            "required": ["name", "return_type", "parameters", "visibility"],
            "additionalProperties": False
        },
        "parameter": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "pattern": NAME_PATTERN},
                "type": {"type": "string", "pattern": TYPE_PATTERN},
                "description": {"type": "string"},
                "default_value": {"type": ["string", "number", "boolean", "null"]},
                "is_varargs": {"type": "boolean"}
            },
            "required": ["name", "type"],
            "additionalProperties": False
        },
        "relationship": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": RELATIONSHIP_TYPES},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "source": {"type": "string", "format": "uuid"},
                "target": {"type": "string", "format": "uuid"},
                "source_multiplicity": {
                    "type": "string",
                    "pattern": "^(\\d+|\\*)(\.\.(\\d+|\\*))?$"
                },
                "target_multiplicity": {
                    "type": "string",
                    "pattern": "^(\\d+|\\*)(\.\.(\\d+|\\*))?$"
                },
                "source_role": {"type": "string", "pattern": NAME_PATTERN},
                "target_role": {"type": "string", "pattern": NAME_PATTERN},
                "stereotypes": {
                    "type": "array",
                    "items": {"type": "string", "pattern": NAME_PATTERN}
                },
                "properties": {"type": "object"}
            },
            "required": ["type", "source", "target"],
            "additionalProperties": False,
            "allOf": [
                {
                    "if": {
                        "properties": {
                            "type": {"enum": ["association", "composition", "aggregation"]}
                        }
                    },
                    "then": {
                        "required": ["source_multiplicity", "target_multiplicity"]
                    }
                }
            ]
        }
    }
}
        },
        "relationships": {
            "type": "array",
            "items": {"$ref": "#/definitions/relationship"}
        }
    },
    "required": ["version", "name", "packages", "relationships"],
    "definitions": {
        "package": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "id": {"type": "string", "format": "uuid"},
                "stereotypes": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "properties": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                },
                "elements": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/element"}
                }
            },
            "required": ["name", "id", "elements"]
        },
        "element": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["class", "interface"]},
                "name": {"type": "string"},
                "id": {"type": "string", "format": "uuid"},
                "stereotypes": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "properties": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                },
                "attributes": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/attribute"}
                },
                "operations": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/operation"}
                },
                "is_abstract": {"type": "boolean"},
                "is_interface": {"type": "boolean"}
            },
            "required": ["type", "name", "id"]
        },
        "attribute": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "visibility": {"type": "string", "enum": ["public", "private", "protected", "package"]},
                "default_value": {"type": ["string", "null"]},
                "is_static": {"type": "boolean"},
                "is_final": {"type": "boolean"}
            },
            "required": ["name", "type", "visibility"]
        },
        "operation": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "return_type": {"type": ["string", "null"]},
                "parameters": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": [
                            {"type": "string"},
                            {"type": "string"}
                        ]
                    }
                },
                "visibility": {"type": "string", "enum": ["public", "private", "protected", "package"]},
                "is_static": {"type": "boolean"},
                "is_abstract": {"type": "boolean"}
            },
            "required": ["name", "visibility"]
        },
        "relationship": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "id": {"type": "string", "format": "uuid"},
                "source": {"type": "string", "format": "uuid"},
                "target": {"type": "string", "format": "uuid"},
                "relationship_type": {"type": "string", "enum": ["association", "generalization", "dependency", "aggregation", "composition", "realization"]},
                "stereotypes": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "properties": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                },
                "multiplicity_source": {"type": "string"},
                "multiplicity_target": {"type": "string"},
                "navigability_source": {"type": "boolean"},
                "navigability_target": {"type": "boolean"}
            },
            "required": ["name", "id", "source", "target", "relationship_type"]
        }
    }
}
