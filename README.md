# Spring

Backend API for a placement helper system for NIT Kurukshetra. Built with Elysia + Bun + Drizzle + PostgreSQL.

## Prerequisites

- [Bun](https://bun.sh)
- [Docker](https://docs.docker.com/get-docker/)

## Setup

```bash
# install dependencies
bun install

# create env file and fill in Google OAuth credentials
cp .env.example .env

# start postgres
docker compose up -d

# run migrations
bun run db:migrate

# start dev server (with hot reload)
bun run dev
```

Server runs at http://localhost:3000

## Scripts

| Command | Description |
|---|---|
| `bun run dev` | Start dev server with hot reload |
| `bun run db:generate` | Generate migration after schema changes |
| `bun run db:migrate` | Apply pending migrations |
| `bun run db:studio` | Open Drizzle Studio GUI |
