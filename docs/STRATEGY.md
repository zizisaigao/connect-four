# 四子棋（Connect Four）完美策略调研

## 结论

四子棋是**强解（strongly solved）**的完全信息零和博弈：在双方最优策略下，**先手必胜**。这不是平局游戏（如井字棋在双方最优时会和棋），而是一个有确定胜负的已解博弈。

对本项目而言，最实用的实现路径是：

1. **Bitboard 位棋盘**表示状态
2. **Negamax + Alpha-Beta 剪枝**搜索博弈树
3. **置换表（Transposition Table）**缓存子问题
4. **着法排序**（优先中心列、高威胁列）提升剪枝效率
5. **MTD(f) / 二分搜索**精确求分值，而非盲目加深

## 历史与里程碑

| 时间 | 研究者 | 方法 |
|------|--------|------|
| 1988-10 | James D. Allen | 规则 + 知识库 |
| 1988-10 | Victor Allis (VICTOR) | 知识型搜索 + Zugzwang 概念 |
| 1995 | John Tromp | 暴力搜索 + 开局库（8 步内局面） |
| 2015+ | Pascal Pons (gamesolver.org) | Bitboard + Negamax + 开局库，毫秒级求解 |

参考资源：

- [Solving Connect 4 教程](http://blog.gamesolver.org/solving-connect-four/01-introduction/)
- [Pascal Pons Connect4 Solver](https://github.com/PascalPons/connect4)
- [Victor Allis 论文](https://www.emerald.com/insight/content/doi/10.1108/eb010588/full/html)

## 算法细节

### 1. Bitboard 表示

标准 7×6 棋盘用两个 64 位整数编码：

- `mask`：所有已落子位置
- `current_position`：当前行棋方的棋子

每列占 `HEIGHT + 1 = 7` 位，最高位作为哨兵，防止纵向四连误判。

胜负检测可并行完成（位运算）：

```python
# 横向、纵向、两条斜向
diag1 = position & (position >> 7)
hori  = position & (position >> 1)
# ... 再检查是否有连续 4 子
```

### 2. Negamax

Negamax 是 Minimax 在零和博弈中的简化形式：

```
score(position) = max(-score(child) for child in legal_moves)
```

从当前玩家视角，对手局面分值直接取负即可，无需分别实现 max/min 两层逻辑。

### 3. Alpha-Beta 剪枝

维护搜索窗口 `[alpha, beta]`：

- 若某分支分值 `>= beta`，对手不会选择通往该分支的上层着法，可剪枝
- 配合**中心优先**着法顺序 `[3,4,2,5,1,6,0]`，剪枝效率可接近 `O(b^(d/2))`

### 4. 非输着法过滤（Possible Non-Losing Moves）

Pascal Pons 的关键启发式：

- 若对手有唯一强制应对点，必须走该点
- 若对手有两处可立即获胜的位置，当前方已败
- 避免在对手威胁正下方落子（除非被迫）

这大幅缩小搜索分支，是实用求解器的核心技巧之一。

### 5. 分值编码

分值表示**距离终局的步数**，而非启发式估值：

- 当前方必胜：`+(剩余步数/2)`
- 当前方必败：`-(剩余步数/2)`
- 和棋：`0`

因此搜索结果是**精确博弈值**，不是近似估计。

### 6. MTD(f) 精确求解

不固定搜索深度，而是在 `[min_score, max_score]` 上二分，每次用极窄窗口 `[mid, mid+1]` 调用 Negamax（Null Window Search），根据结果收缩区间，直到收敛到精确分值。

## 与强化学习、大模型的关系

| 方法 | 强度 | 适用场景 |
|------|------|----------|
| 完美求解器 | 最优 | 基准对手、验证 RL 策略、教学演示 |
| Minimax + 启发式 | 强（深度受限） | 理解对抗搜索 |
| MCTS | 强（需大量模拟） | AlphaZero 风格自对弈 |
| Q-Learning / DQN | 弱~中 | 学习价值函数与探索 |
| 大模型 Agent | 弱（通常） | 自然语言推理、可解释性对比实验 |

学术对比（见 arXiv:2405.16595）表明：在四子棋上，经典 Minimax 在配置正确时可达到最优；MCTS 和 RL 需要更多工程才能达到相近水平；AlphaZero 风格（RL + MCTS）最强，但复杂度也最高。

**推荐学习路径：**

1. 先理解并运行本项目 `SolverAgent`（完美基准）
2. 用 `ConnectFourEnv` + `RLAgent` 实验 Q-learning
3. 用 `LLMAgent` 对比 LLM 与求解器的着法差异
4. 进阶：实现 MCTS 或阅读 AlphaZero 论文

## 本项目实现对应关系

| 模块 | 文件 | 说明 |
|------|------|------|
| 位棋盘 | `connect_four/board.py` | Pascal Pons 布局 |
| 精确求解器 | `connect_four/solver.py` | Negamax + αβ + 置换表 + MTD(f) |
| 启发式搜索 | `connect_four/heuristic.py` | 深度受限时的评估函数 |
| 开局库 | `connect_four/opening_book.py` | 空盘等已知强解局面 |
| 混合策略 | `Solver` 类 | 开局/中局启发式 + 残局精确求解 |
| 完美 Agent | `connect_four/agents/solver_agent.py` | 包装求解器 |
| RL 环境 | `connect_four/env.py` | Gym 风格接口 |
| RL 占位 | `connect_four/agents/rl_agent.py` | Q-learning 骨架 |
| LLM 占位 | `connect_four/agents/llm_agent.py` | Prompt + API 调用 |

### 关于 Python 实现的性能说明

完整博弈树的纯 Python 暴力搜索在开局阶段较慢（C++/Rust 实现可在毫秒级完成）。本项目采用**教学友好的混合策略**：

1. **开局库**：空盘等局面直接返回已证明的结论（先手必胜，最优首着为第 4 列）
2. **中局**：深度受限 Negamax + 威胁启发式（默认深度 6），交互响应快
3. **残局**（剩余 ≤14 步）：自动切换为精确求解器
4. **CLI `--exact`**：在残局局面强制使用精确分析

算法本身与 Pascal Pons 求解器一致；性能差异来自语言与是否预计算开局库。

## 已知最优开局

空棋盘最优首着是**中间列（第 4 列，0-index 为 3）**。本项目求解器应自动得出该结论，可作为回归测试。
