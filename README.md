# Connect Four / 四子棋

一个面向计算机科学学习的四子棋引擎：实现**已解博弈的完美策略**，并提供强化学习与大模型对比实验的扩展接口。

## 核心特性

- **混合完美策略**：开局库 + 启发式中局 + 残局精确 Negamax（Pascal Pons 算法）
- **先手必胜**：与理论结论一致，空盘分析确认先手存在必胜策略
- **多 Agent 架构**：Solver / Random / Human / RL / LLM 可互换
- **RL 实验环境**：`ConnectFourEnv` 提供 Gym 风格 `reset/step` 接口
- **LLM 对比实验**：`LLMAgent` 可将棋盘编码为 prompt，与完美策略对比

## 快速开始

### Windows

前置条件：已安装 **Python 3.10+** 和 **Git**。

#### 1. 安装 Python

从 https://www.python.org/downloads/ 下载安装包，安装时勾选：

- **Add python.exe to PATH**（重要）

验证安装（打开 **PowerShell** 或 **命令提示符**）：

```powershell
python --version
pip --version
```

#### 2. 下载项目

```powershell
git clone https://github.com/zizisaigao/connect-four.git
cd connect-four
```

若 `main` 分支还没有代码，可切换到开发分支：

```powershell
git checkout cursor/connect-four-solver-6d87
```

没有 Git 时，可在 GitHub 页面点击 **Code → Download ZIP** 解压后进入文件夹。

#### 3. 创建虚拟环境并安装

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

若 PowerShell 提示无法运行脚本，先执行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

或使用 **命令提示符（cmd）** 激活环境：

```cmd
.\.venv\Scripts\activate.bat
pip install -e ".[dev]"
```

#### 4. 开始下棋

```powershell
# 你（先手）vs AI（后手）
connect-four play --p1 human --p2 solver

# 你（后手）vs AI（先手）—— AI 更强，难度更高
connect-four play --p1 solver --p2 human

# 若提示找不到 connect-four，改用：
python -m connect_four.cli play --p1 human --p2 solver
```

对局时在终端输入列号 **1～7**（从左到右），回车落子。

```
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. X . . . . .
1 2 3 4 5 6 7

Player 1, choose column [0, 1, 2, 3, 4, 5, 6]: 4    ← 输入 4 表示走第 4 列
```

#### 5. 其他常用命令

```powershell
# 分析局面
connect-four analyze

# 人机对战（玩家 vs 随机 AI，练手用）
connect-four play --p1 human --p2 random

# 退出虚拟环境
deactivate
```

> **说明**：当前是**终端文字棋盘**，没有图形窗口。棋子用 `X` / `O` 显示，`.` 表示空位。

### macOS

前置条件：已安装 [Homebrew](https://brew.sh/) 和 Python 3.10+。

```bash
# 1. 安装 Python（如尚未安装）
brew install python

# 2. 克隆仓库
git clone https://github.com/zizisaigao/connect-four.git
cd connect-four

# 3. 创建并激活虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 4. 安装项目
pip install -e ".[dev]"

# 5. 若提示找不到 connect-four 命令，将用户脚本目录加入 PATH
export PATH="$HOME/.local/bin:$PATH"
# 或直接用模块方式调用：
# python -m connect_four.cli analyze
```

常用命令：

```bash
# 分析空盘：最优首着为第 4 列
connect-four analyze

# 人机对战（终端输入列号 1-7）
connect-four play --p1 human --p2 solver

# 运行测试
pytest
```

退出虚拟环境：

```bash
deactivate
```

### Linux / 通用

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

- **[四子棋完整策略文档](docs/四子棋完整策略文档.md)** — 详细策略说明 + **代码实现状态标注**（推荐）
- [STRATEGY.md](docs/STRATEGY.md) — 简明调研摘要

- 四子棋被证明为**先手强解必胜**
- 1988 年至今的求解历史
- Bitboard、Negamax、Alpha-Beta、MTD(f) 算法说明
- 与 RL / LLM / MCTS 的对比与学习路径

完整版见 [四子棋完整策略文档](docs/四子棋完整策略文档.md)。

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
