# Connect Four

A two-player Connect Four game built with Vite, React, and TypeScript.

Drop discs into the 7×6 grid — the first player to line up four of their colour
horizontally, vertically, or diagonally wins.

## Getting started

```bash
npm install
npm run dev      # start the dev server at http://localhost:5173
```

## Scripts

| Command            | Description                                   |
| ------------------ | --------------------------------------------- |
| `npm run dev`      | Start the Vite dev server                     |
| `npm run build`    | Type-check and build for production           |
| `npm run preview`  | Preview the production build                  |
| `npm run lint`     | Run ESLint                                    |
| `npm test`         | Run the Vitest unit tests once                |
| `npm run test:watch` | Run tests in watch mode                     |

## Project structure

- `src/game.ts` — pure Connect Four game logic (board, moves, win detection).
- `src/__tests__/game.test.ts` — unit tests for the game logic.
- `src/App.tsx` — React UI for the game board.

## License

MIT — see [LICENSE](./LICENSE).
