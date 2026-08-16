import { useEffect, useState } from 'react';

export const useWebSockets = (onMessageReceived) => {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/complaints');

    ws.onopen = () => {
      console.log('--> Connected to Smart Campus WebSockets');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (onMessageReceived) {
        onMessageReceived(data);
      }
    };

    ws.onclose = () => {
      console.log('--> WebSocket connection closed');
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  return { isConnected };
};