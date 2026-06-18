/**
 * useWebSocket Hook (Sprint 2)
 *
 * Manages WebSocket connection lifecycle with JWT authentication,
 * automatic reconnection, heartbeat, and message routing.
 *
 * Based on docs/design/websocket-message-protocol.md
 */

import { useCallback, useEffect, useRef, useState } from "react";
import type {
  ConnectionState,
  MessageHandler,
  MessageType,
  WebSocketConfig,
  WebSocketError,
  WSMessage,
} from "../types/websocket.types";

interface UseWebSocketReturn {
  state: ConnectionState;
  error: WebSocketError | null;
  send: <T = Record<string, unknown>>(message: WSMessage<T>) => void;
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
  on: <T = Record<string, unknown>>(
    type: MessageType,
    handler: MessageHandler<T>,
  ) => () => void;
  connect: () => void;
  disconnect: () => void;
}

export function useWebSocket(config: WebSocketConfig): UseWebSocketReturn {
  const [state, setState] = useState<ConnectionState>("disconnected");
  const [error, setError] = useState<WebSocketError | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const heartbeatIntervalRef = useRef<number | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const handlersRef = useRef<Map<MessageType, Set<MessageHandler>>>(new Map());
  const connectRef = useRef<() => void>(() => {});

  const {
    url,
    token,
    heartbeatInterval = 30000,
    reconnectDelays = [1000, 2000, 4000],
    maxReconnectAttempts = 3,
  } = config;

  /**
   * Register message handler for specific message type
   */
  const on = useCallback(
    <T = Record<string, unknown>>(
      type: MessageType,
      handler: MessageHandler<T>,
    ): (() => void) => {
      if (!handlersRef.current.has(type)) {
        handlersRef.current.set(type, new Set());
      }
      handlersRef.current.get(type)!.add(handler as MessageHandler);

      // Return cleanup function
      return () => {
        const handlers = handlersRef.current.get(type);
        if (handlers) {
          handlers.delete(handler as MessageHandler);
        }
      };
    },
    [],
  );

  /**
   * Send message to WebSocket
   */
  const send = useCallback(
    <T = Record<string, unknown>>(message: WSMessage<T>) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(message));
      } else {
        console.warn(
          "WebSocket not connected, message not sent:",
          message.type,
        );
      }
    },
    [],
  );

  /**
   * Subscribe to a channel
   */
  const subscribe = useCallback(
    (channel: string) => {
      send({
        type: "subscribe",
        data: { channel },
        timestamp: new Date().toISOString(),
        id: crypto.randomUUID(),
      });
    },
    [send],
  );

  /**
   * Unsubscribe from a channel
   */
  const unsubscribe = useCallback(
    (channel: string) => {
      send({
        type: "unsubscribe",
        data: { channel },
        timestamp: new Date().toISOString(),
        id: crypto.randomUUID(),
      });
    },
    [send],
  );

  /**
   * Send ping heartbeat
   */
  const sendPing = useCallback(() => {
    send({
      type: "ping",
      data: {},
      timestamp: new Date().toISOString(),
      id: crypto.randomUUID(),
    });
  }, [send]);

  /**
   * Start heartbeat interval
   */
  const startHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current !== null) {
      clearInterval(heartbeatIntervalRef.current);
    }
    heartbeatIntervalRef.current = window.setInterval(
      sendPing,
      heartbeatInterval,
    );
  }, [sendPing, heartbeatInterval]);

  /**
   * Stop heartbeat interval
   */
  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current !== null) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  /**
   * Handle incoming WebSocket message
   */
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const message = JSON.parse(event.data) as WSMessage;

        // Dispatch to registered handlers
        const handlers = handlersRef.current.get(message.type);
        if (handlers) {
          handlers.forEach((handler) => handler(message));
        }

        // Handle system messages
        if (message.type === "welcome") {
          setState("connected");
          setError(null);
          reconnectAttemptsRef.current = 0;
          startHeartbeat();
        } else if (message.type === "system.error") {
          const errorData = message.data as {
            code: string;
            message: string;
            recoverable: boolean;
          };
          setError({
            code: errorData.code as WebSocketError["code"],
            message: errorData.message,
            recoverable: errorData.recoverable,
          });
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    },
    [startHeartbeat],
  );

  /**
   * Handle WebSocket errors
   */
  const handleError = useCallback((event: Event) => {
    console.error("WebSocket error:", event);
    setError({
      code: "CONNECTION_TIMEOUT",
      message: "WebSocket connection error",
      recoverable: true,
    });
  }, []);

  /**
   * Handle WebSocket close with reconnection logic
   */
  const handleClose = useCallback(
    (event: CloseEvent) => {
      stopHeartbeat();
      wsRef.current = null;

      // Map close codes to error types
      let errorCode: WebSocketError["code"] = "UNKNOWN_ERROR";
      let recoverable = true;

      if (event.code === 4401) {
        errorCode = "AUTH_FAILED";
        recoverable = false;
      } else if (event.code === 4403) {
        errorCode = "FORBIDDEN";
        recoverable = false;
      } else if (event.code === 4404) {
        errorCode = "PROTOCOL_VERSION_MISMATCH";
        recoverable = false;
      } else if (event.code === 4409) {
        errorCode = "CONFLICT";
        recoverable = true;
      } else if (event.code === 4429) {
        errorCode = "RATE_LIMITED";
        recoverable = true;
      } else if (event.code === 1000) {
        // Normal closure
        setState("disconnected");
        return;
      }

      setError({
        code: errorCode,
        message: event.reason || "Connection closed",
        recoverable,
      });

      // Attempt reconnection for recoverable errors
      if (recoverable && reconnectAttemptsRef.current < maxReconnectAttempts) {
        const delay =
          reconnectDelays[reconnectAttemptsRef.current] ||
          reconnectDelays[reconnectDelays.length - 1];
        setState("reconnecting");
        reconnectTimeoutRef.current = window.setTimeout(() => {
          reconnectAttemptsRef.current++;
          connectRef.current();
        }, delay);
      } else {
        setState("disconnected");
      }
    },
    [reconnectDelays, maxReconnectAttempts, stopHeartbeat],
  );

  /**
   * Connect to WebSocket with JWT authentication
   */
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setState("connecting");
    setError(null);

    try {
      // WebSocket with Sec-WebSocket-Protocol JWT authentication (Q2-b decision)
      const ws = new WebSocket(url, [`bearer.${token}`]);

      ws.onopen = () => {
        // Welcome message will trigger 'connected' state
      };

      ws.onmessage = handleMessage;
      ws.onerror = handleError;
      ws.onclose = handleClose;

      wsRef.current = ws;
    } catch (err) {
      console.error("Failed to create WebSocket:", err);
      setState("error");
      setError({
        code: "UNKNOWN_ERROR",
        message: err instanceof Error ? err.message : "Failed to connect",
        recoverable: true,
      });
    }
  }, [url, token, handleMessage, handleError, handleClose]);

  connectRef.current = connect;

  /**
   * Disconnect WebSocket
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current !== null) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    stopHeartbeat();

    if (wsRef.current) {
      wsRef.current.close(1000, "Client disconnect");
      wsRef.current = null;
    }

    setState("disconnected");
    setError(null);
    reconnectAttemptsRef.current = 0;
  }, [stopHeartbeat]);

  /**
   * Auto-connect on mount, disconnect on unmount
   */
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    state,
    error,
    send,
    subscribe,
    unsubscribe,
    on,
    connect,
    disconnect,
  };
}
