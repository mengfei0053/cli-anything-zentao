# cli-anything-zentao

> 🇨🇳 中文 | [🇬🇧 English](#english-version)

禅道（ZenTao）项目管理系统命令行工具，基于 [CLI-Anything](https://github.com/HKUDS/CLI-Anything) 方法论构建。

通过命令行即可完整操控禅道系统——无需浏览器或 GUI。支持单次子命令模式和交互式 REPL 模式，适合 AI Agent 和开发者使用。

### 功能特性

| 模块 | 功能 |
|------|------|
| **产品管理** | 创建、查看、更新、删除产品 |
| **项目管理** | 迭代/项目增删改查 |
| **需求管理** | 需求全生命周期（创建、编辑、关闭、激活） |
| **任务管理** | 创建、编辑、开始、完成、关闭、取消 |
| **工时管理** | 查看/添加/编辑/删除任务工时记录 |
| **Bug 管理** | 创建、编辑、解决、激活、关闭 |
| **测试用例** | 创建、更新、查看列表 |
| **构建管理** | 创建、查看、删除 |
| **JSON 输出** | `--json` 参数输出机器可读格式 |
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

## 使用方式

### 交互模式（默认）

```bash
cli-anything-zentao
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

# 开始任务
cli-anything-zentao task start 42

# 添加任务工时
cli-anything-zentao effort add 42 3.5 --left 4.0 --work "完成了登录模块开发"

# 查看任务工时列表
cli-anything-zentao effort list 42

# 更新工时记录
cli-anything-zentao effort update 101 --consumed 4.0 --work "修改工作内容"

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
| `effort list <任务ID>` | 列出任务工时 |
| `effort get <工时ID>` | 查看工时详情 |
| `effort add <任务ID> <工时>` | 添加工时（支持 --left, --date, --work） |
| `effort update <工时ID>` | 更新工时记录 |
| `effort delete <工时ID>` | 删除工时记录 |
| `bug list <产品ID>` | 列出 Bug |
| `bug get <id>` | 查看 Bug 详情 |
| `bug create <产品ID> <标题>` | 创建 Bug |
| `bug update <id>` | 更新 Bug |
| `bug resolve <id>` | 解决 Bug |
| `bug activate <id>` | 重新激活 Bug |
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

```bash
# 单元测试（无需禅道服务器）
python -m pytest cli_anything/zentao/tests/test_core.py -v

# E2E 测试（需要禅道服务器）
export ZENTAO_URL="http://localhost/zentao"
export ZENTAO_USER="admin"
export ZENTAO_PASSWORD="你的密码"
python -m pytest cli_anything/zentao/tests/ -v
```

## AI Agent 集成

安装 SKILL.md 供 AI Agent 发现：

```bash
npx skills add HKUDS/CLI-Anything --skill cli-anything-zentao -g -y
```

---

## English Version

### CLI for [ZenTao](https://www.zentao.pm/) Project Management

A command-line interface for ZenTao, built using the [CLI-Anything](https://github.com/HKUDS/CLI-Anything) methodology. Lets AI agents and developers manage projects, tasks, bugs, and more — entirely from the terminal.

### Features

| Module | Capabilities |
|--------|-------------|
| **Product** | Create, list, update, delete products |
| **Project** | Sprint/project CRUD |
| **Story** | Full lifecycle (create, edit, close, activate) |
| **Task** | Create, edit, start, finish, close, cancel |
| **Effort** | List/add/update/delete task work hour records |
| **Bug** | Create, edit, resolve, activate, close |
| **Testcase** | Create, update, list |
| **Build** | Create, list, delete |
| **`--json`** | Machine-readable output for agent consumption |
| **REPL** | Interactive mode with history and branded prompt |

### Installation

```bash
# From GitHub (recommended)
pip install git+https://github.com/mengfei0053/cli-anything-zentao.git

# From source
cd /path/to/agent-harness/
pip install -e .

# Upgrade
pip install --upgrade git+https://github.com/mengfei0053/cli-anything-zentao.git
```

### Configuration

```bash
export ZENTAO_URL="http://localhost/zentao"
export ZENTAO_USER="admin"
export ZENTAO_PASSWORD="your_password"
```

### Usage Examples

```bash
# List products
cli-anything-zentao --json product list

# Create a task
cli-anything-zentao task create 5 "Write unit tests" \
  --type devel --pri 2 --assigned-to dev1

# Add work hours (effort)
cli-anything-zentao effort add 42 3.5 --left 4.0 --work "Completed login module"

# List efforts for a task
cli-anything-zentao effort list 42

# Update an effort record
cli-anything-zentao effort update 101 --consumed 4.0 --work "Updated work log"

# Resolve a bug
cli-anything-zentao bug resolve 42 --resolution fixed
```

### Testing

```bash
# Unit tests (no server needed)
python -m pytest cli_anything/zentao/tests/test_core.py -v

# E2E tests (requires ZenTao server)
export ZENTAO_URL="http://localhost/zentao"
export ZENTAO_USER="admin"
export ZENTAO_PASSWORD="***"
python -m pytest cli_anything/zentao/tests/ -v
```

### Project Structure

```
agent-harness/
├── setup.py
├── README.md
├── ZENTAO.md
└── cli_anything/
    └── zentao/
        ├── zentao_cli.py        # CLI entry point
        ├── core/                # Business modules
        │   ├── product.py
        │   ├── project.py
        │   ├── story.py
        │   ├── task.py
        │   ├── effort.py        # Task effort/work hour management
        │   ├── bug.py
        │   ├── testcase.py
        │   └── build.py
        ├── utils/
        │   ├── zentao_backend.py
        │   └── repl_skin.py
        └── tests/
            ├── TEST.md
            ├── test_core.py
            └── test_full_e2e.py
```

### License

MIT
