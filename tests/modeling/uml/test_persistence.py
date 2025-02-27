"""
Tests for the UML model persistence layer
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from src.modeling.uml.core import Model, Package, Class, Attribute, Operation
from src.modeling.uml.persistence import ModelRepository

@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary repository"""
    return ModelRepository(tmp_path)

@pytest.fixture
def sample_model():
    """Create a sample UML model for testing"""
    model = Model("TestModel")
    
    # Create a package
    package = Package("com.example")
    model.add_package(package)
    
    # Create a class
    cls = Class(
        name="User",
        is_abstract=False,
        is_interface=False
    )
    
    # Add attributes
    cls.add_attribute(Attribute(
        name="id",
        type="UUID",
        visibility="private"
    ))
    cls.add_attribute(Attribute(
        name="username",
        type="str",
        visibility="private"
    ))
    
    # Add operations
    cls.add_operation(Operation(
        name="get_full_name",
        return_type="str",
        parameters=[],
        visibility="public"
    ))
    
    package.add_element(cls)
    return model

def test_save_and_load_model(temp_repo, sample_model):
    """Test saving and loading a model"""
    # Save model
    model_id = temp_repo.save_model(sample_model)
    assert model_id is not None
    
    # Load model
    loaded_model = temp_repo.load_model(model_id)
    assert loaded_model.name == sample_model.name
    assert len(loaded_model.packages) == len(sample_model.packages)
    
    # Check package
    loaded_pkg = loaded_model.packages[0]
    original_pkg = sample_model.packages[0]
    assert loaded_pkg.name == original_pkg.name
    
    # Check class
    loaded_cls = loaded_pkg.elements[0]
    original_cls = original_pkg.elements[0]
    assert loaded_cls.name == original_cls.name
    assert loaded_cls.is_abstract == original_cls.is_abstract
    assert loaded_cls.is_interface == original_cls.is_interface

def test_versioning(temp_repo, sample_model):
    """Test model versioning"""
    # Save initial version
    model_id = temp_repo.save_model(sample_model)
    version_id = temp_repo.create_version(sample_model)
    
    # Modify model
    sample_model.name = "UpdatedModel"
    new_version_id = temp_repo.create_version(sample_model)
    
    # List versions
    versions = temp_repo.list_versions(model_id)
    assert len(versions) == 2
    
    # Load old version
    old_model = temp_repo.load_version(model_id, version_id)
    assert old_model.name == "TestModel"
    
    # Load new version
    new_model = temp_repo.load_version(model_id, new_version_id)
    assert new_model.name == "UpdatedModel"

def test_backups(temp_repo, sample_model):
    """Test backup functionality"""
    # Save model and create backup
    model_id = temp_repo.save_model(sample_model)
    backup_name = temp_repo.create_backup(sample_model)
    
    # List backups
    backups = temp_repo.list_backups(model_id)
    assert len(backups) == 1
    assert backups[0]["backup_name"] == backup_name
    
    # Restore from backup
    restored_model = temp_repo.restore_backup(backup_name)
    assert restored_model.name == sample_model.name

def test_cleanup_old_backups(temp_repo, sample_model, monkeypatch):
    """Test cleanup of old backups"""
    model_id = temp_repo.save_model(sample_model)
    
    # Create old backup
    old_time = datetime.now() - timedelta(days=31)
    backup_path = temp_repo._get_backup_path(model_id, old_time)
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text("{}")
    os.utime(backup_path, (old_time.timestamp(), old_time.timestamp()))
    
    # Create recent backup
    temp_repo.create_backup(sample_model)
    
    # Clean up old backups
    removed = temp_repo.cleanup_old_backups(model_id, keep_days=30)
    assert removed == 1
    
    # Check remaining backups
    backups = temp_repo.list_backups(model_id)
    assert len(backups) == 1

def test_multiple_formats(temp_repo, sample_model):
    """Test saving and loading in different formats"""
    model_id = temp_repo.save_model(sample_model)
    
    # Test JSON format
    json_model = temp_repo.load_model(model_id, format="json")
    assert json_model.name == sample_model.name
    
    # Test YAML format
    temp_repo.save_model(sample_model, format="yaml")
    yaml_model = temp_repo.load_model(model_id, format="yaml")
    assert yaml_model.name == sample_model.name
    
    # Test XMI format
    temp_repo.save_model(sample_model, format="xmi")
    xmi_model = temp_repo.load_model(model_id, format="xmi")
    assert xmi_model.name == sample_model.name

def test_error_handling(temp_repo):
    """Test error handling"""
    # Test loading non-existent model
    with pytest.raises(FileNotFoundError):
        temp_repo.load_model("non_existent")
    
    # Test loading non-existent version
    with pytest.raises(FileNotFoundError):
        temp_repo.load_version("model_id", "version_id")
    
    # Test loading non-existent backup
    with pytest.raises(FileNotFoundError):
        temp_repo.restore_backup("non_existent_backup.json")
    
    # Test invalid format
    with pytest.raises(ValueError):
        temp_repo.save_model(Model("test"), format="invalid")
