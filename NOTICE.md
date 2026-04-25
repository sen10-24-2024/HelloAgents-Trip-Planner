# NOTICE

## Attribution

This project is based on the HelloAgents trip-planner tutorial code created by the HelloAgents teaching team. The original framework and tutorial project are used under the CC BY-NC-SA 4.0 license.

## Contributions

### Upstream (HelloAgents Teaching Team)

- FastAPI backend scaffold and project structure
- Multi-agent orchestration design (Attraction / Weather / Hotel / Planner pipeline)
- HelloAgents framework integration (`SimpleAgent`, `MCPTool`, `ToolRegistry`)
- Vue 3 frontend scaffold (Home page, Result page, map visualization)
- Amap MCP integration architecture
- Unsplash image service

### Derivative Improvements (Zhisen Qiu)

- Root-level `.gitignore`, `.gitattributes`, `.editorconfig`
- Frontend `.gitignore` — added `.env` exclusion
- `requirements.txt` — added missing `requests` dependency
- `backend/app/config.py` — removed dead code (hardcoded HelloAgents path), replaced with `load_dotenv()` + environment variable approach
- `backend/app/api/routes/trip.py` — replaced `traceback.print_exc()` with `logger.exception()`
- `backend/app/agents/trip_planner_agent.py` — replaced `traceback.print_exc()` with `logger.exception()`
- `frontend/src/views/Result.vue` — replaced hardcoded `localhost:8000` with `VITE_API_BASE_URL` environment variable
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- `.github/` issue and pull request templates
- `docs/EXTERNAL_DEPENDENCIES.md`, `docs/GITHUB_OPEN_SOURCE_CHECKLIST.md`, `docs/ROADMAP.md`
- This `NOTICE.md` and the repository `LICENSE`

## License

Both the upstream work and derivative improvements in this repository are distributed under CC BY-NC-SA 4.0. See [LICENSE](LICENSE) for details.
