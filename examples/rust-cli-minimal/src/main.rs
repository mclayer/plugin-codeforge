// rust-cli-minimal — codeforge Rust consumer 로컬빌드 경로 실증 (CFP-2506)
//
// 목적: 이 crate 는 `cargo check`(링커 불요, R-1)·Docker 마운트 빌드(R-3)를
//       실증하기 위한 최소 example 이다. 가상 도메인 = Log Parser
//       (cli-tool-minimal 답습). production 코드 아님.
//
// 비-Copy 값(String) 을 단 한 번 move 해 사용한다 — 만약 잘못해서 move 된 값을
// 재사용하면 rustc 가 E0382(use after partial move)를 낸다. 이 류 컴파일·차용
// 버그는 codegen 전 단계에서 잡히므로 **링커 없이 `cargo check` 만으로 검출**된다
// (도메인 지식 rust-local-build-equivalence.md R-1). 이것이 로컬 피드백 루프를
// 당기는 최소·고-ROI 경로의 실증.

/// 파싱된 로그 이벤트 (구조화 레코드). String 필드 = 비-Copy.
struct Event {
    level: String,
    message: String,
}

/// raw 로그 한 줄을 Event 로 파싱. `level message` 형태(첫 토큰 = level)를 가정.
fn parse_line(line: &str) -> Event {
    let mut parts = line.splitn(2, ' ');
    let level = parts.next().unwrap_or("info").to_string();
    let message = parts.next().unwrap_or("").to_string();
    Event { level, message }
}

fn main() {
    let sample = "warn disk usage above threshold";

    // 비-Copy String 필드를 move 해 소비한다. event.message 를 여기서 단 한 번
    // 넘기므로 차용 검사를 통과한다 (재사용 시 E0382 → cargo check 가 즉시 검출).
    let event = parse_line(sample);
    let Event { level, message } = event;

    println!("[{}] {}", level, message);
}
