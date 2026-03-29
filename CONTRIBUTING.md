# Contributing to Optio

Thanks for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites

- **Node.js 22+**
- **pnpm 10+** (`npm install -g pnpm`)
- **Docker Desktop** with Kubernetes enabled

### Quick Start

```bash
git clone https://github.com/jonwiggins/optio.git
cd optio
pnpm install

# Start Kubernetes infrastructure
./scripts/setup-local.sh

# Start dev servers (API + Web)
pnpm dev
```

The API runs on http://localhost:4000 and the web UI on http://localhost:3000.

### Building the Agent Image

```bash
docker build -t optio-agent:latest -f Dockerfile.agent .
# Load into K8s containerd (Docker Desktop)
docker save optio-agent:latest | docker exec -i desktop-control-plane ctr -n k8s.io image import --digests -
```

## Project Structure

```
apps/api/     Fastify API server + BullMQ workers
apps/web/     Next.js web UI
packages/     Shared libraries (types, runtime, adapters, providers)
helm/         Production Helm charts
images/       Agent container Dockerfiles
k8s/          Local dev K8s manifests
```

## Development Workflow

### Commands

```bash
pnpm dev              # Start API + Web with hot reload
pnpm turbo typecheck  # Typecheck all packages
pnpm turbo test       # Run tests
pnpm format           # Format with Prettier
pnpm lint             # Lint with ESLint
```

### Planning And Execution Artifacts

Optio keeps delivery planning artifacts under `docs/`:

- `docs/roadmap/` for backlog and iteration bundles
- `docs/features/` for feature specs
- `docs/process/` for the repository workflow contract

For non-trivial changes, keep code updates synchronized with backlog, feature, and iteration docs. Use `make test` and `make check` before closing an iteration slice.
Use `make governance-check` when you want to run just the planning/documentation gate without the full project test suite.

### Local Hooks

- Husky is the default hook path in this repository.
- `pre-commit` runs `make hooks-pre-commit`.
- `pre-push` runs `make hooks-pre-push`.
- `.pre-commit-config.yaml` is optional and mirrors the governance checks for contributors who already use `pre-commit`.

### Database Changes

```bash
# Edit apps/api/src/db/schema.ts, then:
cd apps/api && npx drizzle-kit generate  # Generate migration
cd apps/api && npx drizzle-kit migrate   # Apply migration
```

### Adding a New API Route

1. Create the route handler in `apps/api/src/routes/`
2. Register it in `apps/api/src/server.ts`
3. Add the API client method in `apps/web/src/lib/api-client.ts`

## Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/). Commit messages are enforced by commitlint.

```
feat: add new feature
fix: fix a bug
docs: documentation changes
style: formatting, no code change
refactor: code change that neither fixes nor adds
perf: performance improvement
test: add or update tests
build: build system or dependencies
ci: CI configuration
chore: maintenance
```

## Pull Requests

1. Fork the repo and create a feature branch
2. For non-trivial work, keep the backlog, feature, and iteration artifacts in `docs/` synchronized with your code changes
3. Make your changes with tests
4. Ensure `make governance-check` and `make check` pass
5. Submit a PR using the template and link the relevant `BLG-###`, feature spec, and iteration bundle
6. Wait for CI to pass and a maintainer review

## Code Style

- TypeScript with strict mode
- ESM modules (`.js` extensions in imports)
- Prettier for formatting (runs on commit via Husky)
- Tailwind CSS v4 for styling
- Zustand for client state
- Zod for API validation
- Drizzle ORM for database

## License

MIT — see [LICENSE](./LICENSE)
