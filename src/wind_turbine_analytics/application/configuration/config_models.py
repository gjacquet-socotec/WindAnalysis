from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class RunTestPipelineConfig:
    root_path: str
    template_path: str = "./assets/template_runtest.docx"
    output_path: str = "./output/runtest_output.docx"
    render_template: bool = True


@dataclass(frozen=True)
class ScadaRunnerConfig:
    root_path: str
    template_path: str = "./assets/template_scada.docx"
    output_path: str = "./output/scada_output.docx"
    render_template: bool = False


@dataclass(frozen=True)
class ScadaYamlSource:
    operation_path: str
    log_path: str
    operation_mapping: dict[str, str]
    log_mapping: dict[str, str]
    timestamp_key: str


@dataclass(frozen=True)
class GeneralInformation:
    name: str = ""
    description: str = ""
    park_name: str = ""
    client_name: str = ""
    client_location: str = ""
    client_contact: str = ""
    number_wtg: str = ""
    model_wtg: str = ""
    nominal_power: str = ""
    v_rated: str = ""
    constructor: str = ""
    author_name: str = ""
    author_email: str = ""
    author_phone: str = ""
    writer_name: str = ""
    writer_email: str = ""
    writer_phone: str = ""
    verficator_name: str = ""
    verficator_email: str = ""
    verficator_phone: str = ""
    date_archive: str = ""


@dataclass(frozen=True)
class LogCode:
    manual_stop: list[str] = field(default_factory=list)
    authorized_stop: list[str] = field(default_factory=list)
    unauthorized_stop: list[str] = field(default_factory=list)
    curtailment: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class Criterion:
    value: Optional[Any] = None
    unit: Optional[Any] = None
    specification: str = "=="
    description: bool = True


@dataclass(frozen=True)
class ValidationCriteria:
    validation_criterion: Optional[dict[str, Criterion]] = field(default_factory=dict)


@dataclass(frozen=True)
class TurbineGeneralInformation:
    model: Optional[str] = None
    nominal_power: Optional[float] = None
    constructor: Optional[str] = None
    path_operation_data: Optional[str] = None
    path_log_data: Optional[str] = None
    path_guaranteed_power_curve: Optional[str] = None
    timestamp: str = ""


@dataclass(frozen=True)
class TurbineMappingOperationData:
    timestamp: Optional[str] = None
    wind_speed: Optional[str] = None
    wind_direction: Optional[str] = None
    availability: Optional[str] = None
    activation_power: Optional[str] = None
    rpm: Optional[str] = None
    temperature: Optional[str] = None
    nacelle_position: Optional[str] = None
    power_reference: Optional[str] = None
    pitch_pale1: Optional[str] = None
    pitch_pale2: Optional[str] = None
    pitch_pale3: Optional[str] = None


@dataclass(frozen=True)
class TurbineLogMapping:
    start_date: Any  # str ou list[str] pour ["date", "time"]
    end_date: Any  # str ou list[str] pour ["date", "time"]
    name: Optional[str] = None
    oper: Optional[str] = None
    status: Optional[str] = None

    def get_start_date_columns(self) -> list[str]:
        """
        Retourne la liste des colonnes pour start_date.

        Returns:
            Liste de colonnes (ex: ["date", "time"] ou ["timestamp"])
        """
        if isinstance(self.start_date, list):
            return self.start_date
        return [self.start_date]

    def get_end_date_columns(self) -> list[str]:
        """
        Retourne la liste des colonnes pour end_date.

        Returns:
            Liste de colonnes (ex: ["date", "time"] ou ["timestamp"])
        """
        if isinstance(self.end_date, list):
            return self.end_date
        return [self.end_date]


@dataclass(frozen=True)
class TurbineConfig:
    turbine_id: str
    general_information: Optional[TurbineGeneralInformation] = None
    mapping_operation_data: Optional[TurbineMappingOperationData] = None
    mapping_log_data: Optional[TurbineLogMapping] = None
    test_start: Optional[str] = None
    test_end: Optional[str] = None


@dataclass(frozen=True)
class TurbineFarm:
    farm: Optional[dict[str, TurbineConfig]] = field(default_factory=dict)
