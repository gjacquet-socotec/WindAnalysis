from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AnalysisResult:
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    requires_visuals: bool = True
    detailed_results: Optional[Dict[str, Any]] = None
