# HelloAgents Trip Planner

Multi-agent travel planner built with FastAPI, HelloAgents, Vue 3, TypeScript, and Amap MCP tools.

> This project is based on the HelloAgents framework's trip-planner tutorial code, with engineering improvements and open-source preparation by Zhisen Qiu. The original framework and tutorial project are attributed to the HelloAgents teaching team. This repository is licensed under CC BY-NC-SA 4.0.

## Overview

This project combines:

- A FastAPI backend
- The HelloAgents framework for agent orchestration
- Amap MCP tools for map-related capabilities
- A Vue 3 + TypeScript frontend for trip planning and result visualization

The application generates travel plans that include attractions, weather, hotels, meals, and map-based presentation.

## Feature Snapshot

- Multi-agent trip planning workflow (Attraction / Weather / Hotel / Planner pipeline)
- Amap MCP integration for travel-related map tools
- Attraction image loading through Unsplash
- Result page with daily itinerary, map view, export actions, and lightweight local editing

## Tech Stack

### Backend

- Python
- FastAPI
- HelloAgents
- Amap MCP server
- Pydantic

### Frontend

- Vue 3
- TypeScript
- Vite
- Ant Design Vue
- Axios
- AMap JavaScript API

## Repository Structure

```text
helloagents-trip-planner/
|- backend/
|  |- app/
|  |  |- agents/
|  |  |- api/
|  |  |- models/
|  |  `- services/
|  |- .env.example
|  |- .gitignore
|  |- requirements.txt
|  `- run.py
|- frontend/
|  |- src/
|  |  |- services/
|  |  |- types/
|  |  `- views/
|  |- .env.example
|  |- .gitignore
|  |- package.json
|  `- vite.config.ts
|- docs/
|- .editorconfig
|- .gitattributes
|- .gitignore
|- CODE_OF_CONDUCT.md
|- CONTRIBUTING.md
|- LICENSE
|- SECURITY.md
`- README.md
```

## Prerequisites

- Python 3.10+
- Node.js 18+ recommended
- Amap API credentials
- An OpenAI-compatible LLM API credential
- Access to the `hello_agents` framework package or source

## Setup Notes

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Then fill in the required values in `backend/.env`.

Important: the backend also requires the `hello_agents` package to be available in the active Python environment. This repository does not currently bundle that framework source.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
```

Then fill in the required values in `frontend/.env`.

## Local Run Commands

Backend:

```bash
cd backend
python run.py
```

Frontend:

```bash
cd frontend
npm run dev
```

By default the frontend runs on `http://localhost:5173` and the backend runs on `http://localhost:8000`.

## Environment Variables

### Backend

See `backend/.env.example`.

Important keys include:

- `AMAP_API_KEY`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL_ID`
- `UNSPLASH_ACCESS_KEY`
- `UNSPLASH_SECRET_KEY`

### Frontend

See `frontend/.env.example`.

Important keys include:

- `VITE_API_BASE_URL`
- `VITE_AMAP_WEB_KEY`
- `VITE_AMAP_WEB_JS_KEY`

## Open Collaboration Files

This repository includes:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [NOTICE.md](NOTICE.md)
- [SECURITY.md](SECURITY.md)
- [docs/GITHUB_OPEN_SOURCE_CHECKLIST.md](docs/GITHUB_OPEN_SOURCE_CHECKLIST.md)
- [docs/EXTERNAL_DEPENDENCIES.md](docs/EXTERNAL_DEPENDENCIES.md)

## Known Limitations

- The backend depends on the external `hello_agents` framework package or source, which is not included here as repository source code.
- Some backend integrations and workflow details still require follow-up work.
- No CI pipeline is included yet.
- See [docs/ROADMAP.md](docs/ROADMAP.md) for a detailed analysis and improvement plan.

## Publishing Notes

Before the first public push, review:

- `docs/GITHUB_OPEN_SOURCE_CHECKLIST.md`
- `docs/EXTERNAL_DEPENDENCIES.md`

## Contributing

Issues and pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

This work is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

Original work by the HelloAgents teaching team. Derivative improvements by Zhisen Qiu. See [NOTICE.md](NOTICE.md) for attribution details.
