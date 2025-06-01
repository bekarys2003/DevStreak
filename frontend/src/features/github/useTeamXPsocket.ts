// src/features/github/useTeamXPsocket.ts

import { useEffect, useState } from 'react';

export interface XPEntry {
  username: string,
  xp: number
}

// Now accept a `teamName` parameter.
export function useTeamXPsocket(teamName: string): XPEntry[] | null {
  const [entries, setEntries] = useState<XPEntry[] | null>(null);

  useEffect(() => {
    if (!teamName) return; // don’t do anything if no team is chosen

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.hostname;
    const port = '8000';
    const socket = new WebSocket(
        `${protocol}://${host}:${port}/ws/team-xp/${teamName}/`
      );

    socket.onopen = () => {
      console.log(`🌐 WebSocket connected: team=${teamName}`);
    };

    socket.onmessage = (e) => {
      try {
        const data: XPEntry[] = JSON.parse(e.data);
        setEntries(data);
      } catch (err) {
        console.error(`Failed to parse ${teamName} message`, err);
      }
    };

    socket.onclose = () => {
      console.log(`🌐 WebSocket disconnected: team=${teamName}`);
    };

    return () => {
      socket.close();
    };
  }, [teamName]);

  return entries;
}
