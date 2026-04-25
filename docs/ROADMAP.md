# HelloAgents Trip Planner 项目分析与实施路线图

> 本文档基于静态代码分析生成，未运行项目，所有结论需结合实际运行验证。文中带有【待验证】标记的结论，表示从静态代码路径可以高概率推断，但仍需以实际运行结果最终确认。

## 文档元信息

| 字段 | 内容 |
| --- | --- |
| 文档标题 | HelloAgents Trip Planner 项目分析与实施路线图 |
| 文档版本 | v1.0 |
| 生成日期 | 2026-04-24 |
| 项目路径 | 本仓库根目录 |
| 框架参考路径 | HelloAgents 框架（`hello_agents` Python 包） |
| 分析方式 | 静态代码分析 |
| 分析范围 | `backend/app/agents/trip_planner_agent.py`、`backend/app/services/llm_service.py`、`backend/app/services/amap_service.py`、`backend/app/services/unsplash_service.py`、`backend/app/config.py`、`backend/app/models/schemas.py`、`backend/app/api/routes/`、`frontend/src/`、`README.md`，以及 HelloAgents 框架中的 `agents/simple_agent.py`、`agents/react_agent.py`、`agents/function_call_agent.py`、`core/agent.py`、`core/llm.py`、`tools/base.py`、`tools/registry.py`、`tools/builtin/protocol_tools.py`、`tools/builtin/mcp_wrapper_tool.py`、`protocols/mcp/client.py` |

## 目录

- [A. 已实现功能清单](#a-已实现功能清单)
- [B. 架构与技术选型深度分析](#b-架构与技术选型深度分析)
  - [B1. 后端架构模式](#b1-后端架构模式)
  - [B2. Agent 协作机制深度分析](#b2-agent-协作机制深度分析)
  - [B3. 工具调用机制深度剖析](#b3-工具调用机制深度剖析)
  - [B4. MCP 集成分析](#b4-mcp-集成分析)
  - [B5. HelloAgentsLLM 统一抽象层评价](#b5-helloagentsllm-统一抽象层评价)
  - [B6. 前后端通信分析](#b6-前后端通信分析)
- [C. 现存问题与缺陷](#c-现存问题与缺陷)
  - [C0 — 致命级](#c0--致命级)
  - [C1 — 严重级](#c1--严重级)
  - [C2 — 一般级](#c2--一般级)
  - [C3 — 优化级](#c3--优化级)
- [D. 功能补充与优化建议](#d-功能补充与优化建议)
- [E. 任务执行顺序](#e-任务执行顺序)
- [F. 风险评估与备选方案](#f-风险评估与备选方案)
- [附录：执行前置验证项](#附录执行前置验证项)
  - [附录1：执行前必须验证的关键假设](#附录1执行前必须验证的关键假设)
  - [附录2：5-7天时间窗口下的推荐执行策略](#附录25-7天时间窗口下的推荐执行策略)
  - [附录3：改动文件影响矩阵](#附录3改动文件影响矩阵)

## A. 已实现功能清单

| 功能点 | 实现位置（精确到文件名和关键行号） | 当前实现细节描述 | 质量评估（完整/部分实现/有缺陷/未实现） | 判定依据 |
| --- | --- | --- | --- | --- |
| 应用壳与前端路由 | `App.vue:1-27`，`main.ts:9-30` | 提供页头/页脚布局，注册 `Home` 与 `Result` 两个页面路由 | 完整 | 页面结构与路由闭环完整，未见空实现 |
| 首页旅行表单 | `Home.vue:20-161,219-228` | 收集城市、日期、交通、住宿、偏好、额外要求 | 完整 | 表单字段、默认值、校验规则均已落地 |
| 前端日期联动与天数计算 | `Home.vue:230-244`，`schemas.py:10-20` | 监听开始/结束日期，自动计算 `travel_days`，限制 1-30 天 | 部分实现 | 只有前端校验；后端 `TripRequest` 仍使用 `str` 且无日期一致性校验 |
| 提交计划、加载进度与跳转 | `Home.vue:246-314`，`api.ts:41-48` | 调 `/api/trip/plan`，显示进度，成功后跳转结果页 | 部分实现 | 进度条是 `setInterval` 模拟，不是后端真实步骤；后端 fallback 仍会显示“成功” |
| 结果页行程展示 | `Result.vue:38-287` | 展示概览、预算、每日行程、天气、地图、空状态 | 完整 | 展示链路完整，空状态也已处理 |
| 本地编辑行程 | `Result.vue:354-415` | 支持进入编辑、保存、取消、删除景点、调整顺序 | 部分实现 | 只写回 `sessionStorage`，不回写后端，也不重算预算/路线 |
| 景点图片获取与回退图 | `unsplash_service.py:7-85`，`poi.py:89-128`，`Result.vue:427-490` | 后端查 Unsplash，前端加载失败时显示占位图 | 部分实现 | `requests` 未在依赖声明；即使没取到图也返回 success |
| 地图可视化 | `Result.vue:832-956` | 加载高德 JS API，绘制标记、信息窗、折线 | 部分实现 | 画的是前端 `Polyline` 直线，不是真实路径规划结果 |
| 导出 PNG/PDF | `Result.vue:496-787` | 用 `html2canvas + jsPDF` 导出图片/PDF | 部分实现 | 依赖 DOM 克隆与地图 canvas 快照，鲁棒性一般，且导出代码重复较多 |
| FastAPI 启动、根路由与全局健康检查 | `api/main.py:11-87` | 注册 CORS、路由、根路径、`/health`、文档地址 | 完整 | API 壳层完整，Swagger/ReDoc 可用 |
| 配置加载与校验 | `config.py:9-110` | 加载 `.env`、校验高德/LLM 配置、打印配置 | 有缺陷 | `helloagents_env` 拼接到 `...code/chapter13/HelloAgents/.env`，与 HelloAgents 框架实际路径不符 |
| LLM 单例服务 | `llm_service.py:10-36` | 单例化 `HelloAgentsLLM()`，打印 provider/model | 完整 | 功能单一明确，可正常作为统一入口 |
| 多智能体编排初始化 | `trip_planner_agent.py:155-220`，`simple_agent.py:325-342`，`registry.py:20-45`，`protocol_tools.py:57-65,113-124,314-337` | 初始化共享 `MCPTool`、4 个 `SimpleAgent` | 有缺陷【待验证】 | 项目依赖 `SimpleAgent.add_tool()`，但其注册逻辑不识别 `MCPTool.auto_expand`；静态推断 `amap_maps_*` 子工具可能根本没注册 |
| 景点搜索 Agent | `trip_planner_agent.py:13-33,241-245,280-291` | 通过偏好搜索景点，并把结果传给 Planner | 有缺陷【待验证】 | 只取 `preferences[0]`；系统 prompt、增强 prompt 与用户 query 三重工具引导叠加 |
| 天气查询 Agent | `trip_planner_agent.py:35-54,247-251,140-141` | 查询城市天气后传给 Planner | 部分实现 | 只传城市，不传旅行日期区间；但 Planner 要求 `weather_info` 覆盖每天 |
| 酒店推荐 Agent | `trip_planner_agent.py:56-73,253-257` | 搜索酒店并传给 Planner | 部分实现 | prompt 说“根据城市和景点位置推荐”，但实际 query 只有城市+住宿偏好 |
| Planner Agent 与 JSON 解析 | `trip_planner_agent.py:75-152,293-368` | 汇总上游字符串结果，要求输出 JSON，再解析成 `TripPlan` | 部分实现 | 上游数据是原始字符串拼接；解析时用代码块/大括号贪婪提取，无 repair 机制 |
| 备用 fallback 行程 | `trip_planner_agent.py:370-414` | LLM/工具失败时伪造一个通用行程 | 有缺陷 | 坐标硬编码为近北京值，且缺预算/天气/酒店完整性，但上层仍可能返回 success |
| 旅行规划 API 与专用健康检查 | `trip.py:14-85` | `POST /api/trip/plan` 与 `/trip/health` | 有缺陷 | `plan` 路由会把 fallback 包成成功响应；`/trip/health` 访问不存在的 `agent.agent` |
| 地图服务封装与 Map API | `amap_service.py:12-268`，`map.py:17-162` | 提供 POI、天气、路线、地理编码、健康检查 | 有缺陷 | `search_poi/get_weather/plan_route/geocode` 都是 TODO/空返回；`/route` 还会把 `{}` 塞进 `RouteInfo` |
| POI 详情/搜索/图片 API | `poi.py:19-128`，`amap_service.py:219-254` | 支持详情、搜索、图片接口 | 部分实现 | 详情接口靠 `re.search(r'\{.*\}')` 贪婪抓 JSON；搜索接口依赖空实现的 `search_poi()` |

## B. 架构与技术选型深度分析

### B1. 后端架构模式

- 当前是典型的“路由层 -> 编排/服务层 -> 框架/MCP -> Pydantic 模型”单体分层：`trip.py/map.py/poi.py` 负责 HTTP 入口，`trip_planner_agent.py` 负责编排，`amap_service.py/llm_service.py` 负责外部能力封装，`schemas.py` 负责输入输出契约。
- 全局单例模式用得很多：`settings`（`config.py:59-65`）、`_llm_instance`（`llm_service.py:6-30`）、`_multi_agent_planner`（`trip_planner_agent.py:418-428`）、`_amap_service`（`amap_service.py:257-268`）。优点是 demo 场景接线简单、冷启动少；缺点是带状态对象一旦进入多请求场景就会污染上下文，尤其 `Agent._history` 是实例级可变状态（`agent.py:19-40`）。
- 依赖注入方式是“模块级 getter + 全局对象”，而不是 FastAPI `Depends`。优点是代码直白；缺点是测试替换困难、请求级生命周期无法表达、并发隔离差。

### B2. Agent 协作机制深度分析

- 当前实现的数据流是：`Home.vue` 表单提交 -> `POST /api/trip/plan`（`trip.py:20-52`）-> `get_trip_planner_agent()` 取单例编排器（`trip_planner_agent.py:421-428`）-> 依次执行 attraction / weather / hotel / planner（`trip_planner_agent.py:222-267`）-> `_parse_response()` 转 `TripPlan`（`trip_planner_agent.py:327-368`）-> 前端写入 `sessionStorage`（`Home.vue:293-300`）-> `Result.vue` 读出并渲染（`Result.vue:329-338`）。
- 职责边界表面清晰，但并不完全一致。景点、天气、酒店、Planner 四个角色是分开的；但酒店 prompt 声称依赖“景点位置”（`trip_planner_agent.py:56-57`），实际代码并未把 attraction 结果结构化传给 hotel query（`trip_planner_agent.py:253-257`），说明“概念边界”和“实际数据依赖”有偏差。
- Agent 之间的信息传递方式是“原始字符串拼接”：Planner query 直接把 `attraction_response/weather_response/hotel_response` 塞进 prompt（`trip_planner_agent.py:293-325`）。优点是实现快、与框架低耦合；缺点是没有中间 schema、无法做类型校验、工具错误文本也会被当成业务输入继续传递。
- 一个额外隐患是上下文会在 Agent 实例内累积。`SimpleAgent.run()` 每次会把历史消息重新拼进请求（`simple_agent.py:258-270`），因此当前编排器单例下，所谓“多 Agent 协作”实际还叠加了“跨请求隐式记忆”。

### B3. 工具调用机制深度剖析

- 当前项目使用的是 `SimpleAgent` 的文本工具调用范式，不是 OpenAI 原生 Function Calling。完整执行链路是：`SimpleAgent.run()` 构建系统消息与历史（`simple_agent.py:258-270`）-> LLM 输出文本（`simple_agent.py:285`）-> `_parse_tool_calls()` 用正则 `r'\[TOOL_CALL:([^:]+):([^\]]+)\]'` 抽取工具名与参数（`simple_agent.py:78-91`）-> `_parse_tool_parameters()` 把参数转 dict（`simple_agent.py:114-154`）-> `_convert_parameter_types()` 只做顶层基本类型推断（`simple_agent.py:156-211`）-> `_execute_tool_call()` 调 ToolRegistry（`simple_agent.py:93-112`）-> 再把工具结果作为一条“用户消息”塞回去要求模型继续回答（`simple_agent.py:301-306`）。
- 这套方案的优点是对模型要求低，任何能输出文本的 OpenAI-compatible 模型都能用；缺点是解析脆弱。具体体现在：全角标点、额外空格、嵌套 JSON、参数值中含逗号、参数值中含 `]`、模型把工具调用包进自然语言，都会影响 `simple_agent.py:80-154` 这套正则/分割逻辑。
- 与 OpenAI 原生 Function Calling 相比，`FunctionCallAgent` 会先把工具转成 JSON schema（`function_call_agent.py:62-126`），再走 `client.chat.completions.create(..., tools=..., tool_choice=...)`（`function_call_agent.py:226-243,279-312`），参数解析也直接 `json.loads(arguments)`（`function_call_agent.py:147-156`）。稳定性和可观测性都更强，但前提是底层 provider 真正支持 `tools` 参数。
- 从框架代码看，项目没有采用 `FunctionCallAgent` 不是因为框架不支持，而更像是一个“教学/兼容性优先”的选择：项目直接 import `SimpleAgent`（`trip_planner_agent.py:5`），prompt 也都是围绕 `[TOOL_CALL:...]` 写的；这属于架构选择。基于源码推断，作者大概率是为了保留“任何文本模型都能跑”的最低门槛，而不是技术上做不到。
- `max_tool_iterations=3` 来自 `SimpleAgent.run()` 默认值（`simple_agent.py:246`），项目调用时没有覆盖（`trip_planner_agent.py:244,250,256,262`）。对当前 attraction/weather/hotel 这类“一次工具调用就够”的子任务来说，3 并没有业务依据；反而因为 prompt 冲突，单个子 Agent 最坏可能走到 3 次工具轮询 + 1 次最终 LLM 调用（`simple_agent.py:283-317`），主要放大的是延迟和不确定性，不是可靠性。

### B4. MCP 集成分析

- 项目存在明显双链路：一条是编排器里直接给 Agent 挂 `MCPTool`（`trip_planner_agent.py:166-201`）；另一条是 `AmapService` 再包一层 `MCPTool.run({"action":"call_tool", ...})`（`amap_service.py:27-34,71-79,105-111,173-177`）。这导致同一高德能力有两套命名体系：Agent prompt 用 `amap_maps_*`，Service 用裸 `maps_*`。
- `auto_expand=True` 的理论机制是：`MCPTool` 初始化后发现服务器工具并设置前缀 `amap_`（`protocol_tools.py:113-124`），`get_expanded_tools()` 再把每个 MCP 工具包成 `MCPWrappedTool`（`protocol_tools.py:314-337`，`mcp_wrapper_tool.py:31-60,100-118`）。但在当前项目实际使用的 `SimpleAgent.add_tool()` 路径里，这个展开机制静态上并没有真正接上。
- 原因是：`FunctionCallAgent.add_tool()` 显式识别 `tool.auto_expand`（`function_call_agent.py:342-356`）；`SimpleAgent.add_tool()` 只是把 tool 交给 `ToolRegistry.register_tool()`（`simple_agent.py:325-342`），而后者只在 `tool.expandable=True` 时才展开（`registry.py:20-37`）。`MCPTool` 使用的是 `auto_expand` 而不是 `expandable`（`protocol_tools.py:57-65,113-124`）。这会让 prompt 里的 `amap_maps_text_search` 与实际注册工具名发生冲突。【待验证】
- stdio 启动外部进程的风险点也很明显：项目两处都用 `server_command=["uvx","amap-mcp-server"]`（`trip_planner_agent.py:171-173`，`amap_service.py:31-33`）；而 `MCPTool.run()` 每次调用都会 `async with MCPClient(...)` 新建连接（`protocol_tools.py:356-461`），`MCPClient` 进入上下文时会连接/启动底层 transport（`client.py:198-213`）。当前没有显式超时、重试、熔断或健康探针，进程挂起时会直接阻塞同步调用链。

### B5. HelloAgentsLLM 统一抽象层评价

- `HelloAgentsLLM` 的 `SUPPORTED_PROVIDERS` 一共声明了 11 个 provider 标识：`openai/deepseek/qwen/modelscope/kimi/zhipu/ollama/vllm/local/auto/custom`（`llm.py:9-21`）。严格说其中 `auto` 和 `custom` 更像模式而不是具体厂商。
- provider 自动检测优先级非常明确：先查特定环境变量（`llm.py:88-115`），再看 API Key 格式（`llm.py:116-134`），再看 `base_url`（`llm.py:135-170`），最后退回 `auto`（`llm.py:171-172`）；之后 `_resolve_credentials()` 再按 provider 决定 key/base_url（`llm.py:174-230`），`_get_default_model()` 给默认模型（`llm.py:240-283`）。
- 这层抽象的工程价值很高：项目 `get_llm()` 基本不需要写任何 provider 分支，只要 `HelloAgentsLLM()` 即可（`llm_service.py:19-24`）。对课程项目、企业 PoC 和多环境部署都很友好。
- 但它也有代价：provider 识别偏“全局环境驱动”。例如只要机器上存在 `OPENAI_API_KEY`，`_auto_detect_provider()` 就会优先判成 `openai`（`llm.py:99-100`），即便你实际想用别的 `LLM_BASE_URL`。这不会立刻让调用失败，但会影响 provider 标签、默认模型和排障体验。

### B6. 前后端通信分析

- 当前通信全貌是：前端主要通过 Axios 调 REST JSON（`api.ts:4-48`），规划结果写入 `sessionStorage`（`Home.vue:293-300`），结果页从 `sessionStorage` 读取（`Result.vue:329-338`）；图片又单独用原生 `fetch` 访问 `/api/poi/photo`（`Result.vue:435-440`）；地图本身直接走高德 JS API（`Result.vue:835-849`）。
- 因为没有 SSE/WebSocket，前端无法拿到“真实的 Agent 中间步骤”，所以首页只能做假进度（`Home.vue:257-272`）。而框架层其实具备流式 LLM 能力（`llm.py:285-343`），只是当前项目没有用。
- Axios 与原生 `fetch` 混用造成了一致性问题：`api.ts` 已经支持 `VITE_API_BASE_URL` 和统一拦截器（`api.ts:4-35`），但 `Result.vue` 仍然把图片请求硬编码为 `http://localhost:8000`（`Result.vue:435`），直接绕过了 `vite.config.ts:13-20` 里现成的 `/api` 代理。
- 结果页地图与导出功能大多是纯前端行为，不经过后端。这让展示层很灵活，但也意味着前端承受了更多状态、快照和兼容性问题。

## C. 现存问题与缺陷

### C0 — 致命级

- 跨请求上下文串话：`_multi_agent_planner` 是全局单例（`trip_planner_agent.py:418-428`），而 `Agent` 基类把历史存在实例字段 `_history`（`agent.py:19-24`）；`SimpleAgent.run()` 每次会读取旧历史（`simple_agent.py:266-267`）并在结束后追加新历史（`simple_agent.py:320-321`）。这在多次请求下会把前一个用户的问题带进后一个用户的规划。
- “伪成功 fallback”：`plan_trip()` 任意异常都返回 `_create_fallback_plan()`（`trip_planner_agent.py:274-278`），`_parse_response()` 解析失败也回退（`trip_planner_agent.py:365-368`）；但 API 仍然固定返回 `success=True` 和“旅行计划生成成功”（`trip.py:48-52`）。更严重的是 fallback 坐标是伪造的（`trip_planner_agent.py:392-396`），数据不可信却被包装成成功。

### C1 — 严重级

- `SimpleAgent + MCPTool` 命名空间不匹配，核心子工具静态上大概率未注册：项目 prompt 强制 `amap_maps_text_search / amap_maps_weather`（`trip_planner_agent.py:20,42,63,290`），但 `SimpleAgent.add_tool()` 不识别 `MCPTool.auto_expand`（`simple_agent.py:325-342`，`registry.py:29-37`，`protocol_tools.py:113-124,314-337`）。这是当前主链路最危险的隐藏 bug。【待验证】
- `amap_service.py` 主方法都是 TODO/空返回：`search_poi()` 返回 `[]`（`amap_service.py:86-87`），`get_weather()` 返回 `[]`（`amap_service.py:115-116`），`plan_route()` 返回 `{}`（`amap_service.py:181-182`），`geocode()` 返回 `None`（`amap_service.py:212-213`）。这意味着 `/api/map/*` 大部分目前只是接口外壳。
- `/trip/health` 几乎必然报错：代码访问 `agent.agent.name` 和 `agent.agent.list_tools()`（`trip.py:78-79`），但 `MultiAgentTripPlanner` 没有 `agent` 字段。
- `config.py` 的 HelloAgents `.env` 路径拼错：`Path(__file__).parent.parent.parent.parent / "HelloAgents" / ".env"`（`config.py:14-16`）会落到 `...code/chapter13/HelloAgents/.env`，而不是 HelloAgents 框架的实际安装路径。
- `requirements.txt` 缺少 `requests`：`UnsplashService` 明确 `import requests` 并调用 `requests.get()`（`unsplash_service.py:3,35`），但依赖列表没有它（`requirements.txt:1-29`）。
- `/api/map/route` 的响应模型存在契约冲突：服务层返回 `{}`（`amap_service.py:181-182`），路由层却把它放进 `RouteResponse.data`（`map.py:128-131`），而 `RouteInfo` 要求 `distance/duration/route_type/description` 全部必填（`schemas.py:177-189`）。

### C2 — 一般级

- Prompt 双重甚至三重引导：attraction prompt 已内嵌工具格式（`trip_planner_agent.py:18-33`），`_build_attraction_query()` 又直接把 `[TOOL_CALL:...]` 塞进用户 query（`trip_planner_agent.py:280-291`），而 `SimpleAgent` 还会再自动注入一段通用工具说明（`simple_agent.py:41-76`）。这会诱导模型重复输出工具调用。
- Prompt 与 `SimpleAgent` 的“工具结果后回答”流程相冲突：三个子 Agent prompt 都要求“必须使用工具，不要直接回答”（`trip_planner_agent.py:15-17,37-39,58-60`），但 `SimpleAgent.run()` 在工具执行后会追加“请基于这些结果给出完整的回答”（`simple_agent.py:301-306`）。模型容易继续调用工具而不是收束回答。
- JSON 解析脆弱：`TripPlan` 解析时会从第一个 `{` 找到最后一个 `}`（`trip_planner_agent.py:349-353`），`POI 详情` 也用了贪婪正则 `\{.*\}`（`amap_service.py:245-248`）。一旦模型输出多个代码块或插入解释文本，就可能抓错 JSON。
- 前端硬编码 `localhost:8000`：`Result.vue:435` 直接写死图片接口地址，绕过 `api.ts:4-35` 和 `vite.config.ts:13-20`，部署到非本机地址会失效。
- `TripRequest` 无服务端日期一致性校验：模型只限制 `travel_days` 范围（`schemas.py:10-20`），但不校验 `end_date >= start_date`，也不校验 `travel_days` 是否与日期区间匹配。
- 异步路由里混用同步阻塞调用：`trip.py`、`map.py`、`poi.py` 都是 `async def`（如 `trip.py:20,69`），但内部调用的是同步 `agent.plan_trip()`、`AmapService` 和 `requests.get()`（`trip.py:44`，`map.py:44,83,120`，`unsplash_service.py:35`），会阻塞事件循环。
- 业务语义有缺口：景点搜索只吃第一个偏好（`trip_planner_agent.py:282-286`）；天气不按日期查；酒店不使用景点位置。主流程能“跑”，但协作质量与产品文案不一致。

### C3 — 优化级

- 0 测试覆盖：项目中未看到测试文件；前端 `package.json` 只有 `dev/build/preview`（`frontend/package.json:6-25`），后端依赖里也没有 `pytest`（`requirements.txt:1-29`）。
- README 与代码不一致：README 声称有 `components/` 目录（`README.md:50-57`），但实际前端只有 `views/services/types`；README 还写“Agent 获取路线规划”（`README.md:135-145`），实际主链路没有调用路线工具。
- 结构化日志缺失：后端核心几乎全部用 `print()`（如 `trip_planner_agent.py:160-217,233-277`，`api/main.py:38-65`），不利于 trace、聚合检索和线上排障。
- 双高德接入链路并存：编排器直连 MCPTool（`trip_planner_agent.py:166-201`）和 `AmapService` 二次封装（`amap_service.py:27-34,50-268`）同时存在，命名空间和错误语义都不统一。

## D. 功能补充与优化建议

### D1. 请求级上下文隔离与真实状态语义

- 具体要做什么：把 `MultiAgentTripPlanner` 改成“无状态 orchestrator + 每次请求新建 worker agents”或至少在入口显式 `clear_history()`，并给 `TripPlanResponse` 增加 `status/warnings`，让 fallback 变成 `partial` 而不是“成功”。
- 解决了 C 节中的哪些问题：直接解决 `C0` 的串话与伪成功。
- 为什么要做：互联网企业最看重这一点，因为 Agent 输出必须可追责；跨用户串话和伪成功都会直接损害系统可信度。
- 改动范围评估：主要在 `trip_planner_agent.py`、`trip.py`、`schemas.py`，约 120-180 行，不必改框架。
- 不做的风险：数据泄漏和不可置信结果继续存在，且越往后加功能越难补救。
- 预期效果：消除跨请求污染这一类 bug，并把失败显性化，避免“看起来成功但其实是兜底数据”。
- 替代方案及为什么不选替代方案：替代方案是仅在每次调用前后 `clear_history()`，但不建议把它作为唯一方案，因为它仍保留了隐式全局状态。

### D2. Prompt 工程重写与工具命名对齐

- 具体要做什么：重写 4 个 Agent prompt，去掉 attraction query 里的内嵌 `[TOOL_CALL]`、增加“每轮最多一次工具调用”“拿到工具结果后必须收束输出”“数据不足时返回空值而不是编造”等约束，并统一工具命名策略。
- 解决了 C 节中的哪些问题：解决 `C1` 中的工具名冲突风险，以及 `C2` 中的双重引导、JSON 不稳、业务语义不一致。
- 为什么要做：这是高 ROI 小改动，企业做 Agent 应用通常先稳 prompt 再谈复杂能力；当前问题很多不是“模型不行”，而是 prompt 与执行器在互相拉扯。
- 改动范围评估：改动主要在 `trip_planner_agent.py`，约 80-140 行；如选择补框架兼容则少量涉及 `simple_agent.py`。
- 不做的风险：会继续出现重复调用、幻觉补全、工具调用名不一致和解析失败。
- 预期效果：把单子 Agent 的平均 LLM 轮数从 2-4 次压到 1-2 次，减少格式波动。
- 替代方案及为什么不选替代方案：替代方案是直接迁移 `FunctionCallAgent`，但不建议把它作为第一步，因为要额外确认底层 provider 对 `tools` 的支持。

### D3. 完成 AmapService 并加 MCP 调用容错

- 具体要做什么：在 `amap_service.py` 增加 `run_mcp_call()`、`parse_poi_result()`、`parse_weather_result()`、`parse_route_result()`、`parse_geo_result()` 等函数，统一返回 typed schema，同时加 timeout、重试、失败分类与降级。
- 解决了 C 节中的哪些问题：解决 `C1` 的 TODO、空返回、无超时保护，以及部分 `C2` 的同步阻塞风险。
- 为什么要做：企业 Agent 项目对工具稳定性的要求通常高于“多智能体炫技”；外部工具层不稳，Planner 再强也只能输出垃圾进垃圾出。
- 改动范围评估：改动在 `amap_service.py`、`map.py`、`poi.py`、必要时 `schemas.py`，约 220-380 行，不一定要改框架。
- 不做的风险：地图能力永远停留在 demo 外壳，且请求可能被外部进程卡死。
- 预期效果：让 `/api/map/*` 从空接口变成真实可用接口，并把单次外部调用的尾延迟控制在设定超时内。
- 替代方案及为什么不选替代方案：替代方案是完全绕过 `AmapService` 继续让 Agent 自己查工具，但那样稳定性和可测试性都更差。

### D4. API 契约与输出质量控制

- 具体要做什么：把 `TripRequest.start_date/end_date` 改为 `date`，增加 `model_validator` 校验日期区间与 `travel_days` 一致性，同时为 Planner 增加更稳健的 JSON 提取/repair 策略，并为 map route 修正响应模型。
- 解决了 C 节中的哪些问题：解决 `C0` 的输出不可信问题，以及 `C2` 中的 JSON 解析脆弱、日期校验缺失、接口设计薄弱。
- 为什么要做：企业最怕“接口看着 200，内容全错”；后端需要成为真正的契约边界，而不是把风险转嫁给前端。
- 改动范围评估：改动在 `schemas.py`、`trip_planner_agent.py`、`trip.py`、`map.py`，约 140-220 行。
- 不做的风险：前端只能信任字符串，后端无法成为最终可信边界。
- 预期效果：把“解析失败直接伪造行程”改成“明确 partial/warning”，并减少因模型格式波动导致的失败。
- 替代方案及为什么不选替代方案：替代方案是仅靠前端校验，不建议，因为后端仍然是最终入口。

### D5. 多智能体编排升级为 DAG 并行而不是简单并行

- 具体要做什么：把当前串行流水线改成带依赖图的编排，MVP 只并行 `attraction + weather`，酒店在 attraction 之后执行，Planner 最后汇总。
- 解决了 C 节中的哪些问题：解决 `C2` 的延迟与错误隔离问题，也更符合“酒店依赖景点位置”的真实业务语义。
- 为什么要做：这更接近真实多智能体协作，而不是单线程顺序调用四个角色；同时能提升产品亮点。
- 改动范围评估：改动主要在 `trip_planner_agent.py`，MVP 约 180-280 行；若改框架 async 则会扩大到 300-450+ 行。
- 不做的风险：延迟始终线性增长，且“多智能体协作”卖点不足。
- 预期效果：在 happy path 下把前半段耗时从串行求和压到阶段最大值，而不是简单叠加。
- 替代方案及为什么不选替代方案：替代方案是全量 `asyncio` 改框架，或完全让 orchestrator 直连 `AmapService` 做确定性并发；更建议先做线程池/DAG 的 MVP。

### D6. 可观测性、真实进度与调试能力

- 具体要做什么：给每次规划生成 `run_id`、步骤 trace、耗时统计与警告列表，后端返回 debug 元数据，前端据此显示真实步骤进度而不是假进度。
- 解决了 C 节中的哪些问题：解决 `C2` 的假反馈、难排障，以及 `C3` 的结构化日志缺失。
- 为什么要做：企业 Agent 应用要上线，trace 和可调试性几乎是必需品；否则问题只会堆积在 `print()` 里。
- 改动范围评估：改动在 `trip.py`、`trip_planner_agent.py`、`api/main.py`、`api.ts`、`Home.vue`、`Result.vue`，约 160-300 行。
- 不做的风险：问题一旦出现就只能看散落的打印，无法快速判断卡在 LLM、MCP 还是前端展示。
- 预期效果：让用户看到“景点搜索/天气查询/酒店推荐/Planner 汇总”的真实状态，并提升定位效率。
- 替代方案及为什么不选替代方案：替代方案是直接上 WebSocket，不建议第一步就上，SSE 或普通 trace 返回更轻。

### D7. 测试、评估、文档与 GitHub 交付收口

- 具体要做什么：补 parser/validator 单测、API 契约测试、若干固定城市的金样例、README 与接口说明同步，以及部署/环境说明。
- 解决了 C 节中的哪些问题：解决 `C3` 的 0 测试和文档漂移。
- 为什么要做：企业和 GitHub 展示都需要“可复现”；没有测试和文档，项目很难持续演进。
- 改动范围评估：会跨 `backend/tests`、`frontend` smoke、`README.md`，总量约 400-700 行。
- 不做的风险：后续每次改 prompt 或工具解析都可能悄悄回归，且开源展示说服力不足。
- 预期效果：让项目达到“可写简历、可开源演示”的最低门槛。
- 替代方案及为什么不选替代方案：替代方案是仅手工回归，不建议，因为这类 Agent 项目回归成本会越来越高。

## E. 任务执行顺序

| 编码 | 任务名称 | 解决的 C 节问题 | 改动范围 | 新增/修改行数估算 | 必做/选做 | 依赖任务 | 务实工作量估算 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | 修复致命运行缺陷与状态语义 | C0-1, C1-2, C1-3, C1-4, C1-6 | `trip_planner_agent.py`、`trip.py`、`config.py`、`requirements.txt`、`schemas.py` | 120-180 | 必做 | 无 | 1-1.5 天 | 先处理串话、伪成功、健康检查、错误 env 路径、缺依赖、route 响应契约 |
| T2 | Prompt 工程与工具命名对齐 | C1-1, C2-1, C2-2, C2-6 | `trip_planner_agent.py`；如选框架补丁则少量涉及 `simple_agent.py` | 80-140 | 必做 | T1 | 0.5-1 天 | 高收益小改动，先把主链路提示词与工具名稳定下来 |
| T3 | 补全 `AmapService` 并加 MCP 容错 | C1-2, C1-6, C2-5 | `amap_service.py`、`map.py`、`poi.py`、必要时 `schemas.py` | 220-380 | 必做 | T1,T2 | 2-2.5 天 | 先修工具稳定性这个根因，再谈 Planner 输出质量 |
| T4 | API 契约与 Planner 输出质量控制 | C0-2, C2-2, C2-4 | `schemas.py`、`trip_planner_agent.py`、`trip.py`、`map.py` | 140-220 | 必做 | T3 | 1-1.5 天 | 把 date 校验、partial 语义、JSON repair、错误回传收紧 |
| T5 | 多智能体编排升级（DAG 并行 MVP） | C2-6, C3-4 | `trip_planner_agent.py`，必要时少量 `amap_service.py` | 180-280（MVP） | 选做 | T1-T4 | 2.5-3 天 | 不建议一上来全并行；先做 attraction+weather 并行、hotel 后置 |
| T6 | 结构化日志、trace 与 debug 能力 | C3-3，辅助 C0-C2 排障 | `trip.py`、`trip_planner_agent.py`、`api/main.py` | 160-240 | 选做 | T4 | 1-1.5 天 | 为真实进度与定位问题打基础 |
| T7 | 前端 API 一致性与真实进度展示 | C2-3, C2-5 | `api.ts`、`Home.vue`、`Result.vue`、必要时后端 trace 输出 | 180-260 | 选做 | T4,T6 | 1.5-2 天 | 统一 Axios/fetch，去掉硬编码 localhost，把假进度换成真实步骤 |
| T8 | 后端单测与 API 契约测试 | C3-1，辅助验证 T1-T4 | `backend/tests/*`、少量生产代码可测试化改造 | 250-400 | 选做 | T4 | 2-3 天 | 如果时间只有 5-7 天，这一步先不做全量，只做最关键 parser/validator/contract |
| T9 | 前端 smoke/E2E 与 Agent 评估样例 | C3-1, C3-2 | `frontend` 测试目录、评估样例数据、README 演示流程 | 250-350 | 选做 | T7,T8 | 2-3 天 | 从 0 到有 E2E+评估集，单独拆出来更务实 |
| T10 | README、部署说明与 GitHub 展示收口 | C3-2 | `README.md`、环境说明、接口说明、演示素材 | 60-120 | 选做 | T8/T9 | 0.5-1 天 | 最后收口，确保项目可公开展示 |

补充说明：

- 按“只有 5-7 天”的前提，必做集合建议是 `T1-T4`。这四项合计大约 `4.5-6.5 天`，刚好覆盖核心稳定性。
- `T5` 以后都建议放到第二阶段。若目标是“可上线 + 可写简历 + 可上 GitHub”，第二阶段优先顺序建议是 `T6 -> T8 -> T10 -> T7 -> T9 -> T5`，其中 `T5` 虽亮眼，但不是第一阶段必须。

## F. 风险评估与备选方案

- T5 的核心技术难点不在“写不写 `gather`”，而在依赖图和状态隔离。`SimpleAgent.run()` 是同步阻塞（`simple_agent.py:246-323`），`ReActAgent.run()` 也是同步阻塞（`react_agent.py:119-200`）；当前 Agent 还带 `_history` 可变状态（`agent.py:19-40`），不能直接共享进并发 worker。
- 难点二是依赖关系本身并非完全独立。当前代码里 hotel 虽然还没真正用 attraction 结果，但其 prompt 已经声明要基于景点位置（`trip_planner_agent.py:56-57`）；这意味着正确的未来编排更像 DAG：`attraction + weather` 并行，`hotel` 依赖 attraction，最后 `planner` 收口。
- 备选方案 A：项目层 `ThreadPoolExecutor` MVP。每个并发任务使用“独立 Agent + 独立 MCPTool/Service 实例”，加 per-future timeout 与错误隔离；优点是不改框架、上线快；缺点是线程阻塞依旧存在，且 stdio 外部进程启动成本高。
- 备选方案 B：框架层 async 化。为 `SimpleAgent/MCPTool/HelloAgentsLLM` 新增 async 调用链，再用 `asyncio.gather` 做 DAG 编排；优点是取消阻塞、可取消、可追踪；缺点是会改到 HelloAgents 框架共享代码，测试与回归成本明显更高。
- 备选方案 C：把外部 I/O 统一下沉到 `AmapService`，只让 Planner 保留 Agent 能力。优点是最稳、最易测试；缺点是“多智能体自主调用工具”的展示感会弱一些。
- 如果时间不够，T5 的最小可行版本建议是：不追求“三子任务全并行”，只把 `weather` 与 `attraction` 并行化，`hotel` 保持在 attraction 之后；如果连这一版都来不及，就先不并行，只补 timeout、错误隔离和 trace，让项目先稳定可用。

## 附录：执行前置验证项

### 附录1：执行前必须验证的关键假设

| 验证项 | 验证方法 | 如果成立的影响 | 对应任务调整 |
| --- | --- | --- | --- |
| MCPTool.auto_expand 是否真的断裂 | 在 `trip_planner_agent.py` 的 `__init__` 中 `add_tool` 后打印 `list_tools()`，观察输出是否为空或工具名是否为 `amap_maps_*` | 如果成立，说明三个核心 Agent 从未真正调通 MCP 工具，主链路可能一直失败 | T1 范围需扩大，增加 MCPTool 注册修复（给 MCPTool 加 `expandable` 属性或在 `SimpleAgent.add_tool` 中识别 `auto_expand`） |
| 前端硬编码 `localhost:8000` 的实际影响范围 | 搜索 `Result.vue` 中所有 `fetch/XMLHttpRequest` 调用，确认是否只有图片接口硬编码 | 如果不止一处硬编码，修复范围需扩大 | T7 需覆盖更多硬编码点 |

### 附录2：5-7天时间窗口下的推荐执行策略

- 第一阶段（必做）：`T1 -> T2 -> T3 -> T4`，预计 `4.5-6.5 天`。

第一阶段每个任务完成后的可运行验证点：

- T1 完成后项目应处于的状态：
  - 后端可以完成基础启动检查。
  - `/trip/health` 不再访问不存在字段。
  - `TripPlanResponse` 不再把 fallback 误报为纯成功。
  - 请求级上下文隔离策略已落地，至少不存在显式跨请求历史复用。
- T2 完成后项目应处于的状态：
  - 4 个 Agent 的 prompt 与工具命名策略一致。
  - attraction query 不再叠加额外 `[TOOL_CALL]` 指令。
  - 即使还没完全补完工具解析，主链路的 prompt 行为已经更可控。
- T3 完成后项目应处于的状态：
  - `/api/map/poi`、`/api/map/weather`、`/api/map/route` 至少具备结构化返回与基础错误处理。
  - `AmapService` 不再以 TODO/空返回为主。
  - MCP 调用具备基础 timeout/异常分类/降级能力。
- T4 完成后项目应处于的状态：
  - `TripRequest` 具备服务端日期与天数一致性校验。
  - Planner 输出解析失败时能返回明确状态或 warning，而不是静默伪造完整成功数据。
  - 核心 API 契约达到“可作为前后端稳定边界”的最低要求。

如果某一步超时，推荐裁剪策略如下：

- T1 超时：
  - 先保证串话问题与 `/trip/health` 修复落地。
  - `config.py` 路径与 `requirements.txt` 依赖修复必须同批完成。
  - 若 MCPTool 注册修复确认为框架级问题，可先做最小兼容补丁，不阻塞 T2。
- T2 超时：
  - 先完成 4 个 Agent 的工具名统一与 attraction prompt/query 去重。
  - Planner prompt 的细化优化可留到 T4 同批收口。
- T3 超时：
  - 优先完成 `search_poi()` 与 `get_weather()`，因为它们直接影响主链路。
  - `plan_route()` 和 `geocode()` 可先返回明确“暂不支持/部分可用”的结构化错误，不阻塞 T4。
- T4 超时：
  - 先落实 `TripRequest` 校验与 TripPlan 的 partial/warning 语义。
  - 更复杂的 JSON repair 策略可先保留为“单次重试 + 明确失败”，不要回退到伪成功。

### 附录3：改动文件影响矩阵

| 文件路径 | 涉及任务 | 改动类型 |
| --- | --- | --- |
| `backend/app/agents/trip_planner_agent.py` | T1,T2,T4,T5,T6 | 修改/重构 |
| `backend/app/api/routes/trip.py` | T1,T4,T6 | 修改 |
| `backend/app/api/routes/map.py` | T1,T3,T4 | 修改 |
| `backend/app/api/routes/poi.py` | T3 | 修改 |
| `backend/app/services/amap_service.py` | T3,T5 | 修改/补全 |
| `backend/app/models/schemas.py` | T1,T3,T4 | 修改 |
| `backend/app/config.py` | T1 | 修改 |
| `backend/requirements.txt` | T1 | 修改 |
| `backend/app/api/main.py` | T6 | 修改 |
| `frontend/src/services/api.ts` | T7 | 修改 |
| `frontend/src/views/Home.vue` | T7 | 修改 |
| `frontend/src/views/Result.vue` | T7 | 修改 |
| `backend/tests/test_schemas.py` | T8 | 新增 |
| `backend/tests/test_trip_api.py` | T8 | 新增 |
| `backend/tests/test_amap_service.py` | T8 | 新增 |
| `frontend/tests/home.spec.ts` | T9 | 新增 |
| `frontend/tests/result.spec.ts` | T9 | 新增 |
| `frontend/package.json` | T9 | 修改 |
| `README.md` | T10 | 修改 |
| HelloAgents 框架 `agents/simple_agent.py` | T1【条件性】,T2【条件性】 | 条件性修改 |
| HelloAgents 框架 `tools/registry.py` | T1【条件性】 | 条件性修改 |

