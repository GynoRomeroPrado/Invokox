import { useState, useEffect, useCallback, useRef } from 'react';
import { invoicesApi } from '../services/invoices';

interface TaskStatus {
  task_id: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  progress: number;
  result?: any;
  error?: string;
}

interface UseTaskPollingOptions {
  interval?: number; // milliseconds
  maxAttempts?: number;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
}

export function useTaskPolling(
  taskId: string | null,
  options: UseTaskPollingOptions = {}
) {
  const {
    interval = 2000, // Poll cada 2 segundos por defecto
    maxAttempts = 60, // Máximo 2 minutos (60 * 2seg = 120seg)
    onComplete,
    onError,
  } = options;

  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [attempts, setAttempts] = useState(0);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const attemptsRef = useRef(0);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }, []);

  const fetchTaskStatus = useCallback(async () => {
    if (!taskId) return;

    try {
      const status = await invoicesApi.getTaskStatus(taskId);
      setTaskStatus(status);
      attemptsRef.current += 1;
      setAttempts(attemptsRef.current);

      // Si completó o falló, detener polling
      if (status.status === 'COMPLETED') {
        stopPolling();
        onComplete?.(status.result);
      } else if (status.status === 'FAILED') {
        stopPolling();
        onError?.(status.error || 'Task failed');
      }

      // Si alcanzó máximo de intentos
      if (attemptsRef.current >= maxAttempts) {
        stopPolling();
        onError?.('Timeout: Task took too long to complete');
      }
    } catch (error: any) {
      console.error('Error polling task:', error);
      stopPolling();
      onError?.(error.message || 'Error polling task status');
    }
  }, [taskId, maxAttempts, stopPolling, onComplete, onError]);

  const startPolling = useCallback(() => {
    if (!taskId || isPolling) return;

    setIsPolling(true);
    attemptsRef.current = 0;
    setAttempts(0);

    // Fetch inmediatamente
    fetchTaskStatus();

    // Luego continuar polling
    intervalRef.current = setInterval(fetchTaskStatus, interval);
  }, [taskId, isPolling, interval, fetchTaskStatus]);

  // Cleanup en unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  // Auto-start si hay taskId
  useEffect(() => {
    if (taskId && !isPolling) {
      startPolling();
    }
  }, [taskId]); // Solo cuando cambia taskId

  return {
    taskStatus,
    isPolling,
    attempts,
    startPolling,
    stopPolling,
  };
}

// Hook simplificado para un solo uso
export function useSingleTaskPoll(
  taskId: string | null,
  options?: UseTaskPollingOptions
) {
  return useTaskPolling(taskId, options);
}
