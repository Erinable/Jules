/**
 * WebSocket context provider (Sprint 2)
 *
 * Provides global WebSocket connection accessible throughout the app.
 */

import React, {
  createContext,
  useContext,
  useMemo,
  type ReactNode,
} from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import type {
  ConnectionState,
  MessageHandler,
  MessageType,
  WebSocketConfig,
  WebSocketError,
  WSMessage,
} from "../types/websocket.types";

interface WebSocketContextValue {
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

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

interface WebSocketProviderProps {
  config: WebSocketConfig;
  children: ReactNode;
}

export function WebSocketProvider({
  config,
  children,
}: WebSocketProviderProps) {
  const ws = useWebSocket(config);

  const value = useMemo(() => ws, [ws]);

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

/**
 * Hook to access WebSocket connection from any component
 */
export function useWebSocketContext(): WebSocketContextValue {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error(
      "useWebSocketContext must be used within WebSocketProvider",
    );
  }
  return context;
}
