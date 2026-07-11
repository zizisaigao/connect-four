# Connect Four / 四子棋

一个面向计算机科学学习的四子棋引擎：实现**已解博弈的完美策略**，并提供强化学习与大模型对比实验的扩展接口。

## 核心特性

- **混合完美策略**：开局库 + 启发式中局 + 残局精确 Negamax（Pascal Pons 算法）
- **先手必胜**：与理论结论一致，空盘分析确认先手存在必胜策略
- **多 Agent 架构**：Solver / Random / Human / RL / LLM 可互换
- **RL 实验环境**：`ConnectFourEnv` 提供 Gym 风格 `reset/step` 接口
- **LLM 对比实验**：`LLMAgent` 可将棋盘编码为 prompt，与完美策略对比

## 快速开始

```bash
pip install -e ".[dev]"

# 分析空盘：最优首着为第 4 列
connect-four analyze

# 分析指定局面（列号 1-7）
connect-four analyze --sequence 3542

# 残局精确分析（剩余步数较少时）
connect-four analyze --sequence 354261273 --exact

# 人机对战（玩家 vs 完美 AI）
connect-four play --p1 human --p2 solver

# 求解器性能基准
connect-four benchmark

# 运行测试
pytest
```

## 策略调研

详见 [docs/STRATEGY.md](docs/STRATEGY.md)，涵盖：

- 四子棋被证明为**先手强解必胜**
- 1988 年至今的求解历史
- Bitboard、Negamax、Alpha-Beta、MTD(f) 算法说明
- 与 RL / LLM / MCTS 的对比与学习路径

## 项目结构

```
connect_four/
  board.py          # 位棋盘与规则
  solver.py         # 完美求解器
  game.py           # 对局流程
  env.py            # RL 环境
  cli.py            # 命令行入口
  agents/
    solver_agent.py # 完美策略 Agent
    rl_agent.py     # Q-learning 骨架
    llm_agent.py    # 大模型 Agent 占位
docs/
  STRATEGY.md       # 策略调研文档
tests/
```

## RL 实验示例

```python
from connect_four.env import ConnectFourEnv
from connect_four.agents.rl_agent import RLAgent
from connect_four.agents.random_agent import RandomAgent

env = ConnectFourEnv()
agent = RLAgent(epsilon=0.2)
opponent = RandomAgent()

for episode in range(100):
    reward = agent.train_episode(env, lambda pos: opponent.choose_move(pos, 2))
    print(f"episode {episode}: reward={reward}")
```

## LLM 实验示例

```bash
export OPENAI_API_KEY=your_key
pip install -e ".[llm]"
```

```python
from connect_four.agents.llm_agent import LLMAgent
from connect_four.board import Position

agent = LLMAgent(fallback_to_solver=True)
move = agent.choose_move(Position(), player=1)
```

## 参考

- [Pascal Pons Connect4 Solver](https://github.com/PascalPons/connect4)
- [Solving Connect 4 Tutorial](http://blog.gamesolver.org/solving-connect-four/01-introduction/)
- [An Evolutionary Framework for Connect-4 (arXiv:2405.16595)](https://arxiv.org/abs/2405.16595)

## License

MIT
