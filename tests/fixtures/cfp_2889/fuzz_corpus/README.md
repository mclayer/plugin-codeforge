# fuzz corpus (§8.8.1 seed_or_corpus)

synthetic seed, not captured — §3.9 captured-golden 규약(합성 편집 금지·실측 시에만 갱신) 비적용.

실 400 body 원문은 §3.9 body drop 정책(truncate→scrub→deny-scan) 설계 결과로 run 산출물에 보존되지 않아 corpus 는 합성 seed 한정이다 (§8.8.1 "captured 실 400 body 갱신" 축 = 구조적 달성 불가 실측 확인 — 정직 이월, 향후 실 재측정에서 body 가 보존될 때에만 갱신).

corpus 파일 채널 = `.gitattributes` LF 정규화 지배 — CR/CRLF 케이스는 seed 파일이 아닌 테스트 내 bytes 합성 또는 Hypothesis 전략 소관 (FIX iter2 F-CL2-04).
