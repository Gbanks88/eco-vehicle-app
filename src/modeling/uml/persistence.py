"""
Model persistence layer for UML models.
Provides storage, retrieval, versioning, and backup capabilities.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

import yaml
from .core import Model
from .serialization import ModelSerializer, ModelDeserializer

class ModelRepository:
    """Handles model storage, retrieval, and versioning"""

    def __init__(self, base_path: Union[str, Path]):
        """Initialize repository with base storage path"""
        self.base_path = Path(base_path)
        self.models_path = self.base_path / "models"
        self.backups_path = self.base_path / "backups"
        self.versions_path = self.base_path / "versions"
        self._ensure_directories()

        self.serializer = ModelSerializer()
        self.deserializer = ModelDeserializer()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        for path in [self.models_path, self.backups_path, self.versions_path]:
            path.mkdir(parents=True, exist_ok=True)

    def _get_model_path(self, model_id: str, format: str = "json") -> Path:
        """Get path for model file"""
        return self.models_path / f"{model_id}.{format}"

    def _get_version_path(self, model_id: str, version_id: str) -> Path:
        """Get path for versioned model file"""
        return self.versions_path / model_id / f"{version_id}.json"

    def _get_backup_path(self, model_id: str, timestamp: datetime) -> Path:
        """Get path for backup file"""
        backup_name = f"{model_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        return self.backups_path / backup_name

    def save_model(self, model: Model, format: str = "json", create_backup: bool = True) -> str:
        """Save model to storage in specified format"""
        if not isinstance(model, Model):
            raise ValueError("Expected Model instance")

        # Generate model ID if not present
        model_id = str(getattr(model, 'id', uuid4()))
        
        # Create backup if requested
        if create_backup:
            self.create_backup(model)

        # Save model in specified format
        model_path = self._get_model_path(model_id, format)
        if format == "json":
            content = self.serializer.to_json(model)
        elif format == "yaml":
            content = self.serializer.to_yaml(model)
        elif format == "xmi":
            content = self.serializer.to_xmi(model)
        else:
            raise ValueError(f"Unsupported format: {format}")

        model_path.write_text(content)
        return model_id

    def load_model(self, model_id: str, format: str = "json") -> Model:
        """Load model from storage"""
        model_path = self._get_model_path(model_id, format)
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_id}")

        content = model_path.read_text()
        if format == "json":
            return self.deserializer.from_json(content)
        elif format == "yaml":
            return self.deserializer.from_yaml(content)
        elif format == "xmi":
            return self.deserializer.from_xmi(content)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def create_version(self, model: Model, version_id: Optional[str] = None) -> str:
        """Create a new version of the model"""
        model_id = str(getattr(model, 'id', uuid4()))
        version_id = version_id or str(uuid4())
        
        # Create version directory if needed
        version_dir = self.versions_path / model_id
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Save version
        version_path = self._get_version_path(model_id, version_id)
        content = self.serializer.to_json(model)
        version_path.write_text(content)
        
        return version_id

    def load_version(self, model_id: str, version_id: str) -> Model:
        """Load a specific version of a model"""
        version_path = self._get_version_path(model_id, version_id)
        if not version_path.exists():
            raise FileNotFoundError(f"Version not found: {model_id}/{version_id}")
        
        content = version_path.read_text()
        return self.deserializer.from_json(content)

    def list_versions(self, model_id: str) -> List[Dict[str, str]]:
        """List all versions of a model"""
        version_dir = self.versions_path / model_id
        if not version_dir.exists():
            return []
        
        versions = []
        for version_file in version_dir.glob("*.json"):
            version_id = version_file.stem
            timestamp = datetime.fromtimestamp(version_file.stat().st_mtime)
            versions.append({
                "version_id": version_id,
                "created_at": timestamp.isoformat(),
                "file_size": version_file.stat().st_size
            })
        
        return sorted(versions, key=lambda v: v["created_at"], reverse=True)

    def create_backup(self, model: Model) -> str:
        """Create a backup of the model"""
        timestamp = datetime.now()
        backup_path = self._get_backup_path(str(getattr(model, 'id', uuid4())), timestamp)
        
        content = self.serializer.to_json(model)
        backup_path.write_text(content)
        
        return backup_path.name

    def list_backups(self, model_id: str) -> List[Dict[str, str]]:
        """List all backups for a model"""
        backups = []
        for backup_file in self.backups_path.glob(f"{model_id}_*.json"):
            timestamp = datetime.fromtimestamp(backup_file.stat().st_mtime)
            backups.append({
                "backup_name": backup_file.name,
                "created_at": timestamp.isoformat(),
                "file_size": backup_file.stat().st_size
            })
        
        return sorted(backups, key=lambda b: b["created_at"], reverse=True)

    def restore_backup(self, backup_name: str) -> Model:
        """Restore model from a backup"""
        backup_path = self.backups_path / backup_name
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_name}")
        
        content = backup_path.read_text()
        return self.deserializer.from_json(content)

    def delete_model(self, model_id: str, delete_versions: bool = False, delete_backups: bool = False) -> None:
        """Delete a model and optionally its versions and backups"""
        # Delete main model files
        for format in ["json", "yaml", "xmi"]:
            model_path = self._get_model_path(model_id, format)
            if model_path.exists():
                model_path.unlink()

        # Delete versions if requested
        if delete_versions:
            version_dir = self.versions_path / model_id
            if version_dir.exists():
                shutil.rmtree(version_dir)

        # Delete backups if requested
        if delete_backups:
            for backup_file in self.backups_path.glob(f"{model_id}_*.json"):
                backup_file.unlink()

    def cleanup_old_backups(self, model_id: str, keep_days: int = 30) -> int:
        """Remove backups older than specified days"""
        cutoff = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        count = 0
        
        for backup_file in self.backups_path.glob(f"{model_id}_*.json"):
            if backup_file.stat().st_mtime < cutoff:
                backup_file.unlink()
                count += 1
        
        return count
