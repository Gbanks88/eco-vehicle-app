"""
Model serialization and deserialization with support for JSON, YAML, and XMI formats.
Includes validation and versioning support.
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
import xml.etree.ElementTree as ET
import yaml
from jsonschema import validate
from .core import (
    Model, Package, Class, Attribute, Operation,
    Relationship, Association, Generalization, Dependency
)
from .schemas import MODEL_SCHEMA

class ModelSerializer:
    """Handles serialization of UML models to various formats including JSON, YAML, and XMI.
    Includes support for validation and versioning."""
    
    VERSION = "1.0.0"  # Model format version

    @staticmethod
    def to_dict(model: Model, author: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """Convert model to dictionary with metadata"""
        now = datetime.utcnow().isoformat()
        data = {
            "version": ModelSerializer.VERSION,
            "metadata": {
                "author": author or "unknown",
                "created_at": now,
                "updated_at": now,
                "description": description or ""
            },
            "name": model.name,
            "packages": [ModelSerializer._package_to_dict(p) for p in model.packages],
            "relationships": [ModelSerializer._relationship_to_dict(r) for r in model.relationships]
        }
        # Validate against schema
        validate(instance=data, schema=MODEL_SCHEMA)
        return data

    @staticmethod
    def _package_to_dict(package: Package) -> Dict[str, Any]:
        """Convert package to dictionary"""
        return {
            "name": package.name,
            "id": str(package.id),
            "stereotypes": list(package.stereotypes),
            "properties": package.properties,
            "elements": [ModelSerializer._element_to_dict(e) for e in package.elements]
        }

    @staticmethod
    def _element_to_dict(element: Any) -> Dict[str, Any]:
        """Convert element to dictionary"""
        if isinstance(element, Class):
            return {
                "type": "class",
                "name": element.name,
                "id": str(element.id),
                "stereotypes": list(element.stereotypes),
                "properties": element.properties,
                "attributes": [ModelSerializer._attribute_to_dict(a) for a in element.attributes],
                "operations": [ModelSerializer._operation_to_dict(o) for o in element.operations],
                "is_abstract": element.is_abstract,
                "is_interface": element.is_interface
            }
        return {}

    @staticmethod
    def _attribute_to_dict(attr: Attribute) -> Dict[str, Any]:
        """Convert attribute to dictionary"""
        return {
            "name": attr.name,
            "type": attr.type,
            "visibility": attr.visibility,
            "default_value": attr.default_value,
            "is_static": attr.is_static,
            "is_final": attr.is_final
        }

    @staticmethod
    def _operation_to_dict(op: Operation) -> Dict[str, Any]:
        """Convert operation to dictionary"""
        return {
            "name": op.name,
            "return_type": op.return_type,
            "parameters": op.parameters,
            "visibility": op.visibility,
            "is_static": op.is_static,
            "is_abstract": op.is_abstract
        }

    @staticmethod
    def _relationship_to_dict(rel: Relationship) -> Dict[str, Any]:
        """Convert relationship to dictionary"""
        base_dict = {
            "name": rel.name,
            "id": str(rel.id),
            "source": str(rel.source),
            "target": str(rel.target),
            "relationship_type": rel.relationship_type,
            "stereotypes": list(rel.stereotypes),
            "properties": rel.properties
        }

        if isinstance(rel, Association):
            base_dict.update({
                "multiplicity_source": rel.multiplicity_source,
                "multiplicity_target": rel.multiplicity_target,
                "navigability_source": rel.navigability_source,
                "navigability_target": rel.navigability_target
            })

        return base_dict

    def to_json(self, model: Model, indent: int = 2, author: Optional[str] = None, description: Optional[str] = None) -> str:
        """Convert model to JSON string with metadata"""
        return json.dumps(self.to_dict(model, author, description), indent=indent)
        
    def to_yaml(self, model: Model, author: Optional[str] = None, description: Optional[str] = None) -> str:
        """Convert model to YAML string with metadata"""
        return yaml.dump(self.to_dict(model, author, description), sort_keys=False)
        
    def to_xmi(self, model: Model, author: Optional[str] = None, description: Optional[str] = None) -> str:
        """Convert model to XMI 2.1 format"""
        # Create root element
        xmi = ET.Element('xmi:XMI')
        xmi.set('xmlns:xmi', 'http://schema.omg.org/spec/XMI/2.1')
        xmi.set('xmlns:uml', 'http://schema.omg.org/spec/UML/2.1')
        xmi.set('xmi:version', '2.1')
        
        # Add documentation
        doc = ET.SubElement(xmi, 'xmi:Documentation')
        ET.SubElement(doc, 'xmi:exporter').text = 'Eco Vehicle UML Modeler'
        ET.SubElement(doc, 'xmi:exporterVersion').text = self.VERSION
        if author:
            ET.SubElement(doc, 'xmi:author').text = author
        if description:
            ET.SubElement(doc, 'xmi:description').text = description
            
        # Add model
        uml_model = ET.SubElement(xmi, 'uml:Model')
        uml_model.set('xmi:type', 'uml:Model')
        uml_model.set('name', model.name)
        
        # Add packages
        for package in model.packages:
            pkg_elem = ET.SubElement(uml_model, 'packagedElement')
            pkg_elem.set('xmi:type', 'uml:Package')
            pkg_elem.set('xmi:id', str(package.id))
            pkg_elem.set('name', package.name)
            
            # Add classes
            for element in package.elements:
                if isinstance(element, Class):
                    class_elem = ET.SubElement(pkg_elem, 'packagedElement')
                    class_elem.set('xmi:type', 'uml:Class')
                    class_elem.set('xmi:id', str(element.id))
                    class_elem.set('name', element.name)
                    if element.is_abstract:
                        class_elem.set('isAbstract', 'true')
                    
                    # Add attributes
                    for attr in element.attributes:
                        attr_elem = ET.SubElement(class_elem, 'ownedAttribute')
                        attr_elem.set('xmi:type', 'uml:Property')
                        attr_elem.set('name', attr.name)
                        attr_elem.set('visibility', attr.visibility)
                        
                        type_elem = ET.SubElement(attr_elem, 'type')
                        type_elem.set('xmi:type', 'uml:PrimitiveType')
                        type_elem.set('href', f'http://schema.omg.org/spec/UML/2.1/{attr.type}')
                    
                    # Add operations
                    for op in element.operations:
                        op_elem = ET.SubElement(class_elem, 'ownedOperation')
                        op_elem.set('xmi:type', 'uml:Operation')
                        op_elem.set('name', op.name)
                        op_elem.set('visibility', op.visibility)
                        if op.is_abstract:
                            op_elem.set('isAbstract', 'true')
                        
                        # Add parameters
                        for param_name, param_type in op.parameters:
                            param_elem = ET.SubElement(op_elem, 'ownedParameter')
                            param_elem.set('xmi:type', 'uml:Parameter')
                            param_elem.set('name', param_name)
                            
                            type_elem = ET.SubElement(param_elem, 'type')
                            type_elem.set('xmi:type', 'uml:PrimitiveType')
                            type_elem.set('href', f'http://schema.omg.org/spec/UML/2.1/{param_type}')
        
        # Add relationships
        for rel in model.relationships:
            rel_elem = ET.SubElement(uml_model, 'packagedElement')
            if isinstance(rel, Generalization):
                rel_elem.set('xmi:type', 'uml:Generalization')
            elif isinstance(rel, Association):
                rel_elem.set('xmi:type', 'uml:Association')
            elif isinstance(rel, Dependency):
                rel_elem.set('xmi:type', 'uml:Dependency')
            
            rel_elem.set('xmi:id', str(rel.id))
            rel_elem.set('name', rel.name)
            
            # Add source and target
            source = ET.SubElement(rel_elem, 'source')
            source.set('xmi:idref', str(rel.source))
            target = ET.SubElement(rel_elem, 'target')
            target.set('xmi:idref', str(rel.target))
        
        # Convert to string
        return ET.tostring(xmi, encoding='unicode', method='xml')
        return json.dumps(self.to_dict(model), indent=indent)

    def to_yaml(self, model: Model) -> str:
        """Convert model to YAML string"""
        return yaml.dump(self.to_dict(model))

class ModelDeserializer:
    """Handles deserialization of UML models from various formats including JSON, YAML, and XMI.
    Includes validation and versioning support."""

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Model:
        """Create model from dictionary with validation"""
        # Validate against schema
        validate(instance=data, schema=MODEL_SCHEMA)

        # Check version compatibility
        version = data.get("version", "0.0.0")
        if version != ModelSerializer.VERSION:
            print(f"Warning: Model version mismatch. Expected {ModelSerializer.VERSION}, got {version}")

        model = Model(name=data["name"])

        # Create packages
        for package_data in data["packages"]:
            package = ModelDeserializer._create_package(package_data)
            model.add_package(package)

        # Create relationships
        for rel_data in data["relationships"]:
            relationship = ModelDeserializer._create_relationship(rel_data)
            model.add_relationship(relationship)

        return model

    @staticmethod
    def _create_package(data: Dict[str, Any]) -> Package:
        """Create package from dictionary"""
        package = Package(
            name=data["name"],
            id=UUID(data["id"])
        )
        
        # Add stereotypes and properties
        package.stereotypes = set(data["stereotypes"])
        package.properties = data["properties"]

        # Create elements
        for element_data in data["elements"]:
            if element_data["type"] == "class":
                element = ModelDeserializer._create_class(element_data)
                package.add_element(element)

        return package

    @staticmethod
    def _create_class(data: Dict[str, Any]) -> Class:
        """Create class from dictionary"""
        cls = Class(
            name=data["name"],
            id=UUID(data["id"]),
            is_abstract=data["is_abstract"],
            is_interface=data["is_interface"]
        )

        # Add stereotypes and properties
        cls.stereotypes = set(data["stereotypes"])
        cls.properties = data["properties"]

        # Create attributes
        for attr_data in data["attributes"]:
            attribute = Attribute(
                name=attr_data["name"],
                type=attr_data["type"],
                visibility=attr_data["visibility"],
                default_value=attr_data["default_value"],
                is_static=attr_data["is_static"],
                is_final=attr_data["is_final"]
            )
            cls.add_attribute(attribute)

        # Create operations
        for op_data in data["operations"]:
            operation = Operation(
                name=op_data["name"],
                return_type=op_data["return_type"],
                parameters=op_data["parameters"],
                visibility=op_data["visibility"],
                is_static=op_data["is_static"],
                is_abstract=op_data["is_abstract"]
            )
            cls.add_operation(operation)

        return cls

    @staticmethod
    def _create_relationship(data: Dict[str, Any]) -> Relationship:
        """Create relationship from dictionary"""
        rel_type = data["relationship_type"]
        source = UUID(data["source"])
        target = UUID(data["target"])

        if rel_type == "generalization":
            rel = Generalization(data["name"], source, target)
        elif rel_type == "dependency":
            rel = Dependency(data["name"], source, target)
        else:
            rel = Association(
                name=data["name"],
                source=source,
                target=target,
                relationship_type=rel_type,
                multiplicity_source=data["multiplicity_source"],
                multiplicity_target=data["multiplicity_target"],
                navigability_source=data["navigability_source"],
                navigability_target=data["navigability_target"]
            )

        # Add stereotypes and properties
        rel.stereotypes = set(data["stereotypes"])
        rel.properties = data["properties"]

        return rel

    def from_json(self, json_str: str) -> Model:
        """Create model from JSON string with validation"""
        data = json.loads(json_str)
        return self.from_dict(data)

    def from_yaml(self, yaml_str: str) -> Model:
        """Create model from YAML string with validation"""
        data = yaml.safe_load(yaml_str)
        return self.from_dict(data)

    def from_xmi(self, xmi_str: str) -> Model:
        """Create model from XMI string"""
        # Parse XMI
        root = ET.fromstring(xmi_str)

        # Get model name
        uml_model = root.find('.//uml:Model', {
            'uml': 'http://schema.omg.org/spec/UML/2.1',
            'xmi': 'http://schema.omg.org/spec/XMI/2.1'
        })
        model_name = uml_model.get('name', 'Unnamed Model')
        model = Model(model_name)

        # Process packages
        for pkg_elem in uml_model.findall('.//packagedElement[@xmi:type="uml:Package"]', {
            'xmi': 'http://schema.omg.org/spec/XMI/2.1'
        }):
            package = Package(
                name=pkg_elem.get('name'),
                id=UUID(pkg_elem.get('xmi:id'))
            )

            # Process classes in package
            for class_elem in pkg_elem.findall('.//packagedElement[@xmi:type="uml:Class"]', {
                'xmi': 'http://schema.omg.org/spec/XMI/2.1'
            }):
                cls = Class(
                    name=class_elem.get('name'),
                    id=UUID(class_elem.get('xmi:id')),
                    is_abstract=class_elem.get('isAbstract') == 'true'
                )

                # Process attributes
                for attr_elem in class_elem.findall('.//ownedAttribute', {
                    'xmi': 'http://schema.omg.org/spec/XMI/2.1'
                }):
                    type_elem = attr_elem.find('type')
                    type_href = type_elem.get('href', '')
                    type_name = type_href.split('/')[-1]

                    attr = Attribute(
                        name=attr_elem.get('name'),
                        type=type_name,
                        visibility=attr_elem.get('visibility', 'private')
                    )
                    cls.add_attribute(attr)

                # Process operations
                for op_elem in class_elem.findall('.//ownedOperation', {
                    'xmi': 'http://schema.omg.org/spec/XMI/2.1'
                }):
                    op = Operation(
                        name=op_elem.get('name'),
                        visibility=op_elem.get('visibility', 'public'),
                        is_abstract=op_elem.get('isAbstract') == 'true'
                    )

                    # Process parameters
                    for param_elem in op_elem.findall('.//ownedParameter', {
                        'xmi': 'http://schema.omg.org/spec/XMI/2.1'
                    }):
                        type_elem = param_elem.find('type')
                        type_href = type_elem.get('href', '')
                        type_name = type_href.split('/')[-1]
                        op.parameters.append((param_elem.get('name'), type_name))

                    cls.add_operation(op)

                package.add_element(cls)
            model.add_package(package)

        # Process relationships
        for rel_elem in uml_model.findall('.//packagedElement[@xmi:type="uml:Generalization"]', {
            'xmi': 'http://schema.omg.org/spec/XMI/2.1'
        }):
            rel = Generalization(
                name=rel_elem.get('name'),
                source=UUID(rel_elem.find('source').get('xmi:idref')),
                target=UUID(rel_elem.find('target').get('xmi:idref')),
                relationship_type='generalization'
            )
            model.add_relationship(rel)

        for rel_elem in uml_model.findall('.//packagedElement[@xmi:type="uml:Association"]', {
            'xmi': 'http://schema.omg.org/spec/XMI/2.1'
        }):
            rel = Association(
                name=rel_elem.get('name'),
                source=UUID(rel_elem.find('source').get('xmi:idref')),
                target=UUID(rel_elem.find('target').get('xmi:idref')),
                relationship_type='association'
            )
            model.add_relationship(rel)

        for rel_elem in uml_model.findall('.//packagedElement[@xmi:type="uml:Dependency"]', {
            'xmi': 'http://schema.omg.org/spec/XMI/2.1'
        }):
            rel = Dependency(
                name=rel_elem.get('name'),
                source=UUID(rel_elem.find('source').get('xmi:idref')),
                target=UUID(rel_elem.find('target').get('xmi:idref')),
                relationship_type='dependency'
            )
            model.add_relationship(rel)

        return model
