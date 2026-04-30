"""
Pydantic request models for API endpoints.
"""
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, field_validator


class AnalyzeRequest(BaseModel):
    """
    Request model for triggering RunTest or SCADA analysis.

    Attributes:
        folder_path: Path to folder containing config.yml
        workflow_type: Type of analysis ("runtest" or "scada")
        template_path: Optional custom template path for Word report
        output_path: Optional custom output path for Word report
        render_template: Whether to generate Word report (default: True)
    """
    folder_path: str
    workflow_type: Literal["runtest", "scada"]
    template_path: Optional[str] = None
    output_path: Optional[str] = None
    render_template: bool = True

    @field_validator("folder_path")
    @classmethod
    def validate_folder_path(cls, v: str) -> str:
        """Validate that folder_path exists."""
        folder = Path(v)
        if not folder.exists():
            raise ValueError(f"Le dossier {v} n'existe pas.")
        if not folder.is_dir():
            raise ValueError(f"{v} n'est pas un dossier.")
        return v

    @field_validator("template_path")
    @classmethod
    def validate_template_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate template path if provided."""
        if v is not None:
            template = Path(v)
            if not template.exists():
                raise ValueError(f"Le template {v} n'existe pas.")
            if not template.suffix == ".docx":
                raise ValueError(f"Le template doit être un fichier .docx")
        return v
