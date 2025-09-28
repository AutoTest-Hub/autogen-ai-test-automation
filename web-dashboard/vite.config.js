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
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['c457fb874975.ngrok-free.app', '5b53c77cc768.ngrok-free.app', 'e51aa9033274.ngrok-free.app', '73f6be212419.ngrok-free.app', '0ee359bb3403.ngrok-free.app', 'ce39141be291.ngrok-free.app', '7891a5a5b100.ngrok-free.app', '2cd223d7288a.ngrok-free.app', '20733040a9fa.ngrok-free.app'],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})

