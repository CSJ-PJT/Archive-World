import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  publicDir: '../assets/previews',
  server: { host: '127.0.0.1', port: 4173 },
  build: {
    target: 'es2022', sourcemap: true,
    // The landing view never imports these modules. Split the deferred viewer
    // into inspectable vendor chunks instead of masking its size with a larger
    // warning limit.
    chunkSizeWarningLimit: 900,
    rolldownOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('three/examples/jsm/')) return 'three-extras';
          if (id.includes('/node_modules/three/')) return 'three-core';
        }
      }
    }
  }
});
