# syntax=docker/dockerfile:1.7
# CFP-2506 / ADR-033 Amendment 1 — rust-cli-minimal 로컬빌드 실증 Dockerfile (INV-2)
#
# 주의: 이것은 *production image 가 아니다*. Docker 마운트 빌드(R-3)와
#       `cargo check`(R-1, 링커 불요)가 컨테이너 안에서 동작함을 실증하는
#       fixture 다. 실제 배포 image 는 multi-stage + distroless 로 별도 구성한다
#       (cli-tool-minimal/Dockerfile 의 builder→distroless 패턴 참조).
#
# target triple 주의: 컨테이너 안 빌드는 x86_64-unknown-linux-gnu 로 빌드된다.
#   = build-verification proxy (타입·차용·플랫폼-비의존 로직 검증)이지
#     Windows PE 산출물 동등(artifact-equivalence)이 아니다. 권위 = CI.

FROM rust:1-slim
WORKDIR /src
COPY . .

# 1차 = cargo check (링커 불요 — R-1). 컨테이너엔 링커가 있으나, 본 fixture 의
# 강조점은 "check 가 codegen 전 정지"임을 보이는 것.
RUN cargo check --workspace

# 2차 = 완전빌드 (codegen+링킹). 컨테이너 linux toolchain 사용.
RUN cargo build --workspace

# 실행 = 빌드된 바이너리 (linux ELF). 실증용 entrypoint.
CMD ["cargo", "run", "--quiet"]
