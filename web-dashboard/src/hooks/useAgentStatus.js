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

export const useAgentStatus = (jobId, isActive = false) => {
  const { data, error, mutate } = useSWR(
    jobId && isActive ? `/api/v1/agent-job/${jobId}` : null,
    fetcher,
    {
      refreshInterval: isActive ? 2000 : 0, // Poll every 2 seconds when active
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      dedupingInterval: 1000,
    }
  );

  return {
    jobData: data?.job || null,
    activities: data?.activities || [],
    isLoading: !error && !data && isActive,
    isError: error,
    mutate,
  };
};

export default useAgentStatus;
