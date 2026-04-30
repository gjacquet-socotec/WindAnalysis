export type WorkflowType = "runtest" | "scada";

export interface AnalyzeRequest {
  folder_path: string;
  workflow_type: WorkflowType;
  template_path?: string;
  output_path?: string;
  render_template?: boolean;
}

export interface ChartData {
  name: string;
  plotly_json: any;  // Format Plotly JSON
}

export interface TableData {
  name: string;
  columns: string[];
  rows: Record<string, any>[];
}

export interface AnalyzeResponse {
  status: "success" | "error";
  message: string;
  charts: ChartData[];
  tables: TableData[];
  report_path?: string;
  metadata: {
    park_name?: string;
    turbines?: string[];
    test_start?: string;
    test_end?: string;
    criteria?: Record<string, { value: any; unit: string }>;
  };
}
