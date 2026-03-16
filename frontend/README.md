# Frontend

React + TypeScript web client for document upload, review workspace, PDF/source inspection, and structured field editing.

## Scope

- UI for upload, list/status, and review flows
- Structured data editor and validation feedback
- PDF/source panels and review ergonomics
- Frontend unit tests and Playwright end-to-end tests

## Main folders

- src: application source code
- e2e: Playwright tests
- public runtime/config files: index.html, nginx.conf, vite config, tailwind config

Generated folders (do not treat as source):

- dist
- coverage
- playwright-report
- test-results

## Run options

Preferred: run the whole stack from repository root.

- Evaluation mode:
  - docker compose up --build
- Dev mode (hot reload):
  - docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

Local frontend-only workflow (from frontend folder):

- Install dependencies:
  - npm ci
- Start dev server:
  - npm run dev
- Production build:
  - npm run build
- Preview build:
  - npm run preview

## Quality and tests

From frontend folder:

- Lint + typecheck:
  - npm run lint
- Unit tests:
  - npm run test
- Coverage:
  - npm run test:coverage
- E2E smoke/core:
  - npm run test:e2e
- E2E extended:
  - npm run test:e2e:all

## Notes

- Design-system validation is wired via npm run check:design-system.
- For canonical architecture, contracts, and evaluator guidance, follow the repository root README and wiki docs.
