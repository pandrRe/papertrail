FROM oven/bun:1 AS base
WORKDIR /app

FROM base AS install
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile --production

FROM base AS release
COPY --from=install /app/node_modules ./node_modules
COPY server ./server
COPY package.json ./

USER bun
EXPOSE 8888
ENTRYPOINT ["bun", "run", "server/index.ts"]
