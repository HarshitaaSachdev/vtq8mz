import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In development, forward every /api request to the Python backend.
// Set API_URL to point at a backend running somewhere other than port 8000.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': process.env.API_URL || 'http://localhost:8000',
    },
  },
})