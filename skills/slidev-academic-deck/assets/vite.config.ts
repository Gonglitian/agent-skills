import { defineConfig } from 'vite'

// Slidev >= 52 (Rolldown) fails `npm run build` on public/ assets referenced by
// absolute URL (/media/x.gif, /figs/x.png) without this. See references/slidev-gotchas.md #3.
export default defineConfig({
  server: { fs: { strict: false, allow: ['.'] } },
  assetsInclude: ['**/*.gif', '**/*.mp4'],
})
