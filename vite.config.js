// Conteúdo para: sofia-command-center/vite.config.js

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5177, // Nova porta dedicada para o Command Center
    host: true, // Permite acesso na rede
  },
});

