# GitHub Open Source Checklist

This document records the repository-level checks completed for publishing this project on GitHub and the manual steps still recommended before the first public push.

## Repository Audit Summary

Completed in this repository:

- Added a root `.gitignore` to avoid committing local virtual environments, IDE files, logs, and build outputs.
- Added `.gitattributes` and `.editorconfig` for more consistent collaboration.
- Added a root `LICENSE` file that matches the license statement already present in the project README.
- Added community files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and GitHub issue and pull request templates.
- Updated `README.md` to better reflect current repository status, setup guidance, and publishing caveats.
- Added the missing `requests` dependency in `backend/requirements.txt`.

Important repository findings:

- This copied project currently includes local development artifacts under `backend/.venv/` and `backend/.idea/`. They are now ignored and should not be committed.
- The codebase is not yet production-ready. The repository should be published with an honest status note rather than presented as a finished product.
- The backend and frontend already include `.env.example` files, which is good for open collaboration.
- The backend depends on the external `hello_agents` framework. The repository does not vendor that framework source, but `backend/requirements.txt` does declare `hello-agents[protocols]`. The remaining publish-time task is to verify that the package-based installation path is really sufficient for outside contributors.

## Open-Source Readiness Gaps

The repository is now much closer to a clean public GitHub baseline, but these items still matter:

1. Verify that the declared `hello-agents[protocols]` dependency is sufficient for a clean install, or document the fallback source-based setup.
2. Decide whether the repository should go public immediately or start private until the first stabilization pass is complete.
3. Add CI only after the external framework dependency story is clear.
4. Add screenshots or a short demo later if you want a stronger first impression on GitHub.

See [EXTERNAL_DEPENDENCIES.md](EXTERNAL_DEPENDENCIES.md) for the framework dependency note.

## Manual Checks Before First Push

1. Review `git status` and make sure no local environment artifacts are staged.
2. Confirm that the chosen license is really what you want for this repository.
3. Confirm how outside contributors are expected to obtain the `hello_agents` framework in practice.
4. Fill in repository metadata on GitHub:
   - Repository description
   - Topics
   - Website or demo link if available
5. Decide whether the repository should start as public or private.
6. Add a repository avatar or screenshots later if you want better presentation.

## Recommended GitHub Repository Settings

- Default branch: `main`
- Enable Issues
- Enable Discussions if you want design feedback before implementation
- Protect `main` after the first stable push if multiple contributors will collaborate

## Suggested Repository Description

Standalone multi-agent travel planner built with FastAPI, HelloAgents, Vue 3, and Amap MCP tools.

## Suggested Topics

- ai-agent
- multi-agent
- fastapi
- vue3
- typescript
- mcp
- amap
- travel-planner
- helloagents

## Suggested First Publish Flow

1. Create the remote repository on GitHub.
2. Add the remote:
   - `git remote add origin <your-repo-url>`
3. Review staged files carefully.
4. Create the first commit with a clear message.
5. Push the `main` branch.
6. Verify the rendered README, license, and issue templates on GitHub.
7. Re-check that the dependency story in `README.md` and `docs/EXTERNAL_DEPENDENCIES.md` is clear enough for outside readers.

## Recommended Follow-Up After Publishing

- Add screenshots of the UI.
- Sync the engineering roadmap document into this repository.
- Add tests and CI before inviting broader external contribution.
- Resolve the external `hello_agents` dependency in a contributor-friendly way.
