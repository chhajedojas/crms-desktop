import { contextBridge, ipcRenderer } from 'electron'

// Define allowed IPC channels for security
const ALLOWED_CHANNELS = [
  'crms:health_check',
  'crms:scan_directory',
  'crms:extract_metadata',
  'crms:search',
  'crms:classify_document',
  'crms:validate_gst',
  'crms:reorganize_documents',
]

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Send IPC message with channel validation
  send: (channel: string, data: unknown) => {
    // Validate channel is in allowlist
    if (!ALLOWED_CHANNELS.includes(channel)) {
      console.error(`IPC channel not allowed: ${channel}`)
      throw new Error(`IPC channel not allowed: ${channel}`)
    }
    ipcRenderer.send(channel, data)
  },

  // Listen to IPC message with channel validation
  on: (channel: string, callback: (...args: unknown[]) => void) => {
    // Validate channel is in allowlist
    if (!ALLOWED_CHANNELS.includes(channel)) {
      console.error(`IPC channel not allowed: ${channel}`)
      throw new Error(`IPC channel not allowed: ${channel}`)
    }
    ipcRenderer.on(channel, (event, ...args) => callback(...args))
  },

  // Remove listener with channel validation
  removeListener: (channel: string, callback: (...args: unknown[]) => void) => {
    // Validate channel is in allowlist
    if (!ALLOWED_CHANNELS.includes(channel)) {
      console.error(`IPC channel not allowed: ${channel}`)
      throw new Error(`IPC channel not allowed: ${channel}`)
    }
    ipcRenderer.removeListener(channel, callback)
  },

  // Expose allowlist for reference (read-only)
  allowedChannels: ALLOWED_CHANNELS,
})

export type ElectronAPI = typeof window.electronAPI
