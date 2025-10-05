import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue( )],
  server: {
    host: '0.0.0.0', // Use '0.0.0.0' para ser mais explícito
    port: 5177,
    strictPort: true,
    allowedHosts: [
      'command.meshwave.com.br'
    ]
  }
})
