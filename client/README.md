# Tensa Client

Next.js 16 frontend with shadcn/ui.

## Setup

```bash
bun install
```

## Run

```bash
bun run dev
```

Client runs at http://localhost:3000

## Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard |
| `/download` | Video download |
| `/playlist` | Playlist download |
| `/audio` | Audio extraction |
| `/transcribe` | Speech-to-text |
| `/convert` | Convert/trim/thumbnails |

## Architecture

```
src/
├── app/              # Pages only
├── features/         # Feature modules
│   ├── download/
│   │   ├── types.ts
│   │   ├── actions.ts
│   │   ├── hooks.ts
│   │   └── components/
│   └── ...
└── components/
    ├── shared/       # Shared components
    └── ui/           # shadcn primitives
```

**Data Flow**: `actions.ts` → `hooks.ts` (React Query) → Components

## Design

- **Theme**: Emerald green
- **Corners**: None (0px radius)
- **Style**: Minimal, no gradients

## Tech

- Next.js 16 (App Router)
- React Query (@tanstack/react-query)
- shadcn/ui + Tailwind CSS
- next-themes (dark mode)
