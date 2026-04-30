import { useEffect, useRef } from "react";
import type { ChartData } from "../types/analysis";

// @ts-ignore - Plotly types
import Plotly from "plotly.js-dist-min";

interface ChartViewerProps {
  charts: ChartData[];
}

export const ChartViewer = ({ charts }: ChartViewerProps) => {
  console.log("📊 ChartViewer rendering with", charts.length, "charts");

  if (charts.length === 0) {
    console.log("⚠️ No charts to display");
    return null;
  }

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4 text-primary-dark">Visualisations</h2>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {charts.map((chart, idx) => (
          <ChartContainer key={idx} chart={chart} />
        ))}
      </div>
    </div>
  );
};

interface ChartContainerProps {
  chart: ChartData;
}

const ChartContainer = ({ chart }: ChartContainerProps) => {
  const plotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (plotRef.current && chart.plotly_json) {
      try {
        Plotly.newPlot(
          plotRef.current,
          chart.plotly_json.data || [],
          {
            ...chart.plotly_json.layout,
            autosize: true,
            responsive: true,
          },
          {
            responsive: true,
            displayModeBar: true,
          }
        );

        console.log("✅ Chart rendered:", chart.name);
      } catch (error) {
        console.error("❌ Failed to render chart:", chart.name, error);
      }
    }

    // Cleanup
    return () => {
      if (plotRef.current) {
        Plotly.purge(plotRef.current);
      }
    };
  }, [chart]);

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold mb-2 text-gray-700">{chart.name}</h3>
      <div ref={plotRef} style={{ width: "100%", height: "500px" }} />
    </div>
  );
};
