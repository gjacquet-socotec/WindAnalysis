import axios from "axios";
import type { AnalyzeRequest, AnalyzeResponse } from "../types/analysis";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,  // 5 minutes (synchrone avec timeout étendu)
  headers: {
    "Content-Type": "application/json",
  },
});

export const analyzeAPI = {
  /**
   * Déclenche une analyse RunTest ou SCADA
   */
  runAnalysis: async (request: AnalyzeRequest): Promise<AnalyzeResponse> => {
    const endpoint = request.workflow_type === "runtest" ? "/analyze/runtest" : "/analyze/scada";
    const response = await apiClient.post<AnalyzeResponse>(endpoint, request);
    return response.data;
  },

  /**
   * Vérifie l'état de santé de l'API
   */
  healthCheck: async (): Promise<{ status: string; version: string }> => {
    const response = await apiClient.get("/health");
    return response.data;
  },
};
