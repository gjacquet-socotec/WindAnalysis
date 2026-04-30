import { useState } from 'react';
import { analyzeAPI } from '../services/api';
import type { ParsedConfig } from '../types/config';

interface UseConfigParserReturn {
  loadConfig: (folderPath: string) => Promise<ParsedConfig | null>;
  isLoading: boolean;
  error: string | null;
}

/**
 * Hook for loading and parsing config.yml files
 */
export function useConfigParser(): UseConfigParserReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadConfig = async (folderPath: string): Promise<ParsedConfig | null> => {
    setIsLoading(true);
    setError(null);

    try {
      console.log('📂 Loading config from:', folderPath);
      const configData = await analyzeAPI.readConfig(folderPath);
      console.log('✅ Config loaded successfully:', configData);

      // Backend returns the config.yml structure directly
      return configData as ParsedConfig;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load configuration';
      console.error('❌ Config loading error:', errorMessage);
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return { loadConfig, isLoading, error };
}
