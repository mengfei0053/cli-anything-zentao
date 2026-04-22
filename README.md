# cli-anything-zentao

禅道（ZenTao）项目管理系统命令行工具，基于 [CLI-Anything](https://github.com/HKUDS/CLI-Anything) 方法论构建。

## 项目简介

通过命令行即可完整操控禅道系统——无需浏览器或 GUI。支持单次子命令模式和交互式 REPL 模式，适合 AI Agent 和开发者使用。

### 功能特性

| 模块 | 功能 |
|------|------|
| **产品管理** | 创建、查看、更新、删除产品 |
| **项目管理** | 迭代/项目增删改查 |
| **需求管理** | 需求全生命周期（创建、编辑、关闭、激活） |
| **任务管理** | 创建、编辑、开始、完成、关闭、取消 |
| **Bug 管理** | 创建、编辑、解决、激活、关闭 |
| **测试用例** | 创建、更新、查看列表 |
| **构建管理** | 创建、查看、删除 |
| **JSON 输出** | `--json` 参数输出机器可读格式，方便 Agent 消费 |
| **交互式 REPL** | 带历史记录、自动补全和品牌化提示符 |

## 安装

### 环境要求

- Python 3.8+
- 运行中的禅道实例（可通过 HTTP 访问）

### 方式一：从 GitHub 安装（推荐）

```bash
pip install git+https://github.com/mengfei0053/cli-anything-zentao.git
```

带 REPL 支持：
```bash
pip install "git+https://github.com/mengfei0053/cli-anything-zentao.git#egg=cli-anything-zentao[repl]"
```

更新到最新版：
```bash
pip install --upgrade git+https://github.com/mengfei0053/cli-anything-zentao.git
```

### 方式二：从源码安装

```bash
cd /path/to/agent-harness/
pip install -e .
```

### 方式三：带 REPL 支持安装

```bash
pip install -e ".[repl]"
```

### 方式四：带开发依赖安装

```bash
pip install -e ".[dev]"
```

## 配置

设置环境变量以连接禅道服务器：

```bash
export ZENTAO_URL="http://localhost/zentao"
export ZENTAO_USER="admin"
export ZENTAO_PASSWORD="你的密码"
```

或者通过命令行参数传入：

```bash
cli-anything-zentao --url http://localhost/zentao --user admin --password xxx
```

也可以使用预生成的会话 Token：

```bash
export ZENTAO_TOKEN="your-session-token"
```

## 使用方式

### 交互模式（默认）

直接运行即可进入交互式 REPL：

```bash
cli-anything-zentao
```

```
╭────────────────────────────────────────────────────────────────────────╮
│ ◆  cli-anything · Zentao                                               │
│    v1.0.0                                                              │
│                                                                        │
│    Type help for commands, quit to exit                                │
╰────────────────────────────────────────────────────────────────────────╯

zentao ❯ products
zentao ❯ create-product "我的产品" MP
zentao ❯ quit
```

### 单次命令模式

```bash
# 测试连接
cli-anything-zentao connect

# 列出所有产品（JSON 格式）
cli-anything-zentao --json product list

# 创建项目
cli-anything-zentao project create "迭代1" "SP1" \
  --model scrum --type sprint \
  --begin 2025-01-01 --end 2025-01-31

# 创建需求
cli-anything-zentao story create 1 "登录功能" \
  --spec "作为用户我想要登录系统" --pri 1

# 创建任务
cli-anything-zentao task create 5 "编写单元测试" \
  --type devel --pri 2 --assigned-to dev1

# 创建 Bug
cli-anything-zentao bug create 1 "登录时空指针异常" \
  --severity 2 --pri 1 --type codeerror

# 解决 Bug
cli-anything-zentao bug resolve 42 --resolution fixed

# 创建测试用例
cli-anything-zentao testcase create 1 "验证登录" \
  --steps "1. 输入账号密码 2. 点击登录" --pri 1

# 创建构建
cli-anything-zentao build create 1 "v1.0.0" \
  --builder ci-bot --desc "正式版本构建"
```

### JSON 输出

所有命令均支持 `--json` 参数，输出机器可读格式：

```bash
cli-anything-zentao --json product list
```

## 命令参考

| 命令 | 描述 |
|------|------|
| `connect` | 测试禅道服务器连接 |
| `product list` | 列出所有产品 |
| `product get <id>` | 查看产品详情 |
| `product create <名称> <编码>` | 创建产品 |
| `product update <id>` | 更新产品 |
| `product delete <id>` | 删除产品 |
| `project list` | 列出所有项目 |
| `project get <id>` | 查看项目详情 |
| `project create <名称> <编码>` | 创建项目 |
| `project update <id>` | 更新项目 |
| `project delete <id>` | 删除项目 |
| `story list <产品ID>` | 列出产品需求 |
| `story get <id>` | 查看需求详情 |
| `story create <产品ID> <标题>` | 创建需求 |
| `story update <id>` | 更新需求 |
| `story close <id>` | 关闭需求 |
| `story activate <id>` | 激活已关闭的需求 |
| `task list <执行ID>` | 列出任务 |
| `task get <id>` | 查看任务详情 |
| `task create <执行ID> <名称>` | 创建任务 |
| `task update <id>` | 更新任务 |
| `task start <id>` | 开始任务 |
| `task finish <id>` | 完成任务 |
| `task close <id>` | 关闭任务 |
| `task cancel <id>` | 取消任务 |
| `bug list <产品ID>` | 列出 Bug |
| `bug get <id>` | 查看 Bug 详情 |
| `bug create <产品ID> <标题>` | 创建 Bug |
| `bug update <id>` | 更新 Bug |
| `bug resolve <id>` | 解决 Bug |
| `bug activate <id>` | 重新激活已解决的 Bug |
| `bug close <id>` | 关闭 Bug |
| `testcase list <产品ID>` | 列出测试用例 |
| `testcase get <id>` | 查看用例详情 |
| `testcase create <产品ID> <标题>` | 创建用例 |
| `testcase update <id>` | 更新用例 |
| `build list` | 列出构建 |
| `build get <id>` | 查看构建详情 |
| `build create <产品ID> <名称>` | 创建构建 |
| `build delete <id>` | 删除构建 |

## 测试

### 运行单元测试（无需禅道服务器）

```bash
python -m pytest cli_anything/zentao/tests/test_core.py -v
```

### 运行 E2E 测试（需要禅道服务器）

```bash
export ZENTAO_URL="http://localhost/zentao"
export ZENTAO_USER="admin"
export ZENTAO_PASSWORD="你的密码"
python -m pytest cli_anything/zentao/tests/ -v
```

### 强制已安装模式运行测试

```bash
CLI_ANYTHING_FORCE_INSTALLED=1 python -m pytest cli_anything/zentao/tests/ -v
```

## 项目结构

```
agent-harness/
├── setup.py                    # 包配置
├── README.md                   # 使用说明
├── ZENTAO.md                   # 软件专属 SOP 文档
└── cli_anything/
    └── zentao/
        ├── zentao_cli.py       # CLI 主入口
        ├── core/               # 核心业务模块
        │   ├── product.py      # 产品
        │   ├── project.py      # 项目
        │   ├── story.py        # 需求
        │   ├── task.py         # 任务
        │   ├── bug.py          # Bug
        │   ├── testcase.py     # 测试用例
        │   └── build.py        # 构建
        ├── utils/              # 工具模块
        │   ├── zentao_backend.py  # 禅道后端集成
        │   └── repl_skin.py    # REPL 交互皮肤
        └── tests/              # 测试
            ├── TEST.md         # 测试计划与结果
            ├── test_core.py    # 单元测试（37 个）
            └── test_full_e2e.py # E2E/子进程测试（10 个）
```

## 测试统计

| 指标 | 数值 |
|------|------|
| 总计 | 47 |
| 通过 | 39 |
| 跳过 | 8（需要 ZENTAO_URL） |
| 失败 | 0 |
| 执行时间 | 0.12s |

- 单元测试：**37/37 通过 (100%)**
- CLI 基础测试：**2/2 通过 (100%)**

## AI Agent 集成

安装 SKILL.md 供 AI Agent 发现：

```bash
npx skills add HKUDS/CLI-Anything --skill cli-anything-zentao -g -y
```

Skill 文件为 Agent 提供完整的命令参考和使用示例。

## 许可证

MIT
