# cli-anything-zentao Test Plan

## Test Inventory Plan

- `test_core.py`: ~25 unit tests planned
- `test_full_e2e.py`: ~12 E2E/subprocess tests planned

---

## Unit Test Plan

### test_core.py

#### ZenTaoBackend Tests (test_core.py)
| # | Test | Description |
|---|------|-------------|
| 1 | `test_backend_init_from_env` | Backend initializes from environment variables |
| 2 | `test_backend_init_from_args` | Backend initializes from explicit arguments |
| 3 | `test_backend_missing_url_raises` | Missing URL raises ZenTaoConfigError |
| 4 | `test_backend_url_strip_trailing_slash` | URL trailing slash is stripped |
| 5 | `test_backend_build_url_simple` | URL built correctly with module and method |
| 6 | `test_backend_build_url_with_params` | URL built correctly with query parameters |
| 7 | `test_backend_build_url_none_params_skipped` | None-valued params are excluded |
| 8 | `test_api_error_exception` | ZenTaoAPIError stores status_code and response |
| 9 | `test_config_error_exception` | ZenTaoConfigError is raised with clear message |

#### Product Operation Tests (test_core.py)
| # | Test | Description |
|---|------|-------------|
| 10 | `test_create_product_builds_data` | create_product builds correct data dict |
| 11 | `test_create_product_with_kwargs` | Extra kwargs are merged into data |

#### Project Operation Tests (test_core.py)
| # | Test | Description |
|---|------|-------------|
| 12 | `test_create_project_builds_data` | create_project builds correct data dict |
| 13 | `test_create_project_default_model` | Default model is "scrum" |

#### Story Operation Tests (test_core.py)
| # | Test | Description |
|---|------|-------------|
| 14 | `test_create_story_builds_data` | create_story builds correct data dict |
| 15 | `test_create_story_priority_range` | Priority field accepts 1-4 |

#### Task Operation Tests (test_core.py)
| # | Test | Description |
|---|------|-------------|
| 16 | `test_create_task_builds_data` | create_task builds correct data dict |
| 17 | `test_create_task_with_all_fields` | All optional fields are included |

#### Bug Operation Tests (test_core.py)
| # | Test | Description |
|---|------|-------------|
| 18 | `test_create_bug_builds_data` | create_bug builds correct data dict |
| 19 | `test_resolve_bug_builds_data` | resolve_bug builds resolution data dict |
| 20 | `test_bug_severity_levels` | Severity accepts 1-4 values |

#### Test Case Operation Tests (test_core.py)
| # | Test | Description |
|---|------|-------------|
| 21 | `test_create_testcase_builds_data` | create_testcase builds correct data dict |

#### Build Operation Tests (test_core.py)
| # | Test | Description |
|---|------|-------------|
| 22 | `test_create_build_builds_data` | create_build builds correct data dict |

---

## E2E Test Plan

### test_full_e2e.py

#### CLI Subprocess Tests
| # | Test | Description |
|---|------|-------------|
| 1 | `test_help` | CLI --help returns exit code 0 |
| 2 | `test_json_flag` | --json flag produces valid JSON output |
| 3 | `test_connect_command` | connect command returns status info |
| 4 | `test_product_list_json` | product list returns JSON array structure |
| 5 | `test_project_list_json` | project list returns JSON array structure |
| 6 | `test_task_list_json` | task list with execution ID returns structure |
| 7 | `test_bug_list_json` | bug list returns JSON structure |
| 8 | `test_testcase_list_json` | testcase list returns JSON structure |
| 9 | `test_build_list_json` | build list returns JSON structure |
| 10 | `test_repl_help_in_repl` | REPL mode recognizes help command |
| 11 | `test_repl_quit` | REPL mode recognizes quit command |
| 12 | `test_full_workflow` | Full workflow: create project → create story → create task |

### Realistic Workflow Scenarios

1. **Agile Sprint Setup**
   - **Simulates**: Setting up a new sprint in ZenTao
   - **Operations chained**: create project → create story → create task → start task
   - **Verified**: Each step returns success status, IDs are returned

2. **Bug Report Lifecycle**
   - **Simulates**: Full bug tracking workflow
   - **Operations chained**: create bug → resolve bug → activate bug → close bug
   - **Verified**: Each state transition returns success

3. **Release Build Management**
   - **Simulates**: Managing release builds
   - **Operations chained**: create build → list builds → get build → delete build
   - **Verified**: Build appears in list, details retrievable

---

## Notes

- Unit tests use mocked backends to avoid requiring a real ZenTao server.
- E2E tests require `ZENTAO_URL`, `ZENTAO_USER`, `ZENTAO_PASSWORD` environment
  variables to be set. Tests will fail if these are not configured.
- Subprocess tests use `_resolve_cli` to find the installed command or fall back
  to `python -m`.

---

## 测试结果

### 执行环境
- Python 3.11.14, pytest-9.0.3
- 平台：darwin (macOS Apple Silicon)

### 测试统计
| 指标 | 数值 |
|------|------|
| 总计 | 47 |
| 通过 | 39 |
| 跳过 | 8（需要 ZENTAO_URL） |
| 失败 | 0 |
| 执行时间 | 0.12s |

### 通过率
- 单元测试: **37/37 通过 (100%)**
- CLI 基础测试: **2/2 通过 (100%)**
- 服务器集成测试: **0/8 跳过**（无 ZENTAO_URL）
