// src/features/github/useDailyCommitsSocket.ts
import { useEffect, useState } from 'react'

export interface XPEntry {
  username: string
  xp: number
}

export function useDailyCommitsSocket(): XPEntry[] | null {
  const [entries, setEntries] = useState<XPEntry[] | null>(null)

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = window.location.hostname
    const port = '8000'  // Django ASGI port
    const socket = new WebSocket(
      `${protocol}://${host}:${port}/ws/daily-commits/`
    )

    socket.onopen = () => {
      console.log('🌐 WebSocket connected: daily-commits')
    }

    socket.onmessage = (e) => {
      try {
        const data: XPEntry[] = JSON.parse(e.data)
        setEntries(data)
      } catch (err) {
        console.error('Failed to parse daily-commits message', err)
      }
    }

    socket.onclose = () => {
      console.log('🌐 WebSocket disconnected: daily-commits')
    }

    return () => {
      socket.close()
    }
  }, [])  // no dependencies

  return entries
}