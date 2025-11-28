import useSWR from 'swr';
import { apiService } from '../lib/api';

const fetcher = async (url) => {
  try {
    const response = await apiService.request(url);
    return response;
  } catch (error) {
    throw error;
  }
};

export const useTests = () => {
  const { data, error, mutate } = useSWR('/api/v1/tests', fetcher, {
    refreshInterval: 30000, // Refresh every 30 seconds
    revalidateOnFocus: true,
    revalidateOnReconnect: true,
  });

  return {
    tests: data?.data || [], // The API returns data in data field, not tests field
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
};

export const useSystemInfo = () => {
  const { data, error } = useSWR('/api/v1/system/info', fetcher, {
    refreshInterval: 60000, // Refresh every minute
  });

  return {
    systemInfo: data || null,
    isLoading: !error && !data,
    isError: error,
  };
};

export const useDashboardStats = () => {
  const { data, error } = useSWR('/api/v1/dashboard/stats', fetcher, {
    refreshInterval: 10000, // Refresh every 10 seconds
  });

  return {
    stats: data || null,
    isLoading: !error && !data,
    isError: error,
  };
};

export default useTests;
