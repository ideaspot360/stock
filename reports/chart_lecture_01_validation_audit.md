# 차트강의 1편 블로그 포스팅 및 16:9 다크 도안 검증 감사 보고서

- **감사 일시**: 2026-11-15T15:20:00Z
- **대상 포스트**: `growth_engine/03_blog_hub/stock_blog/_posts/2026-11-15-changwon-10ma-pullback-trading-strategy.md`
- **검증 도구**: `growth_engine/03_blog_hub/stock_blog/scripts/validate_chart_lecture_blog.py`
- **도안 생성기**: `growth_engine/03_blog_hub/stock_blog/scripts/generate_chart_infographics.py`
- **감사 결과**: **전수 100% PASS (무결점 승인, Exit Code: 0)**

---

## 1. 7대 Hard-Fail 게이트 규칙별 전수 검사 결과

| 규칙 ID | 검증 항목 | 판정 | 실측 세부 사항 및 검증 데이터 |
|:---:|---|:---:|---|
| **RULE-01** | `FRONT_MATTER_SCHEMA` | **PASS** | • `layout: post` 확인 완료<br>• `title`: 3분봉·5분봉 10이평선 첫 눌림목 반등 타점과 호가창 체결강도 판독법: 데이트레이더를 위한 정석 프라이스 액션 공식<br>• `date`: 2026-11-15 10:00:00 +0900 (Jekyll `future: false` 호환)<br>• `category`: '차트강의', `categories`: ['차트강의', '실전 매매기법'] (듀얼 카테고리 정상 인덱싱)<br>• `tags`: 13개 태그 배열 완비 (최소 5개 초과)<br>• `author`: '맥락트레이딩 리서치팀' |
| **RULE-02** | `CORE_TRADING_CONCEPTS` | **PASS** | • 10이평선(10 EMA) 눌림목(Pullback) 동적 균형선 완비<br>• 3분봉(정밀 타점) 및 5분봉(추세 필터) 시너지 서술 완비<br>• 거래량 급감(Volume Dry-Up 1/3 이하) 원리 완비<br>• 호가창 체결강도 100%~120% 돌파 및 매도잔량 2~3배 우위 법칙 완비<br>• -1.5% 기계적 칼손절(Loss Asymmetry 방어) 완비<br>• 손익비(Risk-Reward Ratio 1:2.3, 승률 40% 기대값 증명) 완비 |
| **RULE-03** | `BANNED_SCAM_MYSTICISM` | **PASS** | • 13대 사짜/신비주의 블랙리스트 전수 스캔: **0건 검출 (0% 위반)**<br>• 100% 승률, 신비의 공식, 비밀 기법, 황금선, 신의 타점 등 비과학적 어휘 원천 배제 |
| **RULE-04** | `BANNED_VIDEO_ARTIFACTS` | **PASS** | • 10대 영상 제작/대본 잔재 블랙리스트 전수 스캔: **0건 검출 (0% 위반)**<br>• 대본, 나레이션, [화면전환], 타임라인, BGM 등 롱폼 영상 요소 원천 배제 및 순수 교육 칼럼 구성 |
| **RULE-05** | `AI_CLICHE_HUMANIZING` | **PASS** | • GEMINI.md 제8조 9대 AI 상투어 블랙리스트 전수 스캔: **0건 검출 (0% 위반)**<br>• 기계적 서두/결미 배제, 실전 투자자 1인칭 페르소나 및 다채로운 문장 리듬(Burstiness) 구현 |
| **RULE-06** | `IMAGE_ASSETS_INTEGRITY` | **PASS** | • 포스트 내 링크된 이미지 2종 실물 존재 및 해상도 전수 검증 통과:<br>  1. `chart_3min_5min_10ma_pullback.png`: 1920×1080 px (16:9, 비율: 1.7778, 240 KB)<br>  2. `orderbook_spoofing_execution_strength.png`: 1920×1080 px (16:9, 비율: 1.7778, 224 KB)<br>• `assets/img/posts/` 및 `assets/img/` 듀얼 복사 완비 |
| **RULE-07** | `READABILITY_STRUCTURE_EAT` | **PASS** | • 본문 순수 텍스트 공백 제외 문자수: **8,974자** (기준 2,000자 대비 448% 충족)<br>• 부호 충돌 버그(`+-`, `-+`, `++`, `--` 등): **0건 검출**<br>• 하단 금융 면책 조항(`.post-disclaimer`): 정상 삽입<br>• 하단 태그 필 블록(`.post-tags` 및 `.tag-item`): 정상 삽입 |

---

## 2. 생성 에셋 파일 인벤토리

| 파일명 | 배치 경로 | 해상도 / 규격 | 용도 |
|---|---|:---:|---|
| `generate_chart_infographics.py` | `growth_engine/03_blog_hub/stock_blog/scripts/` | Python 3 Script | 16:9 다크 테마 차트/호가창 결정론적 자동 생성기 |
| `validate_chart_lecture_blog.py` | `growth_engine/03_blog_hub/stock_blog/scripts/` | Python 3 Script | 7대 Hard-Fail 게이트 독립 검증기 |
| `2026-11-15-changwon-10ma-pullback-trading-strategy.md` | `growth_engine/03_blog_hub/stock_blog/_posts/` | Markdown (8,974자) | 실전 차트강의 1편 정규 블로그 포스팅 |
| `chart_3min_5min_10ma_pullback.png` | `assets/img/posts/` & `assets/img/` | 1920×1080 (16:9) | 10이평선 눌림목 정석 타점 인포그래픽 |
| `orderbook_spoofing_execution_strength.png` | `assets/img/posts/` & `assets/img/` | 1920×1080 (16:9) | 호가 잔량 역설 및 체결강도 구조도 인포그래픽 |
| `chart_10ma_pullback_infographic.png` | `assets/img/posts/` & `assets/img/` | 1920×1080 (16:9) | 호환용 별칭 이미지 |
| `orderbook_power_structure.png` | `assets/img/posts/` & `assets/img/` | 1920×1080 (16:9) | 호환용 별칭 이미지 |

---

## 3. 검증 결론
본 감사 대상인 실전 차트강의 1편 포스팅 및 시각화 도안 에셋은 프로젝트 아키텍처 및 헌법 규정을 단 1건의 결함 없이 100% 충족하였으며, 웹 배포를 위한 모든 준비가 완결되었음을 공식 확인합니다.
