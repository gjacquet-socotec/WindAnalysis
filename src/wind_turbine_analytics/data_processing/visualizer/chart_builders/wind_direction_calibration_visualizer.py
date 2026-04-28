class WindDirectionCalibrationVisualizer(BaseVisualizer):
    """Visualizes wind direction calibration results."""

    def __init__(self):
        super().__init__(chart_name="wind_direction_calibration", use_plotly=True)

    def _create_figure(self, result: AnalysisResult) -> go.Figure:
        pass