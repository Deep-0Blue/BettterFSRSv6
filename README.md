# BettterFSRS Clay Dashboard

Localhost dashboard in **TypeScript** + **HTML** with a Times New Roman, warm clay aesthetic.

## Run on localhost

```bash
cd dashboard
npm install
npm run dev
```

Opens **http://localhost:5173** (Vite dev server).

## Build for static hosting

```bash
npm run build
npm run preview
```

Output is in `dist/`.

## Stack

- Vite + TypeScript
- No framework — vanilla TS renders the UI
- Clay/neomorphic CSS in `src/styles/clay.css`

Benchmark buttons currently show **demo metrics** until wired to the Python `bettter_fsrs` CLI or an API.
