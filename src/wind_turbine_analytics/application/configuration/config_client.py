from src.wind_turbine_analytics.application.utils.yaml_tools import (
    build_client_config_from_scada_yaml,
)
from typing import Dict, Any
from src.wind_turbine_analytics.application.configuration.config_models import (
    GeneralInformation,
    Criterion,
    ValidationCriteria,
    TurbineGeneralInformation,
    TurbineMappingOperationData,
    TurbineLogMapping,
    TurbineConfig,
    TurbineFarm,
    ScadaRunnerConfig,
    RunTestPipelineConfig,
)
from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from src.wind_turbine_analytics.application.workflows.base_workflow import (
        BaseWorkflow,
    )


class ConfigClient:
    def __init__(self, config: Union[ScadaRunnerConfig, RunTestPipelineConfig]) -> None:
        self._config = config
        root = Path(self._config.root_path)
        try:
            self.client_config = build_client_config_from_scada_yaml(root)
        except Exception:
            raise RuntimeError(
                f"Failed to load client configuration from {root}. "
                "Ensure config.yml is present and correctly formatted."
            )

    def validate(self, workfkow: "BaseWorkflow") -> None:
        workfkow.general_information = self.get_general_client_information()
        workfkow.validation_criteria = self.get_validation_criteria()
        workfkow.turbine_sources = self.get_turbine_sources()

    # [DONE] get general information of the SCADA
    def get_general_client_information(self) -> GeneralInformation:
        general_information: Dict[str, Any] = self.client_config.get(
            "general_information", {}
        )
        return GeneralInformation(**general_information)

    # [DONE] get the validation criteria
    def get_validation_criteria(self) -> ValidationCriteria:
        criteria_config: Dict[str, Any] = self.client_config.get(
            "validation_criteria", {}
        )
        criteria_dict: dict[str, Criterion] = {}
        for name, criterion in criteria_config.items():
            criteria_dict[name] = Criterion(**criterion)

        return ValidationCriteria(validation_criterion=criteria_dict)

    # [DONE] get relevant information per turbine
    def get_turbine_sources(self) -> TurbineFarm:
        turbines = self.client_config.get("dynamic_fields", {}).get("turbines", {})
        turbine_dict: dict[str, TurbineConfig] = {}
        for turbine_info in turbines:
            turbine_id = turbine_info.get("turbine_id", {})
            turbine = TurbineConfig(
                turbine_id=turbine_id,
                general_information=TurbineGeneralInformation(
                    **turbine_info.get("general_information", {})
                ),
                mapping_operation_data=TurbineMappingOperationData(
                    **turbine_info.get("mapping_operation_data", {})
                ),
                mapping_log_data=TurbineLogMapping(
                    **turbine_info.get("mapping_log_data", {})
                ),
                test_start=turbine_info.get("test_start", None),
                test_end=turbine_info.get("test_end", None),
            )
            turbine_dict[turbine_id] = turbine
        return TurbineFarm(farm=turbine_dict)
