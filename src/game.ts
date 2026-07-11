export const ROWS = 6
export const COLS = 7
export const CONNECT = 4

export type Player = 'red' | 'yellow'
export type Cell = Player | null
export type Board = Cell[][]

export interface GameState {
  board: Board
  currentPlayer: Player
  winner: Player | null
  winningCells: Array<[number, number]>
  isDraw: boolean
}

export function createEmptyBoard(): Board {
  return Array.from({ length: ROWS }, () => Array.from({ length: COLS }, () => null))
}

export function createInitialState(): GameState {
  return {
    board: createEmptyBoard(),
    currentPlayer: 'red',
    winner: null,
    winningCells: [],
    isDraw: false,
  }
}

/**
 * Returns the row index a disc would land in for the given column, or -1 if
 * the column is full.
 */
export function getDropRow(board: Board, col: number): number {
  for (let row = ROWS - 1; row >= 0; row--) {
    if (board[row][col] === null) return row
  }
  return -1
}

function inBounds(row: number, col: number): boolean {
  return row >= 0 && row < ROWS && col >= 0 && col < COLS
}

/**
 * Given the last move, detect whether it completes a line of CONNECT discs.
 * Returns the winning cells (including the placed one) or an empty array.
 */
export function findWinningCells(board: Board, row: number, col: number): Array<[number, number]> {
  const player = board[row][col]
  if (player === null) return []

  const directions: Array<[number, number]> = [
    [0, 1], // horizontal
    [1, 0], // vertical
    [1, 1], // diagonal down-right
    [1, -1], // diagonal down-left
  ]

  for (const [dr, dc] of directions) {
    const line: Array<[number, number]> = [[row, col]]

    for (const sign of [1, -1]) {
      let r = row + dr * sign
      let c = col + dc * sign
      while (inBounds(r, c) && board[r][c] === player) {
        line.push([r, c])
        r += dr * sign
        c += dc * sign
      }
    }

    if (line.length >= CONNECT) return line
  }

  return []
}

export function isBoardFull(board: Board): boolean {
  return board[0].every((cell) => cell !== null)
}

/**
 * Applies a move to the current column. Returns a new GameState. If the move is
 * illegal (full column or game already over), the same state is returned.
 */
export function applyMove(state: GameState, col: number): GameState {
  if (state.winner || state.isDraw) return state

  const row = getDropRow(state.board, col)
  if (row === -1) return state

  const board = state.board.map((r) => r.slice())
  board[row][col] = state.currentPlayer

  const winningCells = findWinningCells(board, row, col)
  const winner = winningCells.length > 0 ? state.currentPlayer : null
  const isDraw = winner === null && isBoardFull(board)

  return {
    board,
    currentPlayer: winner || isDraw ? state.currentPlayer : state.currentPlayer === 'red' ? 'yellow' : 'red',
    winner,
    winningCells,
    isDraw,
  }
}
