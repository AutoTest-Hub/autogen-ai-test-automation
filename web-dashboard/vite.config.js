import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    allowedHosts: ['c457fb874975.ngrok-free.app', '5b53c77cc768.ngrok-free.app', 'e51aa9033274.ngrok-free.app', '73f6be212419.ngrok-free.app'],
  },
})

