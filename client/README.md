# Tensa Client

Frontend for Tensa, a self-hosted, ad-free media toolkit: paste a link (or upload a
file) to download video, extract audio, convert, transcribe, or grab a playlist.

Single-page app (Next.js 16 App Router) with an ember-tinted dark UI. All backend
access flows through Server Actions → the FastAPI API; live download progress
streams directly to the browser over SSE.

## Setup

```bash
bun install
```

## Develop

```bash
bun run dev    # http://localhost:3000
bun run lint   # Biome
```

## Layout

```
src/
├── app/          # layout.tsx + page.tsx (the single page) + globals.css
├── components/   # UI components (flat) + ui/ shadcn/Radix primitives
├── hooks/        # useJobManager, useSSE, useJobReconcile, useUrlPanel, …
├── lib/          # actions/ (Server Actions), api-client, stream, utils
├── constants/    # api, modes, sse, options
└── types/        # shared types (job.ts)
```

**Data flow**: component → hook (React Query) → Server Action (`lib/actions/*`) →
`lib/api-client` → API. The SSE progress stream and file downloads are the
sanctioned direct browser→API exceptions (see `lib/stream.ts`).

## Runtime config

The browser-facing API base is resolved at runtime, not baked into the build.
`app/layout.tsx` reads `PUBLIC_API_URL` on the server and injects it as
`window.__TENSA_API_BASE__`; `getApiBase()` (`constants/api.ts`) reads it in the
browser. The Next server itself reaches the API via `INTERNAL_API_URL`.

## Tech

- Next.js 16 (App Router) · React 19 + React Compiler
- TanStack Query v5
- Tailwind CSS v4 · shadcn/ui + Radix
- GSAP + ogl (hero animation) · next-themes
- Bun
