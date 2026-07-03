import { useEffect, useRef, useState, useCallback } from "react";
import { wsUrl } from "../api/client";

export interface AgentEvent {
  type: string;
  [key: string]: any;
}

export function useAgentSocket(onEvent?: (e: AgentEvent) => void) {
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    let cancelled = false;
    let retryTimer: ReturnType<typeof setTimeout>;

    function connect() {
      if (cancelled) return;
      const ws = new WebSocket(wsUrl());
      wsRef.current = ws;
      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        retryTimer = setTimeout(connect, 2000);
      };
      ws.onerror = () => ws.close();
      ws.onmessage = (msg) => {
        try {
          const parsed = JSON.parse(msg.data);
          setEvents((prev) => [...prev.slice(-99), parsed]);
          onEventRef.current?.(parsed);
        } catch {
          // ignore malformed frames
        }
      };
    }
    connect();
    return () => {
      cancelled = true;
      clearTimeout(retryTimer);
      wsRef.current?.close();
    };
  }, []);

  const clear = useCallback(() => setEvents([]), []);

  return { connected, events, clear };
}
