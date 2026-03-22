FROM oven/bun:1 AS base
WORKDIR /app

# Install dependencies
FROM base AS deps
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile --production

# Build / prepare
FROM base AS runner
COPY --from=deps /app/node_modules ./node_modules
COPY package.json bun.lockb ./
COPY src ./src
COPY drizzle ./drizzle
COPY drizzle.config.ts ./
COPY problems ./problems

EXPOSE 3001

CMD ["bun", "run", "src/index.ts"]
