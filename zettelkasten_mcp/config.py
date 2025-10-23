"""Configuration management for Zettelkasten MCP Server."""

import os
from pathlib import Path
from typing import Optional
import yaml


class Config:
    """Manages configuration loading and validation."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.

        Args:
            config_path: Path to config.yaml file. If None, looks for config.yaml in current directory.
        """
        self.config_path = Path(config_path) if config_path else Path("config.yaml")
        self.data = {}
        self.template_file = Path("template.md")
        self.output_directory = Path.home() / "zettelkasten" / "cards"
        self.naming_conventions_file: Optional[Path] = None
        self.create_backup = True
        self.filename_sanitization = True

        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            print(f"Warning: Config file not found at {self.config_path}. Using defaults.")
            return

        try:
            with open(self.config_path, 'r') as f:
                self.data = yaml.safe_load(f) or {}

            # Parse configuration values
            if 'template_file' in self.data:
                self.template_file = Path(self.data['template_file']).expanduser()

            if 'output_directory' in self.data:
                self.output_directory = Path(self.data['output_directory']).expanduser()

            if 'naming_conventions_file' in self.data:
                self.naming_conventions_file = Path(self.data['naming_conventions_file']).expanduser()

            # File operation settings
            if 'file_operations' in self.data:
                ops = self.data['file_operations']
                self.create_backup = ops.get('create_backup', True)
                self.filename_sanitization = ops.get('filename_sanitization', True)

            # Validate directories exist
            self._validate_directories()

        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")

    def _validate_directories(self) -> None:
        """Validate that configured directories exist or can be created."""
        # Create output directory if it doesn't exist
        if not self.output_directory.exists():
            self.output_directory.mkdir(parents=True, exist_ok=True)

    def load_naming_conventions(self) -> Optional[str]:
        """Load naming conventions from file if configured.

        Returns:
            Content of naming conventions file, or None if not configured.
        """
        if self.naming_conventions_file and self.naming_conventions_file.exists():
            try:
                with open(self.naming_conventions_file, 'r') as f:
                    return f.read()
            except Exception as e:
                print(f"Error loading naming conventions: {e}")
        return None

    def load_template(self) -> Optional[str]:
        """Load the template file.

        Returns:
            Template content, or None if not found.
        """
        if self.template_file.exists():
            try:
                with open(self.template_file, 'r') as f:
                    return f.read()
            except Exception as e:
                print(f"Error loading template: {e}")
        return None
