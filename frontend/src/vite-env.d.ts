/// <reference types="vite/client" />

interface Window {
  electronAPI: {
    send: (channel: string, data: unknown) => void
    on: (channel: string, callback: (...args: unknown[]) => void) => void
    removeListener: (channel: string, callback: (...args: unknown[]) => void) => void
  }
}
