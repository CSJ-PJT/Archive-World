import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env=loadEnv(mode, process.cwd(), '');
  const generated=env.VITE_ARCHIVE_WORLD_RUNTIME_MODE==='generated';
  return {
  base: './',
  // Source fixtures are useful for regression mode only. Generated mode loads
  // previews and manifests exclusively from the external output server.
  publicDir: generated ? false : '../assets/previews',
  server: { host: '127.0.0.1', port: 4173 },
  build: {
    outDir: env.ARCHIVE_WORLD_VIEWER_OUT_DIR || 'dist',
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
};
});
