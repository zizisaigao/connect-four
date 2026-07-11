import { describe, expect, it } from 'vitest'
import {
  applyMove,
  COLS,
  createEmptyBoard,
  createInitialState,
  getDropRow,
  ROWS,
} from '../game'

describe('board setup', () => {
  it('creates an empty board of the right size', () => {
    const board = createEmptyBoard()
    expect(board).toHaveLength(ROWS)
    expect(board.every((row) => row.length === COLS)).toBe(true)
    expect(board.flat().every((cell) => cell === null)).toBe(true)
  })

  it('starts with red to move and no winner', () => {
    const state = createInitialState()
    expect(state.currentPlayer).toBe('red')
    expect(state.winner).toBeNull()
    expect(state.isDraw).toBe(false)
  })
})

describe('dropping discs', () => {
  it('drops a disc to the bottom of an empty column', () => {
    const state = createInitialState()
    const next = applyMove(state, 3)
    expect(next.board[ROWS - 1][3]).toBe('red')
    expect(next.currentPlayer).toBe('yellow')
  })

  it('stacks discs on top of each other', () => {
    let state = createInitialState()
    state = applyMove(state, 0) // red bottom
    state = applyMove(state, 0) // yellow above
    expect(state.board[ROWS - 1][0]).toBe('red')
    expect(state.board[ROWS - 2][0]).toBe('yellow')
  })

  it('ignores moves on a full column', () => {
    let state = createInitialState()
    for (let i = 0; i < ROWS; i++) state = applyMove(state, 2)
    expect(getDropRow(state.board, 2)).toBe(-1)
    const before = state
    const after = applyMove(state, 2)
    expect(after).toBe(before)
  })
})

describe('win detection', () => {
  it('detects a vertical win', () => {
    let state = createInitialState()
    // red: col 0 x4, yellow: col 1 x3
    state = applyMove(state, 0) // R
    state = applyMove(state, 1) // Y
    state = applyMove(state, 0) // R
    state = applyMove(state, 1) // Y
    state = applyMove(state, 0) // R
    state = applyMove(state, 1) // Y
    state = applyMove(state, 0) // R -> vertical 4
    expect(state.winner).toBe('red')
    expect(state.winningCells).toHaveLength(4)
  })

  it('detects a horizontal win', () => {
    let state = createInitialState()
    state = applyMove(state, 0) // R
    state = applyMove(state, 0) // Y
    state = applyMove(state, 1) // R
    state = applyMove(state, 1) // Y
    state = applyMove(state, 2) // R
    state = applyMove(state, 2) // Y
    state = applyMove(state, 3) // R -> horizontal 4
    expect(state.winner).toBe('red')
  })

  it('detects a diagonal win', () => {
    let state = createInitialState()
    // Build a down-right diagonal for red.
    state = applyMove(state, 0) // R (5,0)
    state = applyMove(state, 1) // Y (5,1)
    state = applyMove(state, 1) // R (4,1)
    state = applyMove(state, 2) // Y (5,2)
    state = applyMove(state, 2) // R (4,2)
    state = applyMove(state, 3) // Y (5,3)
    state = applyMove(state, 2) // R (3,2)
    state = applyMove(state, 3) // Y (4,3)
    state = applyMove(state, 3) // R (3,3)
    state = applyMove(state, 6) // Y filler (5,6)
    state = applyMove(state, 3) // R (2,3) -> diagonal (5,0)(4,1)(3,2)(2,3)
    expect(state.winner).toBe('red')
  })

  it('does not allow moves after a win', () => {
    let state = createInitialState()
    state = applyMove(state, 0)
    state = applyMove(state, 1)
    state = applyMove(state, 0)
    state = applyMove(state, 1)
    state = applyMove(state, 0)
    state = applyMove(state, 1)
    state = applyMove(state, 0) // red wins
    const afterWin = applyMove(state, 5)
    expect(afterWin).toBe(state)
  })
})
