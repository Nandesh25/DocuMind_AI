# DocuMind AI — Frontend

Angular 19 SPA for the Enterprise Document Intelligence Platform. Built with
**standalone components**, **route-level lazy loading**, **Angular Material (M3)**,
and a **feature-based architecture**.

## Stack
- Angular 19 · TypeScript · Angular Material · SCSS
- Signals for state, functional guards & HTTP interceptors

## Architecture
```
src/app/
├── core/        # singletons: guards, interceptors, services, layout shell
├── shared/      # reusable components, pipes, Material barrel
├── features/    # lazy-loaded bounded contexts
│   ├── auth/        (login, register)
│   ├── workspaces/  (list, create)
│   ├── documents/   (list, upload)
│   ├── chat/        (RAG assistant)
│   ├── search/      (semantic search)
│   ├── settings/    (profile, security, appearance)
│   └── dashboard/
├── models/      # domain data shapes
└── interfaces/  # API/contract shapes
```

Each `features/*` module ships as its own lazy chunk via `loadChildren` /
`loadComponent`, and depends only on `core`, `shared`, `models`, `interfaces`.

## Setup
```bash
npm install
npm start                 # dev server at http://localhost:4200
```
The dev server calls the backend at `http://localhost:8000/api/v1`
(see `src/environments/environment.ts`).

## Build
```bash
npm run build             # production build -> dist/documind
```

## Docker
```bash
docker build -t documind-frontend .
docker run -p 8080:80 documind-frontend
```
`nginx.conf` serves the SPA and proxies `/api/` to the backend service.

## Path aliases
`@core/*`, `@shared/*`, `@features/*`, `@models/*`, `@interfaces/*`, `@env/*`
(configured in `tsconfig.json`).
