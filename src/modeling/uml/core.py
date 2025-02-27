"""
Core UML modeling components
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Union
from uuid import UUID, uuid4

@dataclass
class UMLElement:
    """Base class for all UML elements"""
    name: str
    id: UUID = field(default_factory=uuid4)
    stereotypes: Set[str] = field(default_factory=set)
    properties: Dict[str, str] = field(default_factory=dict)

    def add_stereotype(self, stereotype: str) -> None:
        """Add a stereotype to the element"""
        self.stereotypes.add(stereotype)

    def add_property(self, key: str, value: str) -> None:
        """Add a property to the element"""
        self.properties[key] = value

@dataclass
class Relationship:
    """Base class for UML relationships"""
    name: str
    source: UUID
    target: UUID
    relationship_type: str
    id: UUID = field(default_factory=uuid4)
    stereotypes: Set[str] = field(default_factory=set)
    properties: Dict[str, str] = field(default_factory=dict)

@dataclass
class Association(Relationship):
    """Association relationship"""
    multiplicity_source: str = "1"
    multiplicity_target: str = "1"
    navigability_source: bool = True
    navigability_target: bool = True

@dataclass
class Generalization(Relationship):
    """Generalization (inheritance) relationship"""
    def __post_init__(self):
        self.relationship_type = "generalization"

@dataclass
class Dependency(Relationship):
    """Dependency relationship"""
    def __post_init__(self):
        self.relationship_type = "dependency"

@dataclass
class Attribute:
    """Class attribute"""
    name: str
    type: str
    visibility: str = "public"
    default_value: Optional[str] = None
    is_static: bool = False
    is_final: bool = False

@dataclass
class Operation:
    """Class operation/method"""
    name: str
    return_type: Optional[str]
    parameters: List[tuple] = field(default_factory=list)
    visibility: str = "public"
    is_static: bool = False
    is_abstract: bool = False

@dataclass
class Class(UMLElement):
    """UML Class"""
    attributes: List[Attribute] = field(default_factory=list)
    operations: List[Operation] = field(default_factory=list)
    is_abstract: bool = False
    is_interface: bool = False

    def add_attribute(self, attribute: Attribute) -> None:
        """Add an attribute to the class"""
        self.attributes.append(attribute)

    def add_operation(self, operation: Operation) -> None:
        """Add an operation to the class"""
        self.operations.append(operation)

@dataclass
class Package(UMLElement):
    """UML Package"""
    elements: List[UMLElement] = field(default_factory=list)

    def add_element(self, element: UMLElement) -> None:
        """Add an element to the package"""
        self.elements.append(element)

@dataclass
class Model:
    """UML Model"""
    name: str
    packages: List[Package] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)

    def add_package(self, package: Package) -> None:
        """Add a package to the model"""
        self.packages.append(package)

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the model"""
        self.relationships.append(relationship)

    def find_element_by_id(self, element_id: UUID) -> Optional[UMLElement]:
        """Find an element by its ID"""
        for package in self.packages:
            if package.id == element_id:
                return package
            for element in package.elements:
                if element.id == element_id:
                    return element
        return None

    def validate(self) -> List[str]:
        """Validate the model"""
        errors = []
        
        # Check for duplicate names in the same package
        for package in self.packages:
            names = set()
            for element in package.elements:
                if element.name in names:
                    errors.append(f"Duplicate name '{element.name}' in package '{package.name}'")
                names.add(element.name)

        # Validate relationships
        for rel in self.relationships:
            source = self.find_element_by_id(rel.source)
            target = self.find_element_by_id(rel.target)
            
            if not source:
                errors.append(f"Relationship '{rel.name}' has invalid source ID")
            if not target:
                errors.append(f"Relationship '{rel.name}' has invalid target ID")

        return errors
