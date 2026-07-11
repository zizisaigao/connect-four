# AGENTS.md

## Project overview

Connect Four — a two-player web game built with **Vite + React + TypeScript**.
Pure game logic lives in `src/game.ts` (framework-agnostic, fully unit-tested);
the UI is in `src/App.tsx`.

## Commands

- Install: `npm install`
- Dev server: `npm run dev` (Vite, http://localhost:5173)
- Lint: `npm run lint`
- Tests: `npm test` (Vitest, run once) / `npm run test:watch`
- Build: `npm run build` (`tsc -b` type-check + `vite build`)
- Preview production build: `npm run preview`

## Cursor Cloud specific instructions

- Single frontend service only; there is no backend, database, or other service to start.
- The dev server is configured with `host: true` in `vite.config.ts`, so it listens
  on all interfaces (needed to reach it from outside the VM).
- Vitest runs in the `node` environment (see `vite.config.ts`) because the tested
  code (`src/game.ts`) is pure logic with no DOM dependency. Add jsdom only if you
  start testing React components.
