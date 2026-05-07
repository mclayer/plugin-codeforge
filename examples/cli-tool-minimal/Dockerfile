# syntax=docker/dockerfile:1.7
# CFP-128 / ADR-033 — cli-tool-minimal example Docker fixture
# distroless single-stage binary (smaller attack surface, Go example)
#
# 본 Dockerfile = consumer adoption 시 출발점 (template).
# 실제 cli stack (Go / Rust / Python pyinstaller / Node pkg 등) 에 맞게 수정 필요.

#─── Stage 1: builder ───
FROM golang:1.22-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /out/cli ./cmd/cli

#─── Stage 2: runner (distroless — minimal attack surface) ───
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /out/cli /cli
USER nonroot
ENTRYPOINT ["/cli"]
