"""
Pydantic response models for API endpoints.
"""
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel


class ChartData(BaseModel):
    """
    Representation of a Plotly chart.

    Attributes:
        name: Identifier of the chart (e.g., "power_curve_chart")
        plotly_json: Plotly JSON representation (dict with 'data' and 'layout' keys)
    """
    name: str
    plotly_json: Dict[str, Any]


class TableData(BaseModel):
    """
    Representation of a data table.

    Attributes:
        name: Identifier of the table (e.g., "summary_table")
        columns: List of column names
        rows: List of rows, each row is a dict mapping column name to value
    """
    name: str
    columns: List[str]
    rows: List[Dict[str, Any]]


class AnalyzeResponse(BaseModel):
    """
    Complete response for analysis endpoints.

    Attributes:
        status: Status of the analysis ("success" or "error")
        message: Human-readable description of the result
        charts: List of all generated charts
        tables: List of all generated tables
        report_path: Path to generated Word report (if render_template=True)
        metadata: Additional information (park name, turbines, dates, criteria)
    """
    status: Literal["success", "error"]
    message: str
    charts: List[ChartData]
    tables: List[TableData]
    report_path: Optional[str] = None
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    """
    Health check response.

    Attributes:
        status: Status of the API ("healthy" or "unhealthy")
        version: API version
    """
    status: str
    version: str
