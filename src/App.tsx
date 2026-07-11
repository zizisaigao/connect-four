import { useMemo, useState } from 'react'
import { applyMove, COLS, createInitialState, getDropRow, type GameState } from './game'
import './App.css'

function statusText(state: GameState): string {
  if (state.winner) return `${state.winner === 'red' ? 'Red' : 'Yellow'} wins!`
  if (state.isDraw) return "It's a draw!"
  return `${state.currentPlayer === 'red' ? 'Red' : 'Yellow'}'s turn`
}

export default function App() {
  const [state, setState] = useState<GameState>(createInitialState)
  const [hoverCol, setHoverCol] = useState<number | null>(null)

  const winning = useMemo(() => {
    const set = new Set<string>()
    for (const [r, c] of state.winningCells) set.add(`${r}-${c}`)
    return set
  }, [state.winningCells])

  const gameOver = state.winner !== null || state.isDraw

  function handleColumnClick(col: number) {
    setState((prev) => applyMove(prev, col))
  }

  return (
    <main className="app">
      <h1>Connect Four</h1>

      <p className={`status status--${state.winner ?? (state.isDraw ? 'draw' : state.currentPlayer)}`}>
        {statusText(state)}
      </p>

      <div className="board" role="grid" aria-label="Connect Four board">
        {Array.from({ length: COLS }, (_, col) => {
          const dropRow = getDropRow(state.board, col)
          const columnFull = dropRow === -1
          return (
            <button
              key={col}
              type="button"
              className="column"
              aria-label={`Drop disc in column ${col + 1}`}
              disabled={gameOver || columnFull}
              onClick={() => handleColumnClick(col)}
              onMouseEnter={() => setHoverCol(col)}
              onMouseLeave={() => setHoverCol((c) => (c === col ? null : c))}
            >
              {state.board.map((row, rowIdx) => {
                const cell = row[col]
                const isGhost =
                  !gameOver && !columnFull && hoverCol === col && rowIdx === dropRow && cell === null
                const cls = cell
                  ? `disc disc--${cell}${winning.has(`${rowIdx}-${col}`) ? ' disc--win' : ''}`
                  : isGhost
                    ? `disc disc--ghost disc--${state.currentPlayer}`
                    : 'disc'
                return (
                  <div key={rowIdx} className="cell">
                    <div className={cls} />
                  </div>
                )
              })}
            </button>
          )
        })}
      </div>

      <button type="button" className="reset" onClick={() => setState(createInitialState())}>
        New game
      </button>
    </main>
  )
}
