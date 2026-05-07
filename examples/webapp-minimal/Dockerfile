# syntax=docker/dockerfile:1.7
# CFP-128 / ADR-033 — webapp-minimal example Docker fixture
# multi-stage build (deps / builder / runner) — Node webapp 기준
#
# 본 Dockerfile = consumer adoption 시 출발점 (template).
# 실제 webapp stack (FastAPI / Flask / Rails / Express 등) 에 맞게 수정 필요.

#─── Stage 1: deps ───
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

#─── Stage 2: builder ───
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

#─── Stage 3: runner ───
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
USER node
HEALTHCHECK --interval=30s --timeout=3s --retries=3 --start-period=10s \
  CMD wget -qO- http://localhost:3000/health || exit 1
EXPOSE 3000
CMD ["node", "dist/server.js"]
