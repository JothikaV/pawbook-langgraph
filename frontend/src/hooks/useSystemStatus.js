import { useState, useEffect } from 'react';
import { getStatus } from '../utils/api';

export function useSystemStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const data = await getStatus();
        setStatus(data);
      } catch (error) {
        console.error('Failed to get status:', error);
      } finally {
        setLoading(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return { status, loading };
}
