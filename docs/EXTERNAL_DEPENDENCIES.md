# External Dependencies Note

This repository is a copied project workspace prepared for public publication on GitHub. It is not yet a fully self-contained backend application.

## Current External Framework Dependency

The backend imports the `hello_agents` package directly:

- `backend/app/agents/trip_planner_agent.py`
- `backend/app/services/amap_service.py`
- `backend/app/services/llm_service.py`

At the moment, the `hello_agents` framework source is not included in this repository.

The repository does declare this dependency in `backend/requirements.txt`:

- `hello-agents[protocols]>=0.2.4,<=0.2.9`

That means:

- The intended dependency path appears to be package-based installation rather than a local source checkout.
- Because this audit did not install or run the project, the package-based installation flow should still be verified in a clean environment before broad publication.
- Any CI pipeline added before this is verified may need extra setup and may be confusing for external contributors.

## Other Important Runtime Dependencies

The project also expects access to:

- An OpenAI-compatible LLM API
- Amap-related credentials and MCP tooling
- Optional Unsplash credentials for attraction images

These are documented through the repository's `.env.example` files and `README.md`.

## Recommended Options Before Broader Collaboration

Choose one of these approaches before inviting outside contributors to run the project:

1. Keep the package-based approach and verify that `hello-agents[protocols]` is sufficient in a clean environment.
2. Publish `hello_agents` as a separate public repository and document source-based installation steps clearly.
3. Vendor `hello_agents` into this repository using a submodule or subtree.
4. Package and publish `hello_agents` so contributors can install it with a normal package manager flow if the current package path is not enough.

## Minimum Acceptable Public-State Documentation

If you do not resolve the dependency immediately, keep the following visible:

- An honest note in `README.md`
- A publishing caveat in `docs/GITHUB_OPEN_SOURCE_CHECKLIST.md`
- Clear contribution expectations in `CONTRIBUTING.md`

That is enough for a transparent source release, but it is not yet enough for a fully verified contributor onboarding experience.
