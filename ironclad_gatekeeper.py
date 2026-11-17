#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
🏛️ 철벽 게이트 검증 시스템 (Ironclad Gatekeeper Verification System)
================================================================================
파일 명칭: ironclad_gatekeeper.py
버전: 1.0.0 (Production Master)
작성 목적:
  AI의 주관적 의지나 다짐에 기대지 않고, 물리적·소프트웨어적으로 글의 완전무결함을
  검증하여 낮은 품질의 글 발행을 원천 차단(Hard Block)하는 기계적 품질 게이트웨이.

적용 대상:
  1. 글로벌 영문 개발 블로그 (dev.ideaspot360.com / markets.ideaspot360.com)
  2. 국내 국문 티스토리 블로그 (softwin.tistory.com - 트러블슈팅 & 마스터 챕터)
  3. 국내 국문 네이버 블로그 생태계 (solidlog, tidynote, infopiece)
  4. 기타 생태계 블로그 (stock.ideaspot360.com, gear.ideaspot360.com 등)

핵심 철학:
  - ZERO EXTERNAL DEPENDENCY: 파이썬 표준 라이브러리(Standard Library)만으로 100% 구동.
  - HARD BLOCK BY DEFAULT: 치명적 위반(AI 클리셰, 억지 스토리, 엔지니어링 필수요소 누락,
    마크다운 문법 결함, 의료법 위반 등) 적발 시 즉각 Exit Code 1로 발행 차단.
  - TRANSPARENT FEEDBACK: 위반 행 번호, 매칭된 텍스트 스니펫, 구체적 교정 가이드라인(Fix Hint) 즉시 출력.
  - ALL-IN-ONE SINGLE FILE: 다른 블로그 전담 에이전트에게 파일 1개만 전달하면 즉시 복제 및 적용 가능.

7대 검증 게이트 (7-Layer Ironclad Verification Gates) -> 8대 확장 (8-Layer):
  [Gate 1] 구조 & 마크다운 무결성 (YAML Frontmatter, 코드 블록 짝 맞춤, 최소 분량)
  [Gate 2] AI 클리셰 & 기계적 번역투 박멸 (국문 40+ 규칙, 영문 40+ 규칙 정밀 정규식)
  [Gate 3] 억지 스토리 & 작위적 연출 차단 (새벽 몇 시 알람, 식은땀, 패닉 등 소설화 원천 배제)
  [Gate 4] 실무 엔지니어링 5대 아티팩트 검증 (Raw Log, Wrong Fix, Unified Diff, Root Cause, CLI Verify)
  [Gate 5] 사족 & 중언부언 차단 (도입부 과다 서술, 판에 박힌 결론 재요약)
  [Gate 6] 맞춤법, 오타 및 플랫폼별 특화 규격 (네이버 의료법/금지어, 이미지 링크 표기, 해시태그)
  [Gate 7] 보안 & 시크릿 누출 방벽 (API Key, AWS, 프라이빗 키 누출 차단)
  [Gate 8] 법적 리스크 & 컴플라이언스 방벽 (자본시장법·금소법, 의료법·식품표시광고법, 공정위 표시광고법, 공공누리 KOGL, 영문 SEC 글로벌 규제)
================================================================================
"""

import os
import sys
import re
import argparse
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ==============================================================================
# 🎨 터미널 컬러 서식 (ANSI Escape Codes)
# ==============================================================================
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"


# ==============================================================================
# 📊 데이터 모델 정의 (Data Models)
# ==============================================================================
@dataclass
class Violation:
    gate_id: str          # GATE_1 ~ GATE_6
    gate_name: str        # 게이트 명칭
    rule_id: str          # 상세 규칙 식별자
    severity: str         # "REJECT" (발행 차단) 또는 "WARNING" (경고/감점)
    line_number: int      # 위반 위치 (1-based, 0이면 전체 레벨)
    snippet: str          # 문제의 문장/스니펫
    message: str          # 위반 사유 설명
    fix_hint: str         # 구체적 교정 가이드


@dataclass
class GateReport:
    file_path: str
    platform: str
    is_passed: bool
    score: int
    reject_count: int
    warning_count: int
    violations: List[Violation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "platform": self.platform,
            "is_passed": self.is_passed,
            "score": self.score,
            "reject_count": self.reject_count,
            "warning_count": self.warning_count,
            "violations": [asdict(v) for v in self.violations]
        }


# ==============================================================================
# 📜 룰셋 데이터베이스 (Ironclad Ruleset Database)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. 영문 AI 클리셰 & 상투어 금지 룰셋 (English Anti-AI Clichés)
# ------------------------------------------------------------------------------
EN_AI_CLICHE_PATTERNS = [
    # 단어 수준 상투어
    (r"\bdelve\b", "REJECT", "AI 단골 어휘 'delve' 감지. 'analyze', 'examine', 'inspect', 'trace' 등으로 대체하십시오."),
    (r"\btapestry\b", "REJECT", "AI 수식어 'tapestry' 감지. 사실적 아키텍처 용어로 대체하십시오."),
    (r"\bseamlessly\b", "REJECT", "AI 상투적 부사 'seamlessly' 감지. 구체적 연동 메커니즘을 명시하십시오."),
    (r"\btestament\b", "REJECT", "AI 미사여구 'testament' 감지. 객관적 지표로 서술하십시오."),
    (r"\bgame-changer\b", "REJECT", "과장된 표현 'game-changer' 감지. 기술적 효익을 구체적 수치로 제시하십시오."),
    (r"\brevolutionize\b", "REJECT", "과장된 동사 'revolutionize' 감지. 실제 개선된 성능이나 처리량을 명시하십시오."),
    (r"\bbeacon\b", "REJECT", "AI 은유 표현 'beacon' 감지."),
    (r"\bmultifaceted\b", "REJECT", "상투적 수식어 'multifaceted' 감지."),
    (r"\bplethora\b", "REJECT", "상투적 수식어 'plethora' 감지. 'multiple', 'several' 또는 구체적 개수를 쓰십시오."),
    (r"\blinchpin\b", "REJECT", "AI 단골 은유 'linchpin' 감지. 'core component', 'critical dependency'로 쓰십시오."),
    (r"\bparamount\b", "WARNING", "상투적 강조어 'paramount' 감지. 과도한 강조를 지양하십시오."),
    (r"\bdemystify\b", "REJECT", "AI 전형적 표현 'demystify' 감지. 담백한 기술 분석 표현을 사용하십시오."),
    (r"\borchestrate\b", "WARNING", "AI 단골 동사 'orchestrate' 감지. (Kubernetes 등의 고유명사가 아닐 경우 구체적 행위 기술)"),
    (r"\bharnessing the power\b", "REJECT", "AI 관용구 'harnessing the power' 감지."),
    (r"\bat the end of the day\b", "REJECT", "구어체 상투어 'at the end of the day' 감지."),
    (r"\bwithout further ado\b", "REJECT", "AI 전형적 도입구 'without further ado' 감지. 즉시 본론으로 진입하십시오."),
    (r"\blet's dive (in|deep)\b", "REJECT", "AI 전형적 챕터 진입구 'let's dive' 감지. 본론으로 바로 들어가십시오."),

    # 문장/구절 수준 상투어
    (r"\bIn (the modern|today's) (fast-paced|digital|cloud|software) (world|landscape|era|environment)\b", "REJECT",
     "AI 전형적 도입 클리셰 'In the modern ... world/landscape' 감지. 공허한 배경 설명을 삭제하고 실제 장애 현상으로 시작하십시오."),
    (r"\bBy doing so,\s*.*?\bbecomes immune\b", "REJECT",
     "AI 과장 클리셰 'becomes immune' 감지. 엔지니어링에 '면역'은 없습니다. 방어 기전과 허용 한계를 서술하십시오."),
    (r"\bHere is the (exact|step-by-step) (diagnostic|solution|breakdown|guide)\b", "REJECT",
     "AI 전형적 튜토리얼 어투 'Here is the exact ...' 감지. 엔지니어의 담백한 관찰 서술로 바꾸십시오."),
    (r"\bIt is worth noting that\b", "WARNING", "AI 습관적 필러 'It is worth noting that' 감지. 문장을 간결하게 줄이십시오."),
    (r"\bIn conclusion,\s*", "REJECT", "AI 형식적 결론 시작 'In conclusion' 감지. 판에 박힌 요약 대신 프로덕션 런북 체크포인트를 제시하십시오."),
    (r"\bIn summary,\s*", "REJECT", "AI 형식적 결론 시작 'In summary' 감지."),
    (r"\bNow that we have (seen|understood|explored)\b", "REJECT", "AI 교과서식 전환구 감지."),
    (r"\bIt's not just a .*?;\s*it's a\b", "REJECT", "AI 이분법적 수사구 'It's not just A, it's B' 감지."),
]

# ------------------------------------------------------------------------------
# 2. 국문 AI 클리셰 & 상투어 금지 룰셋 (Korean Anti-AI Clichés)
# ------------------------------------------------------------------------------
KO_AI_CLICHE_PATTERNS = [
    # 상투적 인트로
    (r"현대\s+(소프트웨어|클라우드|개발|비즈니스|IT)\s+(생태계|환경|사회|시장)에서는?", "REJECT",
     "AI 전형적 인트로 '현대 ... 환경에서는' 감지. 교과서적 서론을 배제하고 구체적인 문제 현상으로 직행하십시오."),
    (r"눈부신\s+발전을\s+거듭하며", "REJECT", "AI 판에 박힌 수식어 '눈부신 발전을 거듭하며' 감지."),
    (r"지금부터\s+자세히\s+(살펴보겠습니다|알아보겠습니다)", "REJECT", "AI 전형적 유튜브/튜토리얼 말투 감지. 즉시 본론으로 진입하십시오."),
    (r"필수불가결한", "REJECT", "AI 상투어 '필수불가결한' 감지. 구체적인 의존성이나 필요성을 서술하십시오."),
    (r"큰\s+의의를\s+(지닙니다|갖습니다)", "REJECT", "공허한 수식어 '큰 의의를 지닙니다' 감지."),
    (r"매우\s+중요하다고\s+할\s+수\s+있습니다", "REJECT", "AI 특유의 모호한 피동 단정 '매우 중요하다고 할 수 있습니다' 감지."),
    (r"~?라\s+할\s+수\s+있겠습니다", "WARNING", "AI 피동/간접 화법 감지. 명확한 종결 어미(~이다, ~한다)를 사용하십시오."),
    (r"~?에\s+다름\s+아닙니다", "REJECT", "일본어 번역투/AI 관용구 '~에 다름 아닙니다' 감지."),
    (r"~?의\s+경우에\s+있어서", "REJECT", "번역투 '~의 경우에 있어서' 감지. '~의 경우', '~할 때'로 간결화하십시오."),
    (r"주목할\s+만한\s+점은", "WARNING", "상투적 환기구 '주목할 만한 점은' 감지."),

    # 상투적 아웃트로/결론
    (r"결론적으로\s+(말씀드리면|말하자면)", "REJECT", "AI 전형적 결론 도입구 감지. 상투적 결론 대신 실무 점검 체크리스트로 마무리하십시오."),
    (r"지금까지\s+.*?에\s+대해\s+(알아보았습니다|살펴보았습니다)", "REJECT", "AI 클로징 멘트 '~에 대해 알아보았습니다' 감지. 기계적 정리를 금지합니다."),
    (r"앞으로도\s+.*?많은\s+관심\s+부탁드립니다", "WARNING", "마케팅 블로그형 맺음말 감지. 기술 백서다운 전문적 마무리를 적용하십시오."),
]

# ------------------------------------------------------------------------------
# 3. 억지 스토리 & 작위적 연출 금지 룰셋 (No-Forced-Drama Patterns)
# ------------------------------------------------------------------------------
FORCED_DRAMA_PATTERNS_KO = [
    (r"새벽\s*[0-9]+시(\s*[0-9]+분)?", "REJECT",
     "억지 타임스탬프('새벽 X시') 감지. 3류 소설식 시간 연출을 배제하고 담백한 모니터링 현상(예: '프로덕션 API 게이트웨이 504 스파이크')으로 기술하십시오."),
    (r"새벽\s*한\s*가운데", "REJECT", "작위적인 시간적 배경 묘사 감지."),
    (r"비상\s*(호출|알람|연락)이\s*(울렸다|울려\s*퍼졌다)", "REJECT", "억지 위기 상황 소설화 감지. 실제 모니터링 메트릭 및 알람 룰을 명시하십시오."),
    (r"(등줄기|이마|손)에\s*(식은땀|땀)이\s*(흘렀다|흘러내렸다|송골송골)", "REJECT", "신체 반응 과장 묘사('식은땀') 감지. 엔지니어링 문서에 부적합합니다."),
    (r"(머릿속|머리속)이\s*하얘(졌다|졌다)", "REJECT", "감정적 과장 묘사('머릿속이 하얘졌다') 감지."),
    (r"정신이\s*아득해(졌다|졌다)", "REJECT", "감정적 과장 묘사('정신이 아득해졌다') 감지."),
    (r"패닉에\s*빠(졌다|졌다)", "REJECT", "소설식 연출('패닉에 빠졌다') 감지."),
    (r"심장이\s*(덜컥|멎는|쿵쾅)", "REJECT", "신체 반응 과장 묘사 감지."),
    (r"피가\s*거꾸로\s*솟", "REJECT", "극단적 과장 묘사 감지."),
]

FORCED_DRAMA_PATTERNS_EN = [
    (r"\b(2|3|4|5)\s*(?:am|a\.m\.)\b", "REJECT",
     "Forced drama timestamp ('3 AM') detected. Replace fake emergency storytelling with direct engineering context (e.g., 'During peak ingress traffic...')."),
    (r"\bmiddle of the night\b", "REJECT", "Forced dramatic narrative setting detected."),
    (r"\bpagerduty (alert|notification) (woke|buzzed|screamed)\b", "REJECT", "Cliché PagerDuty wake-up story detected."),
    (r"\bcold sweat\b", "REJECT", "Exaggerated physical reaction ('cold sweat') detected."),
    (r"\bheart sank\b", "REJECT", "Dramatic storytelling phrase ('heart sank') detected."),
    (r"\bpanic ensued\b", "REJECT", "Melodramatic phrase ('panic ensued') detected."),
    (r"\bfrantic (debugging|scramble|effort)\b", "REJECT", "Melodramatic phrase ('frantic scramble') detected."),
    (r"\bnightmare scenario\b", "REJECT", "Sensationalist phrase ('nightmare scenario') detected."),
]

# ------------------------------------------------------------------------------
# 4. 네이버 블로그 특화 규격 & 법적 리스크 룰셋 (Naver Specific Rules)
# ------------------------------------------------------------------------------
NAVER_HEALTH_FORBIDDEN = [
    (r"치료", "REJECT", "[의료법 위반 방벽] 건기식 포스팅에 '치료' 단어 100% 금지. '식약처 고시 기능성 보충', '체내 메커니즘 지원' 등으로 대체하십시오."),
    (r"완치", "REJECT", "[의료법 위반 방벽] '완치' 단어 100% 금지."),
    (r"특효약", "REJECT", "[의료법 위반 방벽] '특효약' 과장 광고 단어 100% 금지."),
    (r"완벽\s*예방", "REJECT", "[의료법 위반 방벽] '완벽 예방' 표방 금지."),
    (r"항암", "REJECT", "[의료법 위반 방벽] 질병 치유/항암 표방 절대 금지."),
    (r"만병통치", "REJECT", "[의료법 위반 방벽] '만병통치' 표방 금지."),
    (r"약효", "REJECT", "[의료법 위반 방벽] 건기식에 '약효' 표현 금지. '생체이용률', '흡수 기전' 등으로 대체."),
]

# ------------------------------------------------------------------------------
# 5. 플랫폼 카테고리 정의
# ------------------------------------------------------------------------------
DEV_OFFICIAL_CATEGORIES = [
    "Cloud & DevOps",
    "Database & Storage",
    "Systems & Networking"
]

TISTORY_OFFICIAL_CATEGORIES = [
    "프로그래밍 언어 & 패러다임",
    "컴퓨터 과학 핵심 기초",
    "네트워크 & 웹 통신 기술",
    "백엔드 & 서버 아키텍처",
    "프론트엔드 & 클라이언트",
    "데이터베이스 & 스토리지",
    "클라우드, DevOps & 인프라",
    "보안 & 인증 기술",
    "AI, 머신러닝 & 빅데이터",
    "소프트웨어 공학 & 아키텍처",
    "임베디드 & 차세대 기술",
    "실무 장애 트러블슈팅 (Post-Mortem)",
    "실무 장애 트러블슈팅"
]

# ------------------------------------------------------------------------------
# 6. 법적 리스크 & 컴플라이언스 룰셋 데이터베이스 (Legal & Compliance Rulesets)
# ------------------------------------------------------------------------------

# [6-1] 자본시장법 & 금융소비자보호법(금소법) 방벽
# (자본시장법 제55조 손실보전 금지, 금소법 제19조~21조 부당권유행위 금지)
CAPITAL_MARKETS_RULES = [
    # 1. 원금보장 및 손실보전 약정
    (
        r"원금(?:을|은|도|\s*)?\s*보장(?!\s*(?:하지\s*않|되지\s*않|은\s*없|이\s*없|이\s*아닙|이\s*아님|이\s*불가|을\s*하지\s*않|할\s*수\s*없))",
        "REJECT",
        "G8_FIN_PRINCIPAL_GUARANTEE",
        "[자본시장법·금소법 방벽] '원금 보장' 표방 금지 (자본시장법 제55조 및 금소법 제21조). 금융투자상품은 원금 손실 위험이 수반되므로 원금을 보장할 수 없습니다.",
        "원금 보장 표현을 삭제하고 원금 손실 가능성 및 투자 위험 고지 문구를 삽입하십시오."
    ),
    (
        r"원금\s*(?:손실|손실이|손실은)\s*(?:없는|없음|없고|0%|제로)",
        "REJECT",
        "G8_FIN_NO_LOSS_CLAIM",
        "[자본시장법·금소법 방벽] '원금 손실 없음/0%' 단언 금지 (금소법 제19조 부당권유행위).",
        "원금 손실이 없다는 비현실적인 단언을 삭제하고 시장 변동성 위험을 명시하십시오."
    ),
    (
        r"원금(?:을|의|은|\s*)?\s*(?:전액\s*)?보존(?!\s*(?:하지\s*않|되지\s*않|은\s*없|이\s*없|이\s*아닙|이\s*불가|할\s*수\s*없))",
        "REJECT",
        "G8_FIN_PRINCIPAL_PRESERVATION",
        "[자본시장법·금소법 방벽] '원금 보존' 약정 표현 금지 (자본시장법 제55조).",
        "원금 보존 표현을 삭제하십시오."
    ),
    (
        r"원금\s*(?:회수|반환)\s*100%",
        "REJECT",
        "G8_FIN_PRINCIPAL_RECOVERY",
        "[자본시장법·금소법 방벽] '원금 회수 100%' 표방 금지.",
        "원금 회수 100% 표현을 삭제하십시오."
    ),
    (
        r"손실(?:을|은|\s*)?\s*(?:전액\s*)?보전(?!\s*(?:하지\s*않|되지\s*않|은\s*없|이\s*없|이\s*아닙|이\s*불가|할\s*수\s*없))",
        "REJECT",
        "G8_FIN_LOSS_COMPENSATION",
        "[자본시장법 제55조 위반] '손실 보전' 약속 금지.",
        "손실 보전 표현을 삭제하십시오."
    ),

    # 2. 확정수익 및 무위험 고수익 표방
    (
        r"확정\s*수익(?:률)?(?!\s*(?:을\s*보장하지\s*않|이\s*아닙|은\s*없|을\s*약속하지\s*않))",
        "REJECT",
        "G8_FIN_CONFIRMED_PROFIT",
        "[자본시장법·금소법 방벽] '확정 수익(률)' 표방 금지 (금소법 제19조). 예적금을 제외한 금융투자상품에 확정 수익률을 표방할 수 없습니다.",
        "확정 수익 표현을 삭제하고 기대 수익과 시나리오별 리스크를 균형 있게 기술하십시오."
    ),
    (
        r"무위험\s*고수익",
        "REJECT",
        "G8_FIN_RISK_FREE_HIGH_RETURN",
        "[자본시장법·금소법 방벽] '무위험 고수익' 기만 표현 금지 (금소법 제19조).",
        "고수익에는 상응하는 고위험이 수반됨을 명시하십시오."
    ),
    (
        r"위험\s*없는\s*(?:고수익|투자)",
        "REJECT",
        "G8_FIN_RISK_FREE_INVESTMENT",
        "[자본시장법·금소법 방벽] '위험 없는 투자' 표방 금지.",
        "투자 리스크를 객관적으로 명시하십시오."
    ),
    (
        r"수익(?:률)?(?:을|은|\s*)?\s*보장(?!\s*(?:하지\s*않|되지\s*않|은\s*없|이\s*없|이\s*아닙|이\s*아님|이\s*불가|을\s*하지\s*않|할\s*수\s*없))",
        "REJECT",
        "G8_FIN_GUARANTEED_PROFIT",
        "[자본시장법·금소법 방벽] '수익(률) 보장' 표현 금지.",
        "수익 보장 표현을 삭제하십시오."
    ),
    (
        r"100%\s*(?:수익|수익률|원금보장)",
        "REJECT",
        "G8_FIN_100_PERCENT_PROFIT",
        "[자본시장법·금소법 방벽] '100% 수익(률)' 단언 금지.",
        "100% 수익 단언을 배제하십시오."
    ),
    (
        r"손실률\s*0%",
        "REJECT",
        "G8_FIN_ZERO_LOSS_RATE",
        "[자본시장법·금소법 방벽] '손실률 0%' 표방 금지.",
        "손실 위험을 솔직하게 기술하십시오."
    ),

    # 3. 사기성 리딩방 어투 및 시세조종 조장
    (
        r"VIP\s*(?:리딩|추천|정보)",
        "REJECT",
        "G8_FIN_VIP_LEADING",
        "[자본시장법 방벽] 불법 사기성 리딩방 어투 'VIP 리딩/추천' 감지 (자본시장법 위반 소지).",
        "사기성 리딩방 마케팅 용어를 전면 삭제하십시오."
    ),
    (
        r"급등주\s*(?:추천|대공개|포착|공개|발굴|무료)",
        "REJECT",
        "G8_FIN_SURGE_STOCK",
        "[자본시장법 방벽] 선동적 투기 조장 '급등주 추천/포착' 감지.",
        "투기 조장 어휘를 삭제하고 펀더멘털 및 매크로 지표 분석으로 전환하십시오."
    ),
    (
        r"특급\s*(?:호재|정보|재료)",
        "REJECT",
        "G8_FIN_SPECIAL_INSIDER_INFO",
        "[자본시장법 방벽] 사기성 미공개 정보 유혹 어투 '특급 호재/재료' 감지.",
        "객관적 공시 및 시장 뉴스 기반으로 서술하십시오."
    ),
    (
        r"무조건\s*(?:폭등|상승|상한가)",
        "REJECT",
        "G8_FIN_UNCONDITIONAL_SURGE",
        "[자본시장법 방벽] '무조건 폭등/상승/상한가' 선동적 과장 표현 감지.",
        "가격 변동을 확언하는 어투를 배제하십시오."
    ),
    (
        r"내일\s*(?:무조건\s*)?상한가",
        "REJECT",
        "G8_FIN_TOMORROW_UPPER_LIMIT",
        "[자본시장법 방벽] '내일 상한가' 허위 유혹 표현 감지.",
        "내일 상한가 표현을 삭제하십시오."
    ),
    (
        r"세력\s*(?:매집|입성|작전)(?:주)?",
        "REJECT",
        "G8_FIN_MARKET_MANIPULATION",
        "[자본시장법 방벽] '세력 매집/작전주' 등 시세조종 및 불법 투기 조장 어휘 감지 (자본시장법 제178조).",
        "세력/작전 관련 불법 투기 표현을 전면 삭제하십시오."
    ),
    (
        r"선취매(?:\s*완료|\s*종목)?",
        "REJECT",
        "G8_FIN_FRONT_RUNNING",
        "[자본시장법 방벽] 불법 선취매 표방 어투 감지 (자본시장법 불공정거래행위 소지).",
        "선취매 표현을 삭제하십시오."
    ),
    (
        r"단타\s*리딩방",
        "REJECT",
        "G8_FIN_LEADING_ROOM",
        "[자본시장법 방벽] '단타 리딩방' 등 불법 유사투자자문 어휘 감지.",
        "리딩방 홍보 및 유인 어휘를 삭제하십시오."
    ),
    (
        r"목표가\s*(?:찍고|도달\s*확정)",
        "REJECT",
        "G8_FIN_GUARANTEED_TARGET_PRICE",
        "[자본시장법 방벽] '목표가 도달 확정' 표방 감지.",
        "목표가 도달을 확언하지 마십시오."
    ),

    # 4. 미등록 투자자문 소지 표현
    (
        r"무료\s*(?:종목\s*)?상담",
        "REJECT",
        "G8_FIN_UNREGISTERED_ADVICE_CONSULT",
        "[자본시장법 제17조 위반] 미등록 투자자문 소지 '무료 종목 상담' 감지.",
        "개별 종목 상담 유도 문구를 삭제하십시오."
    ),
    (
        r"1:1\s*(?:투자\s*)?(?:리딩|자문|코칭|상담)",
        "REJECT",
        "G8_FIN_UNREGISTERED_1ON1",
        "[자본시장법 제17조 위반] 불법 '1:1 투자 리딩/자문' 표현 감지.",
        "1:1 투자 자문 어휘를 삭제하십시오."
    ),
    (
        r"(?:지금|오늘)\s*당장\s*(?:매수|매도)하십시오",
        "REJECT",
        "G8_FIN_URGENT_TRADE_ORDER",
        "[자본시장법 위반] 일방적 매매 지시 어투 감지.",
        "독자에게 특정 매매 행위를 강요하지 마십시오."
    ),
    (
        r"(?:무조건|반드시)\s*(?:풀매수|매수|매도)하세요",
        "REJECT",
        "G8_FIN_FORCED_TRADE_ORDER",
        "[자본시장법 위반] 단정적 매수/매도 권유 어투 감지.",
        "판단은 투자자 본인의 몫임을 존중하는 기술적 분석으로 서술하십시오."
    ),
    (
        r"종목\s*찍어드립니다",
        "REJECT",
        "G8_FIN_PICK_STOCK",
        "[자본시장법 위반] 불법 종목 추천 어투 감지.",
        "종목 찍어주기 식 어투를 배제하십시오."
    ),
]

KO_FINANCIAL_DISCLAIMER_PATTERNS = [
    r"투자\s*(?:유의사항|경고|참고)",
    r"면책\s*(?:고지|문구)",
    r"투자를?\s*(?:권유|자문|추천|판단|책임)",
    r"권유가\s*아닙",
    r"자문이\s*아닙",
    r"추천이\s*아닙",
    r"원금\s*손실",
    r"손실\s*(?:의\s*)?위험",
    r"본\s*(?:글|포스팅|아티클|자료|콘텐츠)은?는?\s*.*?(?:참고|정보\s*제공)",
    r"정보\s*제공\s*목적",
    r"투자\s*결정은\s*본인",
    r"투자의\s*책임은\s*(?:투자자|본인)",
    r"금융소비자보호법",
    r"금소법",
]

# [6-2] 의료법 & 건강기능식품법(식품표시광고법) 방벽
# (식품표시광고법 제8조 부당한 표시·광고 금지, 의료법 제56조 의료광고 금지)
MEDICAL_LAW_RULES = [
    # 1. 질병 예방/치료 표방 금지
    (
        r"완치",
        "REJECT",
        "G8_MED_CURE_ALL",
        "[식품표시광고법 제8조 위반] '완치' 단어 사용 금지. 건강기능식품/일반식품은 질병 완치를 표방할 수 없습니다.",
        "'완치'를 삭제하고 '체내 흡수율 개선', '영양 공급' 등 객관적 기전으로 서술하십시오."
    ),
    (
        r"특효약",
        "REJECT",
        "G8_MED_MAGIC_CURE",
        "[식품표시광고법 제8조 위반] '특효약' 등 과장 광고 단어 100% 금지.",
        "'특효약' 표현을 삭제하십시오."
    ),
    (
        r"완벽\s*예방",
        "REJECT",
        "G8_MED_PERFECT_PREVENTION",
        "[식품표시광고법 위반] '완벽 예방' 표방 금지.",
        "'완벽 예방' 표현을 삭제하십시오."
    ),
    (
        r"만병통치",
        "REJECT",
        "G8_MED_PANACEA",
        "[식품표시광고법 위반] '만병통치' 표방 금지.",
        "'만병통치' 표현을 삭제하십시오."
    ),
    (
        r"기적의\s*(?:치료|영양제|효능)",
        "REJECT",
        "G8_MED_MIRACLE_CURE",
        "[식품표시광고법 위반] '기적의 치료/영양제' 과장 수식어 금지.",
        "기적 등의 비과학적 수식어를 배제하십시오."
    ),
    (
        r"항암(?:\s*효과|\s*작용|\s*치료)",
        "REJECT",
        "G8_MED_ANTICANCER",
        "[식품표시광고법 위반] 식품/영양소의 '항암 효과/치료' 표방 절대 금지.",
        "항암 표방 표현을 전면 삭제하십시오."
    ),
    (
        r"병이\s*낫는",
        "REJECT",
        "G8_MED_DISEASE_REMEDY",
        "[식품표시광고법 위반] '병이 낫는' 표방 금지.",
        "질병 치유 표방 표현을 삭제하십시오."
    ),

    # 2. 의약품 오인·혼동 표현
    (
        r"천연\s*치료제",
        "REJECT",
        "G8_MED_NATURAL_MEDICINE",
        "[식품표시광고법 제8조 위반] 건강기능식품/식품을 '천연 치료제'로 의약품 오인 유발 금지.",
        "'천연 치료제' 표현을 삭제하고 '식품의약품안전처 고시 기능성 원료'로 서술하십시오."
    ),
    (
        r"약(?:을|\s*)?\s*대신(?:\s*먹는)?",
        "REJECT",
        "G8_MED_INSTEAD_OF_DRUG",
        "[식품표시광고법 위반] '약 대신' 등 의약품 대체 오인 표현 금지.",
        "의약품을 대체할 수 없음을 명시하십시오."
    ),
    (
        r"의약품(?:을|\s*)?\s*(?:대체|대용)",
        "REJECT",
        "G8_MED_DRUG_SUBSTITUTE",
        "[식품표시광고법 위반] '의약품 대체/대용' 표방 금지.",
        "의약품 대체 표현을 삭제하십시오."
    ),
    (
        r"처방약(?:을|은|\s*)?\s*(?:중단|끊고|대체)",
        "REJECT",
        "G8_MED_STOP_PRESCRIPTION",
        "[의료법·식품표시광고법 위반] 환자에게 '처방약 중단/끊고' 유도 절대 금지 (중대한 건강 위해 행위).",
        "전문의 처방약 복용 유지를 안내하십시오."
    ),
    (
        r"부작용(?:이|\s*)?\s*없는\s*(?:치료제|약)",
        "REJECT",
        "G8_MED_NO_SIDE_EFFECT_DRUG",
        "[식품표시광고법 위반] '부작용 없는 치료제/약' 표방 금지.",
        "치료제/약 표현을 삭제하십시오."
    ),
    (
        r"병원(?:에|\s*)?\s*갈\s*필요\s*(?:없는|없음)",
        "REJECT",
        "G8_MED_NO_HOSPITAL_NEED",
        "[의료법 위반] '병원 갈 필요 없는' 등 진료 회피 유도 금지.",
        "이상 증상 시 의사의 진료를 받도록 안내하십시오."
    ),

    # 3. 의료인 사칭 및 추천 보증
    (
        r"(?:현직|임상)\s*(?:의사|약사|한의사)로서",
        "REJECT",
        "G8_MED_IMPERSONATION_PROFESSIONAL",
        "[의료법 제56조 및 표시광고법 위반] 비의료인의 의료인(의사/약사/한의사) 자격 사칭 금지.",
        "소비자 및 영양 데이터 팩트체커 입장에서 객관적으로 서술하십시오."
    ),
    (
        r"(?:의사|약사|한의사)인\s*제가",
        "REJECT",
        "G8_MED_IMPERSONATION_SELF",
        "[의료법 제56조 위반] 의료인 자격 사칭 표현 감지.",
        "의료인 사칭 어투를 삭제하십시오."
    ),
    (
        r"전문의가\s*보증하는",
        "REJECT",
        "G8_MED_DOCTOR_ENDORSEMENT",
        "[식품표시광고법 위반] '전문의가 보증하는' 등 특정 의료인 추천/보증 표방 금지.",
        "공인 학술 논문 및 식약처 공시 자료로 대체하십시오."
    ),
    (
        r"병원장\s*추천",
        "REJECT",
        "G8_MED_HOSPITAL_CHIEF_REC",
        "[식품표시광고법 위반] '병원장 추천' 표방 금지.",
        "병원장 추천 표현을 삭제하십시오."
    ),

    # 4. 거짓·과장된 기능성 광고
    (
        r"체지방\s*100%\s*(?:분해|감소|연소)",
        "REJECT",
        "G8_MED_100PCT_FAT_BURN",
        "[식품표시광고법 위반] '체지방 100% 분해/연소' 비과학적 허위 과장 표현 금지.",
        "식약처 인정 기능성 범위 내로 기재하십시오."
    ),
    (
        r"노화\s*(?:완전\s*)?역전",
        "REJECT",
        "G8_MED_AGING_REVERSAL",
        "[식품표시광고법 위반] '노화 완전 역전' 과장 광고 금지.",
        "항산화 영양소의 체내 작용 기전으로 담백하게 설명하십시오."
    ),
    (
        r"기억력\s*[0-9]+배\s*(?:향상|상승)",
        "REJECT",
        "G8_MED_MEMORY_MULTIPLIER",
        "[식품표시광고법 위반] '기억력 N배 향상' 등 입증되지 않은 수치 과장 금지.",
        "인체적용시험 결과의 통계적 유의성으로 설명하십시오."
    ),
    (
        r"하루만에\s*(?:완치|치료|개선|정상화)",
        "REJECT",
        "G8_MED_ONE_DAY_CURE",
        "[식품표시광고법 위반] '하루만에 완치/개선' 과장 광고 금지.",
        "즉각적인 극적 효과 과장을 삭제하십시오."
    ),
]

HEALTH_DISCLAIMER_PATTERNS = [
    r"면책",
    r"의사의\s*진료",
    r"처방을\s*대신",
    r"의료\s*전문가와\s*상담",
    r"전문\s*의료인",
    r"의사\s*(?:또는|및)\s*약사와\s*상담",
    r"의약품이\s*(?:아님|아니|아닙)",
    r"진단\s*및\s*처방",
    r"의료인의\s*진단",
    r"건강\s*정보\s*제공",
    r"일반적인\s*건강\s*정보",
    r"질병의\s*(?:예방\s*및\s*)?치료를\s*(?:위한\s*의약품이\s*아닙|목적으로\s*하지\s*않)",
    r"의학적\s*치료\s*행위가\s*아닙",
]

# 하위 호환성 유지용 키워드 리스트
HEALTH_DISCLAIMER_KEYWORDS = [
    "면책", "의사의 진료", "처방을 대신", "의료 전문가와 상담", "일반적인 건강 정보",
    "전문 의료인", "의사 또는 약사와 상담", "의약품이 아님", "진단 및 처방", "의료인의 진단"
]

# [6-3] 공정거래위원회 추천·보증 심사지침 (대가성 표시광고법)
AFFILIATE_LINK_PATTERNS = [
    r"link\.coupang\.com",
    r"coupang\.com\/vp\/products",
    r"partners\.coupang\.com",
    r"linkprice\.com",
    r"adpick\.co\.kr",
    r"tenping\.kr",
    r"clix\.kr",
    r"amzn\.to",
    r"amazon\.com\/.*[?&]tag=",
    r"aliexpress\.com\/.*[?&]aff_",
]

AFFILIATE_KEYWORD_PATTERNS = [
    r"쿠팡\s*파트너스",
    r"제휴\s*(?:마케팅|링크|수수료)",
    r"원고료(?:를|\s*)?\s*(?:지원|지급)",
    r"제품(?:을|\s*)?\s*(?:협찬|지원)",
    r"수수료(?:를|\s*)?\s*(?:발생|제공받)",
    r"파트너스\s*활동",
    r"스폰서\s*링크",
]

FTC_DISCLOSURE_PATTERNS = [
    r"소정의\s*수수료",
    r"일정액의\s*수수료",
    r"수수료를\s*(?:제공|지원|지급)받",
    r"수수료를\s*받(?:을\s*수|을\s*있|았)",
    r"경제적\s*대가",
    r"공정거래위원회\s*(?:지침|문구)",
    r"추천[·\s]보증\s*(?:등에\s*관한\s*)?심사지침",
    r"원고료를\s*(?:지급|지원)받",
    r"제품을\s*(?:제공|협찬)받",
    r"파트너스\s*활동의\s*일환",
    r"대가성\s*(?:광고|표시|문구)",
    r"유료\s*광고\s*포함",
    # English & Global FTC Disclosures (US FTC 16 CFR § 255.5)
    r"(?i)\baffiliate\s+(?:link|links|commission|commissions)\b",
    r"(?i)\bearn\s+from\s+qualifying\s+purchases\b",
    r"(?i)\bpaid\s+(?:link|links|ad|advertisement|partnership)\b",
    r"(?i)\bcommission\s+at\s+no(?:\s+additional)?\s+cost\b",
    r"(?i)\b(?:sponsored|promoted)\s+content\b",
]

COVERT_AD_PATTERNS = [
    (
        r"(?:내돈내산|직접\s*구매한|100%\s*자비).*?(?:link\.coupang\.com|amzn\.to|partners\.coupang)",
        "REJECT",
        "G8_FTC_COVERT_MY_MONEY",
        "[공정위 표시광고법 위반] 제휴 링크가 포함되어 있으나 '내돈내산/자비 구매'로 소비자를 오도하는 기만적 스텔스 마케팅 감지.",
        "'내돈내산' 허위 표기를 삭제하고 공정위 표준 대가성 문구를 기재하십시오."
    ),
    (
        r"광고\s*아닙니다.*?(?:link\.coupang\.com|partners\.coupang|amzn\.to)",
        "REJECT",
        "G8_FTC_COVERT_NOT_AD",
        "[공정위 표시광고법 위반] 제휴 수수료 링크가 있으면서 '광고 아닙니다'라고 허위 주장하는 행위 감지.",
        "광고 부인 문구를 삭제하고 수수료 제공 사실을 명시하십시오."
    ),
]

# [6-4] 공공누리(KOGL) 저작권 출처 표기 의무
POLICY_TOPIC_PATTERNS = [
    r"정부\s*(?:지원금|정책|보조금)",
    r"복지\s*(?:지원금|정책|급여|혜택)",
    r"청년도약계좌",
    r"청년내일저축계좌",
    r"국민기초생활보장",
    r"근로장려금",
    r"자녀장려금",
    r"소상공인\s*(?:지원금|손실보전금|방역지원금)",
    r"국민취업지원제도",
    r"긴급복지지원",
    r"보건복지부",
    r"고용노동부",
    r"국세청\s*(?:환급금|연말정산)",
    r"정부24",
    r"복지로",
    r"행정안전부",
    r"중소벤처기업부",
]

KOGL_ATTRIBUTION_PATTERNS = [
    r"공공누리",
    r"KOGL",
    r"제[1-4]유형",
    r"공공저작물",
    r"출처\s*:\s*(?:대한민국\s*)?정책브리핑",
    r"출처\s*:\s*공공데이터포털",
    r"출처\s*:\s*(?:보건복지부|고용노동부|국세청|행정안전부|정부24|복지로|기획재정부|금융위원회|중소벤처기업부)",
    r"본\s*저작물은\s*.*?(?:공공누리|출처표시)",
    r"공공기관\s*저작물",
]

# [6-5] 영문 글로벌 금융 규제 방벽 (SEC Compliance & Global Regulations)
GLOBAL_FINANCIAL_RULES = [
    # 1. Guaranteed Returns & Risk-Free Claims
    (
        r"(?i)(?<!no\s)(?<!not\s)\bguaranteed\s+(?:returns?|profits?|yields?|income|gains?)\b",
        "REJECT",
        "G8_GLOBAL_GUARANTEED_RETURNS",
        "[SEC Global Compliance] Illegal guaranteed returns claim detected (US SEC Rule 10b-5 / FINRA Rule 2210). All securities investments carry market risk.",
        "Remove any guarantee of returns and state potential volatility and market risks objectively."
    ),
    (
        r"(?i)\brisk-free\s+(?:profits?|returns?|yields?|investments?)\b",
        "REJECT",
        "G8_GLOBAL_RISK_FREE_PROFIT",
        "[SEC Global Compliance] Misleading 'risk-free profit/return' claim detected.",
        "Eliminate 'risk-free' claims and provide balanced risk disclosure."
    ),
    (
        r"(?i)\b100%\s*(?:guaranteed|win\s*rate|profit|success\s*rate)\b",
        "REJECT",
        "G8_GLOBAL_100PCT_WIN_RATE",
        "[SEC Global Compliance] Unrealistic '100% win rate / profit' claim detected.",
        "Remove false certainty claims regarding trading performance."
    ),
    (
        r"(?i)\bcannot\s+lose(?:\s+money)?\b",
        "REJECT",
        "G8_GLOBAL_CANNOT_LOSE",
        "[SEC Global Compliance] Deceptive 'cannot lose money' claim detected.",
        "Acknowledge the risk of financial loss in all market conditions."
    ),
    (
        r"(?i)\bzero\s+risk\s+invest(?:ing|ment)\b",
        "REJECT",
        "G8_GLOBAL_ZERO_RISK",
        "[SEC Global Compliance] 'Zero risk investment' claim detected.",
        "Remove zero risk claim and state actual risk parameters."
    ),
    (
        r"(?i)\bguaranteed\s+(?:to\s+double|10x|100x)\b",
        "REJECT",
        "G8_GLOBAL_GUARANTEED_MULTIPLIER",
        "[SEC Global Compliance] Fraudulent multiplier guarantee ('guaranteed 10x') detected.",
        "Remove multiplier promises."
    ),
    (
        r"(?i)\bunconditional\s+returns?\b",
        "REJECT",
        "G8_GLOBAL_UNCONDITIONAL_RETURNS",
        "[SEC Global Compliance] 'Unconditional return' claim detected.",
        "Remove unconditional return statements."
    ),

    # 2. Illegal Investment Advice / Stock Solicitation / Market Manipulation
    (
        r"(?i)\bbuy\s+this\s+stock\s+(?:now|today|immediately)\b",
        "REJECT",
        "G8_GLOBAL_URGENT_BUY_CALL",
        "[SEC Compliance] Unregistered investment solicitation / urgent trade command detected (Investment Advisers Act of 1940).",
        "Present objective fundamental and quantitative analysis without direct buy/sell imperatives."
    ),
    (
        r"(?i)\bsell\s+this\s+stock\s+(?:now|today|immediately)\b",
        "REJECT",
        "G8_GLOBAL_URGENT_SELL_CALL",
        "[SEC Compliance] Direct sell command detected.",
        "Replace trading commands with neutral valuation commentary."
    ),
    (
        r"(?i)\bguaranteed\s+target\s+price\b",
        "REJECT",
        "G8_GLOBAL_TARGET_PRICE_GUARANTEE",
        "[SEC Compliance] Deceptive 'guaranteed target price' claim detected.",
        "State price targets as analyst estimates with associated uncertainty."
    ),
    (
        r"(?i)\bpump\s+and\s+dump\b",
        "REJECT",
        "G8_GLOBAL_PUMP_AND_DUMP",
        "[SEC Rule 10b-5] Pump-and-dump market manipulation language detected.",
        "Remove all references promoting artificial volume or price inflation."
    ),
    (
        r"(?i)\binsider\s+(?:tip|trading|leak)\b",
        "REJECT",
        "G8_GLOBAL_INSIDER_TIP",
        "[SEC Rule 10b5-1] Illegal insider information claim detected.",
        "Rely strictly on publicly disclosed SEC filings and verifiable market data."
    ),
    (
        r"(?i)\byou\s+must\s+buy\s+this\b",
        "REJECT",
        "G8_GLOBAL_MUST_BUY",
        "[SEC Compliance] Coercive trade recommendation detected.",
        "Frame conclusions as analytical insights rather than mandates."
    ),
    (
        r"(?i)\bguaranteed\s+to\s+skyrocket\b",
        "REJECT",
        "G8_GLOBAL_SKYROCKET_CLAIM",
        "[SEC Compliance] Sensationalist stock pumping language detected.",
        "Remove sensationalist hype."
    ),
    (
        r"(?i)\bexclusive\s+(?:trading\s+signal|stock\s+alert)\b",
        "REJECT",
        "G8_GLOBAL_EXCLUSIVE_SIGNAL",
        "[SEC Compliance] Boiler-room style 'exclusive trading signal' lure detected.",
        "Remove boiler-room solicitation language."
    ),
]

GLOBAL_DISCLAIMER_PATTERNS = [
    r"(?i)\bdisclaimer\b",
    r"(?i)\bnot\s+financial\s+advice\b",
    r"(?i)\bnot\s+an\s+investment\s+advice\b",
    r"(?i)\binformational\s+purposes\s+only\b",
    r"(?i)\beducational\s+purposes\s+only\b",
    r"(?i)\bdo\s+your\s+own\s+research\b",
    r"(?i)\bpast\s+performance\s+(?:is\s+no|does\s+not)\s+guarantee\b",
    r"(?i)\bconsult\s+a\s+licensed\s+financial\s+advisor\b",
    r"(?i)\bfor\s+research\s+purposes\s+only\b",
    r"(?i)\brisk\s+of\s+loss\b",
]


# ==============================================================================
# ⚙️ 철벽 게이트 검증 엔진 (Ironclad Gatekeeper Engine)
# ==============================================================================
class IroncladGatekeeper:
    """
    모든 블로그 콘텐츠의 무결성을 기계적으로 판정하는 마스터 검증 엔진.
    """

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode

    def detect_platform(self, file_path: str, content: str) -> str:
        """파일 경로 및 본문 패턴으로 플랫폼 자동 감지."""
        norm_path = file_path.replace("\\", "/").lower()
        if "blogs/dev" in norm_path or "dev.ideaspot360" in norm_path:
            return "dev"
        if "markets" in norm_path or "markets.ideaspot360" in norm_path:
            return "markets"
        if "stock" in norm_path or "stock.ideaspot360" in norm_path:
            return "stock"
        if "gear" in norm_path or "gear.ideaspot360" in norm_path:
            return "gear"
        if "naver" in norm_path or "solidlog" in norm_path or "tidynote" in norm_path or "infopiece" in norm_path:
            return "naver"
        # Frontmatter 언어 및 메타데이터 검사
        if re.search(r"^category:\s*(Cloud & DevOps|Database & Storage|Systems & Networking)", content, re.MULTILINE):
            return "dev"
        return "tistory"

    def split_frontmatter_and_body(self, content: str) -> Tuple[Optional[str], str, int]:
        """
        Frontmatter(--- ... ---)와 Body 분리.
        반환: (frontmatter_text, body_text, body_start_line)
        """
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return None, content, 1

        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm_text = "\n".join(lines[1:i])
                body_text = "\n".join(lines[i + 1:])
                return fm_text, body_text, i + 2

        return None, content, 1

    def parse_frontmatter(self, fm_text: Optional[str]) -> Dict[str, str]:
        """단순 정규식 기반 안전한 Frontmatter 파싱 (PyYAML 미설치 환경 대비)."""
        if not fm_text:
            return {}
        data = {}
        for line in fm_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r"^([a-zA-Z0-9_\-]+)\s*:\s*(.*)$", line)
            if match:
                k, v = match.group(1).strip(), match.group(2).strip()
                # 따옴표 제거
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                data[k] = v
        return data

    def extract_code_blocks(self, body: str) -> List[Tuple[str, str, int]]:
        """
        코드 블록 추출: (language, code_text, start_line)
        """
        blocks = []
        lines = body.splitlines()
        in_block = False
        lang = ""
        current_block = []
        block_start = 0

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```") and not stripped.startswith("+```") and not stripped.startswith("-```"):
                if in_block:
                    blocks.append((lang, "\n".join(current_block), block_start))
                    in_block = False
                    current_block = []
                    lang = ""
                else:
                    in_block = True
                    lang = stripped[3:].strip()
                    block_start = idx
            elif in_block:
                current_block.append(line)

        return blocks

    # --------------------------------------------------------------------------
    # Gate 1: 구조 & 마크다운 무결성 검증
    # --------------------------------------------------------------------------
    def verify_gate_1_structure(self, file_path: str, content: str, fm_data: Dict[str, str], body: str, platform: str) -> List[Violation]:
        violations = []
        
        # 1. Frontmatter 필수 키 검증
        required_keys = ["title", "category", "tags"]
        if platform == "tistory":
            required_keys.append("visibility")
            
        for k in required_keys:
            if k not in fm_data or not fm_data[k].strip():
                violations.append(Violation(
                    gate_id="GATE_1",
                    gate_name="구조 및 메타데이터 무결성",
                    rule_id="G1_REQ_FRONTMATTER",
                    severity="REJECT",
                    line_number=1,
                    snippet=f"Missing key: '{k}'",
                    message=f"YAML Frontmatter에 필수 필드 '{k}'가 누락되었거나 비어 있습니다.",
                    fix_hint=f"파일 최상단 Frontmatter에 '{k}: <값>'을 명시하십시오."
                ))

        # 2. 코드 블록 백틱(```) 짝 맞춤 검증
        backtick_matches = [l for l in content.splitlines() if l.strip().startswith("```") and not l.strip().startswith("+```") and not l.strip().startswith("-```")]
        if len(backtick_matches) % 2 != 0:
            violations.append(Violation(
                gate_id="GATE_1",
                gate_name="구조 및 마크다운 무결성",
                rule_id="G1_UNCLOSED_CODEBLOCK",
                severity="REJECT",
                line_number=0,
                snippet=f"Total backtick rows: {len(backtick_matches)}",
                message="열린 코드 블록(```)이 닫히지 않았습니다. 백틱 개수가 홀수입니다.",
                fix_hint="마크다운 내 모든 ``` 블록이 정상적으로 닫혔는지 확인하십시오."
            ))

        # 3. 최소 분량 검증
        if platform == "dev":
            word_count = len(re.findall(r"\b[a-zA-Z0-9_\-]+\b", body))
            if word_count < 700:
                violations.append(Violation(
                    gate_id="GATE_1",
                    gate_name="구조 및 마크다운 무결성",
                    rule_id="G1_MIN_LENGTH_EN",
                    severity="REJECT",
                    line_number=0,
                    snippet=f"Current word count: {word_count} words",
                    message=f"글로벌 기술 백서의 최소 분량(700단어)에 미달합니다. (현재: {word_count}단어)",
                    fix_hint="에러 로그, 근본 커널 원인, 실패한 시도, 재현 CLI를 상세히 보강하여 전문성을 확보하십시오."
                ))
        else:
            char_count = len(body.replace(" ", "").replace("\n", ""))
            if char_count < 1200:
                violations.append(Violation(
                    gate_id="GATE_1",
                    gate_name="구조 및 마크다운 무결성",
                    rule_id="G1_MIN_LENGTH_KO",
                    severity="REJECT",
                    line_number=0,
                    snippet=f"Current char count: {char_count} chars (excl. spaces)",
                    message=f"국내 기술 블로그 최소 분량(공백 제외 1,200자)에 미달합니다. (현재: {char_count}자)",
                    fix_hint="충실한 기술적 설명과 단계별 예시, 비유를 보강하십시오."
                ))

        return violations

    # --------------------------------------------------------------------------
    # Gate 2: AI 클리셰 & 기계적 번역투 박멸 검증
    # --------------------------------------------------------------------------
    def verify_gate_2_anti_ai(self, lines: List[str], platform: str) -> List[Violation]:
        violations = []
        is_english = (platform == "dev")
        patterns = EN_AI_CLICHE_PATTERNS if is_english else KO_AI_CLICHE_PATTERNS

        # 코드 블록 내부 라인은 제외하고 본문 텍스트만 검사
        in_code_block = False
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            for pattern, severity, msg in patterns:
                match = re.search(pattern, line, re.IGNORECASE if is_english else 0)
                if match:
                    sev = "REJECT" if (severity == "REJECT" or self.strict_mode) else "WARNING"
                    violations.append(Violation(
                        gate_id="GATE_2",
                        gate_name="AI 클리셰 & 기계적 번역투 박멸",
                        rule_id="G2_AI_CLICHE",
                        severity=sev,
                        line_number=idx,
                        snippet=line.strip()[:100],
                        message=f"{msg} (탐지 패턴: '{pattern}')",
                        fix_hint="AI 특유의 진부한 미사여구를 삭제하고, 현업 엔지니어의 담백하고 직관적인 실무 표현으로 교체하십시오."
                    ))

        return violations

    # --------------------------------------------------------------------------
    # Gate 3: 억지 스토리 & 작위적 연출 차단 검증
    # --------------------------------------------------------------------------
    def verify_gate_3_no_forced_drama(self, lines: List[str], platform: str) -> List[Violation]:
        violations = []
        is_english = (platform == "dev")
        patterns = FORCED_DRAMA_PATTERNS_EN if is_english else FORCED_DRAMA_PATTERNS_KO

        in_code_block = False
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            for pattern, severity, msg in patterns:
                match = re.search(pattern, line, re.IGNORECASE if is_english else 0)
                if match:
                    violations.append(Violation(
                        gate_id="GATE_3",
                        gate_name="억지 스토리 & 작위적 연출 차단",
                        rule_id="G3_FORCED_DRAMA",
                        severity="REJECT",
                        line_number=idx,
                        snippet=line.strip()[:100],
                        message=msg,
                        fix_hint="가짜 위기 스토리(새벽 알람, 식은땀, 패닉 등)를 즉시 삭제하고, '실제 프로덕션에서 발생한 모니터링 수치/장애 증상'으로 객관화하십시오."
                    ))

        return violations

    # --------------------------------------------------------------------------
    # Gate 4: 실무 엔지니어링 5대 아티팩트 검증 (트러블슈팅/실무 포스트 전용)
    # --------------------------------------------------------------------------
    def verify_gate_4_engineering_artifacts(self, file_path: str, body: str, fm_data: Dict[str, str], platform: str) -> List[Violation]:
        violations = []
        fname = os.path.basename(file_path).lower()
        category = fm_data.get("category", "").lower()
        title = fm_data.get("title", "").lower()

        # 트러블슈팅 포스트 판별 (Track 1 dev 글 전체, Track 2 국문 트러블슈팅 글)
        is_trouble = (
            platform == "dev" or
            "trouble" in fname or
            "트러블슈팅" in category or
            "post-mortem" in category or
            "장애" in title or
            "트러블슈팅" in title
        )

        if not is_trouble:
            return violations  # 개념 입문서(Track 3)는 제외

        code_blocks = self.extract_code_blocks(body)

        # 1. Raw Log 검증 (에러/로그 패턴 존재 여부)
        has_raw_log = False
        log_keywords = [
            "error", "fatal", "exception", "failed", "panic:", "oomkilled",
            "timeout", "http/1.1 5", "http/2 5", "stderr:", "dmesg:", "status code 5",
            "502 bad gateway", "504 gateway timeout", "http 502", "http 504", "status code 502", "status code 504",
            "traceback (most recent call last):", "connection refused", "broken pipe",
            "deadlock", "latest detected deadlock", "waiting for this lock", "we roll back",
            "[trace]", "[metric]", "[alert]", "[critical]", "saturation", "iops",
            "exit code 13", "exit code 137", "exit code 1", "exit code 255", "sigkill", "sigterm", "sigbus", "sigsegv",
            "cannot assign requested address", "eaddrnotavail", "upstream prematurely closed", "upstream timed out",
            "에러", "실패", "타임아웃", "예외", "데드락", "종료코드"
        ]
        for lang, code, _ in code_blocks:
            code_lower = code.lower()
            if any(k in code_lower for k in log_keywords):
                has_raw_log = True
                break

        if not has_raw_log:
            violations.append(Violation(
                gate_id="GATE_4",
                gate_name="실무 엔지니어링 5대 아티팩트 검증",
                rule_id="G4_MISSING_RAW_LOG",
                severity="REJECT",
                line_number=0,
                snippet="No raw error stacktrace / kernel log block found in code blocks",
                message="[필수 아티팩트 결손] 날것의 시스템 에러 로그(Raw Log / Stacktrace) 블록이 존재하지 않습니다.",
                fix_hint="터미널이나 컨테이너 로그에서 발생한 실제 에러 로그 스택트레이스(Error, Exception, Failed 등)를 코드 블록으로 필수 삽입하십시오."
            ))

        # 2. Wrong Fix (오진/실패한 시도) 검증
        wrong_fix_keywords = [
            "wrong fix", "wrong approach", "initial incorrect", "failed attempt", "what didn't work",
            "what doesn't work", "common missteps", "misstep", "common false fix", "false fix",
            "the flawed fix", "flawed fix", "anti-pattern", "antipattern", "common anti-patterns",
            "what we tried first", "dangerous workaround", "dangerous workarounds", "why naive",
            "naive fix", "naive attempt", "why it fails", "why this fails", "why it backfires",
            "오진", "잘못된 접근", "실패했던 시도", "처음 시도했던", "오판", "삽질", "효과가 없었다", "해결되지 않았다",
            "초기 접근", "임시방편", "처음에는", "기대와 달리", "오류를 잡지 못했다"
        ]
        body_lower = body.lower()
        has_wrong_fix = any(k in body_lower for k in wrong_fix_keywords)

        if not has_wrong_fix:
            violations.append(Violation(
                gate_id="GATE_4",
                gate_name="실무 엔지니어링 5대 아티팩트 검증",
                rule_id="G4_MISSING_WRONG_FIX",
                severity="REJECT",
                line_number=0,
                snippet="No 'Wrong Fix' or failed troubleshooting attempt mentioned",
                message="[필수 아티팩트 결손] 처음 시도했으나 실패했던 잘못된 접근(Wrong Fix / 오진) 섹션이 누락되었습니다.",
                fix_hint="정답으로 직행하지 말고, '처음에는 X 설정을 변경했으나 왜 해결되지 않았는지' 현업의 오진/삽질 과정을 반드시 포함하십시오."
            ))

        # 3. Unified Diff (Before/After) 검증
        has_unified_diff = False
        for lang, code, _ in code_blocks:
            if lang.lower() == "diff":
                has_unified_diff = True
                break
            # 코드 내에 - 라인과 + 라인이 동시에 존재하는지 검사
            has_minus = bool(re.search(r"^\s*-\s+", code, re.MULTILINE))
            has_plus = bool(re.search(r"^\s*\+\s+", code, re.MULTILINE))
            if has_minus and has_plus:
                has_unified_diff = True
                break

        if not has_unified_diff:
            violations.append(Violation(
                gate_id="GATE_4",
                gate_name="실무 엔지니어링 5대 아티팩트 검증",
                rule_id="G4_MISSING_UNIFIED_DIFF",
                severity="REJECT",
                line_number=0,
                snippet="No unified diff (- / +) code block found",
                message="[필수 아티팩트 결손] Before/After 변경 내역을 명확히 대조하는 Unified Diff 블록이 없습니다.",
                fix_hint="```diff 형식으로 수정 전(-)과 수정 후(+)가 한눈에 대비되는 설정/코드 diff 블록을 삽입하십시오."
            ))

        # 4. Root Cause 분석 섹션 검증
        root_cause_keywords = [
            "root cause", "architectural cause", "kernel mechanism", "deep dive into",
            "원인 분석", "근본 원인", "동작 기전", "내부 동작", "발생 원인"
        ]
        has_root_cause = any(k in body_lower for k in root_cause_keywords)
        if not has_root_cause:
            violations.append(Violation(
                gate_id="GATE_4",
                gate_name="실무 엔지니어링 5대 아티팩트 검증",
                rule_id="G4_MISSING_ROOT_CAUSE",
                severity="WARNING",
                line_number=0,
                snippet="No explicit Root Cause / Architecture analysis header found",
                message="[개선 권장] 근본 원인(Root Cause)이나 커널/런타임 내부 동작 기전에 대한 심층 분석 헤더가 미흡합니다.",
                fix_hint="'## Root Cause Analysis' 또는 '## 장애의 근본 원인 분석' 섹션을 두어 내부 아키텍처 레벨의 원인을 설명하십시오."
            ))

        # 5. Verification CLI (재발 방지 및 검증 명령) 검증
        cli_commands = ["curl", "kubectl", "ss", "netstat", "tcpdump", "strace", "sysctl", "dmesg", "systemctl", "journalctl", "vmstat", "sar", "dig", "ping"]
        has_cli_verify = False
        for lang, code, _ in code_blocks:
            code_lower = code.lower()
            if any(re.search(rf"\b{cmd}\b", code_lower) for cmd in cli_commands):
                has_cli_verify = True
                break

        if not has_cli_verify:
            violations.append(Violation(
                gate_id="GATE_4",
                gate_name="실무 엔지니어링 5대 아티팩트 검증",
                rule_id="G4_MISSING_CLI_VERIFICATION",
                severity="WARNING",
                line_number=0,
                snippet="No verification CLI command (curl, ss, kubectl, sysctl, etc.) found in code blocks",
                message="[개선 권장] 수정 사항을 현장에서 즉시 검증할 수 있는 CLI 확인 명령어가 없습니다.",
                fix_hint="수정 후 상태를 검증하는 CLI 명령어(예: curl -v, ss -s, kubectl describe 등) 코드 블록을 추가하십시오."
            ))

        return violations

    # --------------------------------------------------------------------------
    # Gate 5: 사족 & 중언부언 차단 검증
    # --------------------------------------------------------------------------
    def verify_gate_5_anti_fluff(self, body: str, platform: str) -> List[Violation]:
        violations = []
        lines = body.splitlines()

        # 1. 서론 사족 비율 및 기술 밀도 검사 (첫 번째 H2 헤더 이전의 텍스트가 과도하게 긴지 검사)
        intro_lines = []
        for line in lines:
            if re.match(r"^#{1,3}\s+", line.strip()):
                break
            intro_lines.append(line)

        intro_text = "\n".join(intro_lines).strip()
        intro_words = re.findall(r"\b[a-zA-Z0-9_\-]+\b", intro_text)
        body_words = re.findall(r"\b[a-zA-Z0-9_\-]+\b", body)

        if len(body_words) > 0 and len(intro_words) > 250:
            intro_ratio = len(intro_words) / len(body_words)
            if intro_ratio > 0.30:
                violations.append(Violation(
                    gate_id="GATE_5",
                    gate_name="사족 & 중언부언 차단",
                    rule_id="G5_EXCESSIVE_INTRO_FLUFF",
                    severity="WARNING",
                    line_number=1,
                    snippet=intro_text[:120] + "...",
                    message=f"도입부 사족 비율이 전체 본문의 {int(intro_ratio * 100)}%로 과도하게 깁니다. ({len(intro_words)}단어)",
                    fix_hint="원론적인 배경 설명을 대폭 축소하고, 독자가 첫 화면에서 즉시 핵심 문제와 아키텍처를 파악할 수 있도록 바로 본론 헤더를 전진 배치하십시오."
                ))

        # 2. 판에 박힌 결론 재요약 (Parrot Conclusion) 패턴 검사
        last_section = "\n".join(lines[-40:]) if len(lines) >= 40 else body
        parrot_patterns = [
            (r"(지금까지\s+살펴본\s+바와\s+같이|위에서\s+살펴보았듯이|앞서\s+설명한\s+것처럼)", "결론부 상투적 중언부언"),
            (r"(as\s+we\s+have\s+seen\s+above|to\s+recap\s+what\s+we\s+discussed|in\s+this\s+article,\s*we\s+have\s+covered)", "Repetitive conclusion recap")
        ]
        for pattern, label in parrot_patterns:
            match = re.search(pattern, last_section, re.IGNORECASE)
            if match:
                violations.append(Violation(
                    gate_id="GATE_5",
                    gate_name="사족 & 중언부언 차단",
                    rule_id="G5_PARROT_CONCLUSION",
                    severity="WARNING",
                    line_number=0,
                    snippet=match.group(0),
                    message=f"단순 반복 재요약 패턴({label})이 감지되었습니다.",
                    fix_hint="앞서 설명한 내용을 기계적으로 다시 요약하지 말고, 현업 실무자를 위한 '운영 주의점'이나 '모니터링 알람 임계치 설정 팁'으로 실용적 가치를 더하십시오."
                ))

        # 3. Jaccard 유사도 기반 결론부 복제 검증 (Verbose Conclusion Index)
        sections = re.split(r"\n#{1,3}\s+", body)
        if len(sections) >= 3:
            conclusion_text = sections[-1]
            stop_words = {
                "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "by", "of",
                "this", "that", "is", "was", "are", "were", "it", "as", "be", "from", "we", "our",
                "you", "your", "will", "can", "not", "if", "when", "then", "into", "which", "all"
            }
            c_words = set(w.lower() for w in re.findall(r"[a-zA-Z0-9_\-]+", conclusion_text) if len(w) > 2 and w.lower() not in stop_words)
            if len(c_words) >= 20:
                for b_idx, b_sec in enumerate(sections[1:-1], start=1):
                    b_words = set(w.lower() for w in re.findall(r"[a-zA-Z0-9_\-]+", b_sec) if len(w) > 2 and w.lower() not in stop_words)
                    if len(b_words) >= 20:
                        intersection = len(c_words & b_words)
                        union = len(c_words | b_words)
                        jaccard = intersection / union if union > 0 else 0.0
                        if jaccard >= 0.65:
                            violations.append(Violation(
                                gate_id="GATE_5",
                                gate_name="사족 & 중언부언 차단",
                                rule_id="G5_JACCARD_REDUNDANCY",
                                severity="WARNING",
                                line_number=0,
                                snippet=f"Section {b_idx} vs Conclusion (Jaccard: {jaccard:.2f})",
                                message=f"결론부 내용이 본문 {b_idx}번 섹션과 자카드 유사도 {int(jaccard*100)}%로 지나치게 중복됩니다.",
                                fix_hint="결론부에서 본문 텍스트를 단순 복제/요약하지 말고, 차별화된 런북 및 체크리스트 가치를 제시하십시오."
                            ))
                            break

        return violations

    # --------------------------------------------------------------------------
    # Gate 6: 맞춤법, 오타 및 플랫폼별 특화 규격 검증
    # --------------------------------------------------------------------------
    def verify_gate_6_platform_compliance(self, file_path: str, body: str, fm_data: Dict[str, str], lines: List[str], platform: str) -> List[Violation]:
        violations = []
        category = fm_data.get("category", "").strip()

        # 1. 개발 블로그 (dev.ideaspot360.com) 카테고리 정규화 검증
        if platform == "dev":
            if category not in DEV_OFFICIAL_CATEGORIES:
                violations.append(Violation(
                    gate_id="GATE_6",
                    gate_name="플랫폼별 특화 규격 검증",
                    rule_id="G6_DEV_CATEGORY_MISMATCH",
                    severity="REJECT",
                    line_number=1,
                    snippet=f"category: {category}",
                    message=f"개발 블로그 공식 4대 카테고리와 불일치합니다. (허용: {', '.join(DEV_OFFICIAL_CATEGORIES)})",
                    fix_hint=f"Frontmatter의 category를 'Cloud & DevOps', 'Database & Storage', 'Systems & Networking', 'AI & Machine Learning' 중 하나로 정확히 일치시키십시오."
                ))

        # 2. 티스토리 (softwin.tistory.com) 카테고리 검증
        elif platform == "tistory":
            if category and category not in TISTORY_OFFICIAL_CATEGORIES:
                violations.append(Violation(
                    gate_id="GATE_6",
                    gate_name="플랫폼별 특화 규격 검증",
                    rule_id="G6_TISTORY_CATEGORY_MISMATCH",
                    severity="WARNING",
                    line_number=1,
                    snippet=f"category: {category}",
                    message=f"티스토리 11대 마스터 카테고리 또는 트러블슈팅 카테고리와 불일치할 수 있습니다. (지정: '{category}')",
                    fix_hint="CATEGORIES.md의 공식 11대 카테고리 명칭과 일치하는지 확인하십시오."
                ))

        # 3. 네이버 블로그 특화 검증 (의료법 위반 단어, 이미지 링크 표기, 해시태그)
        elif platform == "naver":
            is_health = ("infopiece" in file_path.lower() or "건강" in category or "영양" in category)
            
            # (1) 건강 블로그 의료법 위반 단어 100% 하드 블록
            if is_health:
                for idx, line in enumerate(lines, start=1):
                    # 법적 면책 고지 문구 부분(치료를 목적으로 하지 않음 등)만 국소 제거하여 오탐 방지하되, 나머지 본문 단어는 철저 검증
                    clean_line = re.sub(
                        r"(?:(?:특정\s*)?질병의\s*[^.\n]*?(?:치료|예방)[^.\n]*?(?:목적으로\s*하지\s*않[가-힣]*|의약품이\s*아니[가-힣]*|행위가\s*아니[가-힣]*)|"
                        r"의학적\s*(?:처방이나\s*)?치료\s*(?:행위가\s*아니[가-힣]*|를\s*대신[가-힣]*)|"
                        r"진단\s*및\s*치료를\s*대신[가-힣]*|"
                        r"질환\s*치료\s*(?:중[가-힣]*|를\s*받[가-힣]*))",
                        "",
                        line
                    )
                    for pattern, sev, msg in NAVER_HEALTH_FORBIDDEN:
                        match = re.search(pattern, clean_line)
                        if match:
                            violations.append(Violation(
                                gate_id="GATE_6",
                                gate_name="네이버 블로그 법적 규격 검증",
                                rule_id="G6_NAVER_MEDICAL_LAW",
                                severity="REJECT",
                                line_number=idx,
                                snippet=line.strip()[:100],
                                message=msg,
                                fix_hint="의료법 위반 소지가 있는 단어를 즉시 제거하고 식약처 공인 기능성 표현으로 수정하십시오."
                            ))

                # 법적 면책 고지(Disclaimer) 필수 포함 검증
                has_disclaimer = any(re.search(p, body) for p in HEALTH_DISCLAIMER_PATTERNS)
                if not has_disclaimer:
                    violations.append(Violation(
                        gate_id="GATE_6",
                        gate_name="네이버 블로그 법적 규격 검증",
                        rule_id="G6_NAVER_MISSING_DISCLAIMER",
                        severity="REJECT",
                        line_number=0,
                        snippet="No medical disclaimer found at the bottom",
                        message="[법적 방벽 결손] 건강/영양제 포스팅 최하단에 필수적인 '법적 면책 문구(Disclaimer)'가 누락되었습니다.",
                        fix_hint="포스팅 최하단에 '본 포스팅은 일반적인 정보 제공을 목적으로 하며, 전문 의료인의 진단 및 처방을 대신할 수 없습니다.'를 삽입하십시오."
                    ))

            # (2) 본문 내 이미지 마크다운 직접 삽입(![...]) 금지 및 링크 표기 강제
            img_tag_matches = re.findall(r"!\[(.*?)\]\((.*?)\)", body)
            if img_tag_matches:
                violations.append(Violation(
                    gate_id="GATE_6",
                    gate_name="네이버 블로그 조판 규격 검증",
                    rule_id="G6_NAVER_INLINE_IMAGE_FORBIDDEN",
                    severity="REJECT",
                    line_number=0,
                    snippet=f"Found {len(img_tag_matches)} inline markdown image tags (![...])",
                    message="네이버 블로그 본문 내에 직접 이미지(![...])를 띄우는 것이 금지되어 있습니다. (스마트에디터 수동 업로드 지원 규격 위반)",
                    fix_hint="본문에는 '[사진 X: 파일명](file:///...)' 형태의 클릭 가능한 로컬 링크만 남기십시오."
                ))

            # (3) 본문 최하단 인라인 해시태그 블록 필수 검증
            hashtag_match = re.search(r"#[가-힣a-zA-Z0-9_]+\s+#[가-힣a-zA-Z0-9_]+", body[-300:])
            if not hashtag_match:
                violations.append(Violation(
                    gate_id="GATE_6",
                    gate_name="네이버 블로그 조판 규격 검증",
                    rule_id="G6_NAVER_MISSING_HASHTAGS",
                    severity="WARNING",
                    line_number=0,
                    snippet="No inline #hashtag block found in the last 300 characters",
                    message="본문 최하단에 네이버 스마트에디터 ONE 자동 태그 완성용 '#태그1 #태그2 ...' 블록이 누락되었습니다.",
                    fix_hint="원고 맨 마지막 줄에 '#태그1 #태그2 #태그3 ...' 형태의 단일 인라인 해시태그를 추가하십시오."
                ))

        return violations

    # --------------------------------------------------------------------------
    # Gate 7: 보안 & 시크릿 누출 방벽 (Security & Secret Leak Prevention)
    # --------------------------------------------------------------------------
    def verify_gate_7_security(self, file_path: str, content: str, lines: List[str]) -> List[Violation]:
        violations = []

        dummy_tokens = {
            "your_api_key", "your-api-key", "your_token", "your-token",
            "example_token", "sample_key", "test_token", "placeholder",
            "xxx", "xxxx", "000000", "<token>", "<api_key>", "<api-key>",
            "my_secret", "dummy", "replace_with", "insert_here",
            "secret-key", "secret_key", "super-secure", "my-secret", "sample",
            "example", "demo", "tutorial", "test_key", "change-me", "changeme"
        }

        # 1. AWS Access Key ID
        for idx, line in enumerate(lines, start=1):
            aws_match = re.search(r"\bAKIA[0-9A-Z]{16}\b", line)
            if aws_match:
                matched_val = aws_match.group(0)
                if not any(d in matched_val.lower() for d in dummy_tokens):
                    violations.append(Violation(
                        gate_id="GATE_7",
                        gate_name="보안 & 시크릿 누출 방벽",
                        rule_id="G7_AWS_KEY_LEAK",
                        severity="REJECT",
                        line_number=idx,
                        snippet=matched_val,
                        message="[보안 위험] 실제 AWS Access Key ID 형식의 문자열이 감지되었습니다.",
                        fix_hint="실제 클라우드 자격 증명을 즉시 삭제하고, 환경변수(os.environ['AWS_ACCESS_KEY_ID']) 또는 'YOUR_AWS_ACCESS_KEY'와 같은 플레이스홀더로 대체하십시오."
                    ))

        # 2. GitHub Personal Access Token
        for idx, line in enumerate(lines, start=1):
            gh_match = re.search(r"\b(?:ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})\b", line)
            if gh_match:
                matched_val = gh_match.group(0)
                if not any(d in matched_val.lower() for d in dummy_tokens):
                    violations.append(Violation(
                        gate_id="GATE_7",
                        gate_name="보안 & 시크릿 누출 방벽",
                        rule_id="G7_GITHUB_TOKEN_LEAK",
                        severity="REJECT",
                        line_number=idx,
                        snippet=matched_val[:12] + "...",
                        message="[보안 위험] GitHub Personal Access Token(PAT) 형식의 문자열이 감지되었습니다.",
                        fix_hint="실제 GitHub 토큰을 즉시 폐기하고 더미 문자열로 교체하십시오."
                    ))

        # 3. Slack Webhook URL
        for idx, line in enumerate(lines, start=1):
            slack_match = re.search(r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+", line)
            if slack_match:
                violations.append(Violation(
                    gate_id="GATE_7",
                    gate_name="보안 & 시크릿 누출 방벽",
                    rule_id="G7_SLACK_WEBHOOK_LEAK",
                    severity="REJECT",
                    line_number=idx,
                    snippet=slack_match.group(0)[:35] + "...",
                    message="[보안 위험] 실제 슬랙 웹훅 URL(Slack Webhook URL)이 노출되었습니다.",
                    fix_hint="웹훅 URL을 삭제하고 'https://hooks.slack.com/services/T00/B00/XXXX' 형식의 마스킹된 주소를 사용하십시오."
                ))

        # 4. Private Key Headers
        for idx, line in enumerate(lines, start=1):
            pk_match = re.search(r"-----BEGIN (?:RSA|EC|DSA|OPENSSH|PGP|ENCRYPTED|PRIVATE) KEY-----", line)
            if pk_match:
                violations.append(Violation(
                    gate_id="GATE_7",
                    gate_name="보안 & 시크릿 누출 방벽",
                    rule_id="G7_PRIVATE_KEY_LEAK",
                    severity="REJECT",
                    line_number=idx,
                    snippet=pk_match.group(0),
                    message="[보안 위험] 비공개 암호화 키(Private Key) 헤더가 감지되었습니다.",
                    fix_hint="비공개 키 원문을 마크다운에 절대 삽입하지 마십시오."
                ))

        # 5. 하드코딩된 API Key/Secret 직접 할당문
        secret_assign_pat = re.compile(r"""(?i)\b(?:api_key|apikey|secret_key|client_secret|auth_token)\s*[:=]\s*["']([a-zA-Z0-9_\-\.]{24,})["']""")
        for idx, line in enumerate(lines, start=1):
            m = secret_assign_pat.search(line)
            if m:
                val = m.group(1)
                if not any(d in val.lower() for d in dummy_tokens):
                    violations.append(Violation(
                        gate_id="GATE_7",
                        gate_name="보안 & 시크릿 누출 방벽",
                        rule_id="G7_HARDCODED_SECRET",
                        severity="REJECT",
                        line_number=idx,
                        snippet=line.strip()[:80],
                        message="[보안 위험] 실제 API 키 또는 비밀 시크릿 토큰의 직접 할당문이 감지되었습니다.",
                        fix_hint="비밀번호나 API 키를 코드에 직접 하드코딩하지 말고 환경변수나 시크릿 매니저 참조 코드로 대체하십시오."
                    ))

        return violations

    # --------------------------------------------------------------------------
    # Gate 8: 법적 리스크 & 컴플라이언스 방벽 (Legal & Compliance Risk Gate)
    # --------------------------------------------------------------------------
    def verify_gate_8_legal_compliance(
        self,
        file_path: str,
        content: str,
        body: str,
        fm_data: Dict[str, str],
        lines: List[str],
        platform: str
    ) -> List[Violation]:
        violations: List[Violation] = []
        category = fm_data.get("category", "").strip()
        title = fm_data.get("title", "").strip()
        norm_path = file_path.replace("\\", "/").lower()

        # ----------------------------------------------------------------------
        # 1. 자본시장법 & 금융소비자보호법(금소법) 방벽 검증
        # ----------------------------------------------------------------------
        in_code_block = False
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block or not stripped:
                continue

            for pat, sev, rule_id, msg, hint in CAPITAL_MARKETS_RULES:
                match = re.search(pat, line)
                if match:
                    violations.append(Violation(
                        gate_id="GATE_8",
                        gate_name="자본시장법·금소법 방벽",
                        rule_id=rule_id,
                        severity=sev,
                        line_number=idx,
                        snippet=stripped[:100],
                        message=msg,
                        fix_hint=hint
                    ))

        # [1-2] 금융/투자/증시/재테크 포스팅 필수 투자 면책고지 검증
        is_kr_financial = (
            platform in ["stock"] or
            "stock.ideaspot360" in norm_path or
            ("stock" in norm_path and "posts" not in norm_path) or
            any(k in category for k in ["주식", "증시", "ETF", "금융", "재테크", "투자", "가상화폐", "암호화폐", "코인", "펀드", "채권", "커버드콜", "배당"]) or
            any(k in title for k in ["주식", "증시", "ETF", "재테크", "투자전략", "매수", "매도", "배당주", "커버드콜", "코스피", "나스닥 투자"])
        )
        if is_kr_financial:
            has_fin_disclaimer = any(re.search(p, body) for p in KO_FINANCIAL_DISCLAIMER_PATTERNS)
            if not has_fin_disclaimer:
                violations.append(Violation(
                    gate_id="GATE_8",
                    gate_name="자본시장법·금소법 방벽",
                    rule_id="G8_FIN_MISSING_DISCLAIMER",
                    severity="REJECT",
                    line_number=0,
                    snippet="No investment disclaimer found in financial content",
                    message="[자본시장법·금소법 방벽] 금융/증시/재테크 관련 포스팅 최하단에 필수적인 '투자 유의사항 및 면책고지(Disclaimer)'가 누락되었습니다.",
                    fix_hint="포스팅 최하단에 '본 글은 정보 제공을 목적으로 하며 특정 금융상품의 매수·매도를 권유하지 않습니다. 모든 투자의 책임과 원금 손실 위험은 투자자 본인에게 있습니다.'를 명시하십시오."
                ))

        # ----------------------------------------------------------------------
        # 2. 의료법 & 건강기능식품법(식품표시광고법) 방벽 검증
        # ----------------------------------------------------------------------
        in_code_block = False
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block or not stripped:
                continue

            for pat, sev, rule_id, msg, hint in MEDICAL_LAW_RULES:
                match = re.search(pat, line)
                if match:
                    violations.append(Violation(
                        gate_id="GATE_8",
                        gate_name="의료법·식품표시광고법 방벽",
                        rule_id=rule_id,
                        severity=sev,
                        line_number=idx,
                        snippet=stripped[:100],
                        message=msg,
                        fix_hint=hint
                    ))

        # [2-2] 건강/영양제/건기식 포스팅 필수 법적 면책고지 검증
        is_health = (
            "infopiece" in norm_path or
            any(k in category for k in ["건강", "영양", "건기식", "의학"]) or
            any(k in title for k in ["영양제", "마그네슘", "비타민", "오메가", "건강기능식품", "유산균", "콜라겐"])
        )
        if is_health:
            has_health_disclaimer = any(re.search(p, body) for p in HEALTH_DISCLAIMER_PATTERNS)
            if not has_health_disclaimer:
                violations.append(Violation(
                    gate_id="GATE_8",
                    gate_name="의료법·식품표시광고법 방벽",
                    rule_id="G8_MED_MISSING_DISCLAIMER",
                    severity="REJECT",
                    line_number=0,
                    snippet="No health/medical disclaimer found in health content",
                    message="[의료법·건기식법 방벽] 건강/영양제 포스팅 최하단에 필수적인 '법적 면책 문구(Disclaimer)'가 누락되었습니다.",
                    fix_hint="포스팅 최하단에 '본 포스팅은 일반적인 정보 제공을 목적으로 하며, 전문 의료인의 진단 및 처방을 대신할 수 없습니다. 질병의 예방 및 치료를 위한 의약품이 아닙니다.'를 삽입하십시오."
                ))

        # ----------------------------------------------------------------------
        # 3. 공정거래위원회 추천·보증 심사지침 준수 검증 (대가성 표시광고법)
        # ----------------------------------------------------------------------
        # 제휴 링크 또는 협찬 키워드 존재 시 검증
        has_affiliate_link = any(re.search(pat, body, re.IGNORECASE) for pat in AFFILIATE_LINK_PATTERNS)
        has_affiliate_kw = any(re.search(pat, body) for pat in AFFILIATE_KEYWORD_PATTERNS)

        if has_affiliate_link or has_affiliate_kw:
            # (1) 기만적 스텔스 마케팅/위장 광고 차단 (어휘 순서 무관)
            my_money_match = re.search(r"(?:내돈내산|직접\s*구매한|100%\s*자비)", body)
            if my_money_match:
                violations.append(Violation(
                    gate_id="GATE_8",
                    gate_name="공정위 표시광고법 방벽",
                    rule_id="G8_FTC_COVERT_MY_MONEY",
                    severity="REJECT",
                    line_number=0,
                    snippet=my_money_match.group(0),
                    message="[공정위 표시광고법 위반] 제휴 링크 또는 대가성 상업 활동이 포함되어 있으나 '내돈내산/자비 구매'로 소비자를 오도하는 기만적 스텔스 마케팅이 감지되었습니다.",
                    fix_hint="'내돈내산' 허위 표기를 삭제하고 공정위 표준 대가성 문구를 기재하십시오."
                ))

            not_ad_match = re.search(r"(?:광고|협찬)\s*(?:가\s*)?아닙니다", body)
            if not_ad_match:
                violations.append(Violation(
                    gate_id="GATE_8",
                    gate_name="공정위 표시광고법 방벽",
                    rule_id="G8_FTC_COVERT_NOT_AD",
                    severity="REJECT",
                    line_number=0,
                    snippet=not_ad_match.group(0),
                    message="[공정위 표시광고법 위반] 제휴 수수료 링크가 있으면서 '광고/협찬 아닙니다'라고 허위 주장하는 행위가 감지되었습니다.",
                    fix_hint="광고 부인 문구를 삭제하고 수수료 제공 사실을 명시하십시오."
                ))

            # (2) 대가성 공개 문구 필수 검증
            has_ftc_disclosure = any(re.search(pat, body) for pat in FTC_DISCLOSURE_PATTERNS)
            if not has_ftc_disclosure:
                violations.append(Violation(
                    gate_id="GATE_8",
                    gate_name="공정위 표시광고법 방벽",
                    rule_id="G8_FTC_MISSING_DISCLOSURE",
                    severity="REJECT",
                    line_number=0,
                    snippet="Affiliate links or sponsorship keywords detected without FTC disclosure",
                    message="[공정위 표시광고법 방벽] 제휴 링크(쿠팡 파트너스 등) 또는 대가성 상업 활동 내용이 포함되어 있으나, 공정거래위원회 「추천·보증 등에 관한 표시·광고 심사지침」에 따른 경제적 이해관계(대가성) 고지 문구가 누락되었습니다.",
                    fix_hint="포스팅 최상단 또는 최하단에 '이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.' 또는 '소정의 수수료를 제공받을 수 있습니다.'를 명시하십시오."
                ))

        # ----------------------------------------------------------------------
        # 4. 공공누리(KOGL) 저작권 출처 표기 의무 검증
        # ----------------------------------------------------------------------
        is_policy_content = (
            any(k in category for k in ["정부 정책", "복지 지원금", "복지정책", "행정 절차", "공공누리", "공공"]) or
            "solidlog" in norm_path or
            any(re.search(pat, title) for pat in POLICY_TOPIC_PATTERNS) or
            (any(re.search(pat, body) for pat in POLICY_TOPIC_PATTERNS) and
             bool(re.search(r"(?:신청\s*자격|지원\s*대상|소득\s*기준|신청\s*기간|신청\s*방법|지급\s*방식|선정\s*기준|구비\s*서류)", body)))
        )
        if is_policy_content:
            has_kogl_attribution = any(re.search(pat, body) for pat in KOGL_ATTRIBUTION_PATTERNS)
            if not has_kogl_attribution:
                violations.append(Violation(
                    gate_id="GATE_8",
                    gate_name="공공누리(KOGL) 출처 표기 방벽",
                    rule_id="G8_KOGL_MISSING_ATTRIBUTION",
                    severity="REJECT",
                    line_number=0,
                    snippet="Government policy or welfare content found without KOGL attribution",
                    message="[공공누리(KOGL) 출처 표기 방벽] 정부 정책, 복지 지원금 또는 공공기관 저작물 정보가 포함되어 있으나, 저작권법 제37조 및 공공누리(KOGL) 출처 표기 의무가 누락되었습니다.",
                    fix_hint="포스팅 최하단에 '출처: 대한민국 정책브리핑 (공공누리 제1유형: 출처표시)' 또는 '본 저작물은 공공누리 제1유형에 따라 작성되었습니다.'를 명시하십시오."
                ))

        # ----------------------------------------------------------------------
        # 5. 영문 법적 리스크 (SEC 투자 자문 위반 및 글로벌 금융 규제) 검증
        # ----------------------------------------------------------------------
        in_code_block = False
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block or not stripped:
                continue

            for pat, sev, rule_id, msg, hint in GLOBAL_FINANCIAL_RULES:
                match = re.search(pat, line)
                if match:
                    violations.append(Violation(
                        gate_id="GATE_8",
                        gate_name="영문 글로벌 금융 규제 방벽 (SEC Compliance)",
                        rule_id=rule_id,
                        severity=sev,
                        line_number=idx,
                        snippet=stripped[:100],
                        message=msg,
                        fix_hint=hint
                    ))

        # [5-2] 영문 금융/시장/매크로 포스팅 글로벌 면책문구 누락 검증
        is_en_financial = (
            platform in ["markets"] or
            "markets" in norm_path or
            (platform == "dev" and any(k in category.lower() for k in ["finance", "market", "macro", "quant", "stock", "trading", "investment"])) or
            (bool(re.search(r"(?i)\b(?:s&p\s*500|nasdaq|treasury\s+yield|fed\s+liquidity|equity\s+market|stock\s+market|quantitative\s+trading|macroeconomic)\b", body)) and
             len(re.findall(r"[가-힣]", body[:500])) == 0)
        )
        if is_en_financial:
            has_global_disclaimer = any(re.search(pat, body) for pat in GLOBAL_DISCLAIMER_PATTERNS)
            if not has_global_disclaimer:
                violations.append(Violation(
                    gate_id="GATE_8",
                    gate_name="영문 글로벌 금융 규제 방벽 (SEC Compliance)",
                    rule_id="G8_GLOBAL_MISSING_DISCLAIMER",
                    severity="REJECT",
                    line_number=0,
                    snippet="No global financial disclaimer found in English financial content",
                    message="[SEC Global Compliance] English financial/market article lacks a mandatory global investment disclaimer.",
                    fix_hint="Add standard disclaimer at the bottom: 'Disclaimer: This article is for informational and educational purposes only and does not constitute financial, investment, or legal advice. Past performance is not indicative of future results.'"
                ))

        return violations

    # --------------------------------------------------------------------------
    # 🚀 마스터 통합 검증 실행기 (Master Verification Method)
    # --------------------------------------------------------------------------
    def verify(self, file_path: str, platform_override: Optional[str] = None) -> GateReport:
        path_obj = Path(file_path)
        if not path_obj.exists():
            return GateReport(
                file_path=file_path,
                platform="unknown",
                is_passed=False,
                score=0,
                reject_count=1,
                warning_count=0,
                violations=[Violation(
                    gate_id="GATE_0",
                    gate_name="파일 접근성",
                    rule_id="G0_FILE_NOT_FOUND",
                    severity="REJECT",
                    line_number=0,
                    snippet=file_path,
                    message="지정된 파일을 찾을 수 없습니다.",
                    fix_hint="파일 경로가 정확한지 확인하십시오."
                )]
            )

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        platform = platform_override or self.detect_platform(file_path, content)
        fm_text, body, body_start_line = self.split_frontmatter_and_body(content)
        fm_data = self.parse_frontmatter(fm_text)
        lines = content.splitlines()

        violations: List[Violation] = []

        # Gate 1: 구조 및 메타데이터 무결성
        violations.extend(self.verify_gate_1_structure(file_path, content, fm_data, body, platform))

        # Gate 2: AI 클리셰 & 기계적 번역투 박멸
        violations.extend(self.verify_gate_2_anti_ai(lines, platform))

        # Gate 3: 억지 스토리 & 작위적 연출 차단
        violations.extend(self.verify_gate_3_no_forced_drama(lines, platform))

        # Gate 4: 실무 엔지니어링 5대 아티팩트 검증
        violations.extend(self.verify_gate_4_engineering_artifacts(file_path, body, fm_data, platform))

        # Gate 5: 사족 & 중언부언 차단
        violations.extend(self.verify_gate_5_anti_fluff(body, platform))

        # Gate 6: 플랫폼별 특화 규격
        violations.extend(self.verify_gate_6_platform_compliance(file_path, body, fm_data, lines, platform))

        # Gate 7: 보안 & 시크릿 누출 방벽
        violations.extend(self.verify_gate_7_security(file_path, content, lines))

        # Gate 8: 법적 리스크 & 컴플라이언스 방벽 (자본시장법·금소법, 의료법·건기식법, 공정위 표시광고법, 공공누리 KOGL, 영문 SEC/글로벌 규제)
        violations.extend(self.verify_gate_8_legal_compliance(file_path, content, body, fm_data, lines, platform))

        # 점수 계산 및 판정
        reject_count = sum(1 for v in violations if v.severity == "REJECT")
        warning_count = sum(1 for v in violations if v.severity == "WARNING")

        score = max(0, 100 - (reject_count * 25) - (warning_count * 5))
        is_passed = (reject_count == 0)

        return GateReport(
            file_path=file_path,
            platform=platform,
            is_passed=is_passed,
            score=score,
            reject_count=reject_count,
            warning_count=warning_count,
            violations=violations
        )


# ==============================================================================
# 📢 리포트 출력 및 하드 블록(Hard Block) 실행 함수
# ==============================================================================
def print_gate_report(report: GateReport, show_hints: bool = True):
    """검증 결과를 터미널에 미려한 ANSI 박스로 출력."""
    status_color = Color.GREEN if report.is_passed else Color.RED
    status_text = "PASSED (발행 승인)" if report.is_passed else "REJECTED (발행 원천 차단)"

    print("\n" + "=" * 80)
    print(f"🛡️  {Color.BOLD}철벽 게이트 검증 보고서 (Ironclad Gatekeeper Report){Color.RESET}")
    print("=" * 80)
    print(f"📄 대상 파일: {Color.CYAN}{report.file_path}{Color.RESET}")
    print(f"🌐 타깃 플랫폼: {Color.YELLOW}{report.platform.upper()}{Color.RESET}")
    print(f"⚖️  최종 판정: {status_color}{Color.BOLD}[{status_text}]{Color.RESET}")
    print(f"📈 품질 점수: {Color.BOLD}{report.score}/100{Color.RESET} (치명적 결함: {Color.RED}{report.reject_count}건{Color.RESET}, 경고: {Color.YELLOW}{report.warning_count}건{Color.RESET})")
    print("-" * 80)

    if not report.violations:
        print(f"{Color.GREEN}✨ 축하합니다! 단 하나의 결함도 발견되지 않은 완전무결한 콘텐츠입니다.{Color.RESET}")
        print("=" * 80 + "\n")
        return

    for idx, v in enumerate(report.violations, start=1):
        sev_color = Color.RED if v.severity == "REJECT" else Color.YELLOW
        line_info = f"Line {v.line_number}" if v.line_number > 0 else "전체/글로벌"
        print(f"\n{sev_color}{Color.BOLD}[{v.severity}] #{idx} {v.gate_id} ({v.gate_name}) - {line_info}{Color.RESET}")
        print(f"  🔍 사유: {v.message}")
        if v.snippet:
            print(f"  📝 원문: {Color.WHITE}\"{v.snippet}\"{Color.RESET}")
        if show_hints and v.fix_hint:
            print(f"  💡 교정 팁: {Color.GREEN}{v.fix_hint}{Color.RESET}")

    print("\n" + "=" * 80)
    if not report.is_passed:
        print(f"{Color.BG_RED}{Color.WHITE}{Color.BOLD} ❌ HARD BLOCK: 품질 기준 미달로 인해 글 발행 파이프라인이 물리적으로 중단됩니다. {Color.RESET}")
        print(f"{Color.RED}위 REJECT 항목을 100% 해소한 후 다시 발행 명령을 실행하십시오.{Color.RESET}")
    else:
        print(f"{Color.GREEN}✅ 검증 통과: 발행 시스템으로 작업을 안전하게 인계합니다.{Color.RESET}")
    print("=" * 80 + "\n")


def verify_or_abort(file_path: str, platform: Optional[str] = None, strict: bool = False, show_hints: bool = True):
    """
    글 발행 시스템(create_post.py, publish_to_dev.py 등) 연동용 함수.
    검증 실패 시 즉각 sys.exit(1)을 호출하여 후속 발행 트랜잭션을 물리적으로 차단함.
    """
    gatekeeper = IroncladGatekeeper(strict_mode=strict)
    report = gatekeeper.verify(file_path, platform_override=platform)
    print_gate_report(report, show_hints=show_hints)

    if not report.is_passed:
        sys.exit(1)

    return report


# ==============================================================================
# 🧪 내장 자체 단위 테스트 스위트 (Self-Test Suite)
# ==============================================================================
def run_self_test():
    """다른 에이전트가 본 파일을 복제한 직후 자가 무결성을 검증할 수 있는 테스트 스위트."""
    print("\n🧪 [철벽 게이트 검증 시스템 내장 Self-Test 시작]")
    gatekeeper = IroncladGatekeeper()

    # Case 1: AI 클리셰 포함 케이스 (영문) -> REJECT 기대
    bad_en = """---
title: "Test AI Post"
category: "Cloud & DevOps"
tags: "k8s, dev"
---
In the modern cloud landscape, we must delve into kubernetes issues.
By doing so, the cluster becomes immune to failures.
Here is the exact diagnostic breakdown.
"""
    # 임시 파일 없이 메모리 상 직접 테스트 위해 임시 저장
    temp_dir = Path("scratch")
    temp_dir.mkdir(exist_ok=True)
    temp_bad_en = temp_dir / "_test_bad_en.md"
    temp_bad_en.write_text(bad_en, encoding="utf-8")

    report1 = gatekeeper.verify(str(temp_bad_en), platform_override="dev")
    assert not report1.is_passed, "Case 1: Bad EN AI clichés should be REJECTED"
    assert any(v.rule_id == "G2_AI_CLICHE" for v in report1.violations), "Case 1: Should detect AI cliché"
    print("  ✅ Test 1 Passed: Bad English AI Clichés caught successfully.")

    # Case 2: 억지 스토리 포함 케이스 (국문) -> REJECT 기대
    bad_drama_ko = """---
title: "새벽 장애 일지"
category: "백엔드 & 서버 아키텍처"
tags: "spring"
visibility: "public"
---
새벽 3시 40분, 비상 호출이 울렸다.
등줄기에 식은땀이 흘렀고 머릿속이 하얘졌다.
패닉에 빠진 채로 로그를 보았다.
"""
    temp_bad_drama = temp_dir / "_test_bad_drama.md"
    temp_bad_drama.write_text(bad_drama_ko, encoding="utf-8")

    report2 = gatekeeper.verify(str(temp_bad_drama), platform_override="tistory")
    assert not report2.is_passed, "Case 2: Forced drama should be REJECTED"
    assert any(v.rule_id == "G3_FORCED_DRAMA" for v in report2.violations), "Case 2: Should detect forced drama"
    print("  ✅ Test 2 Passed: Forced Drama Story caught successfully.")

    # Case 3: 네이버 건강 블로그 의료법 위반 단어 -> REJECT 기대
    bad_health_naver = """---
title: "마그네슘 복용법"
category: "건강"
tags: "마그네슘"
---
이 영양제는 불면증 완치와 고혈압 치료에 특효약입니다.
"""
    temp_bad_health = temp_dir / "_test_bad_health.md"
    temp_bad_health.write_text(bad_health_naver, encoding="utf-8")

    report3 = gatekeeper.verify(str(temp_bad_health), platform_override="naver")
    assert not report3.is_passed, "Case 3: Medical claim in health blog should be REJECTED"
    assert any(v.rule_id == "G6_NAVER_MEDICAL_LAW" for v in report3.violations), "Case 3: Medical law violation caught"
    print("  ✅ Test 3 Passed: Naver Medical Law violation caught successfully.")

    # Case 4: 코드 블록 백틱 홀수 (닫히지 않은 코드) -> REJECT 기대
    bad_codeblock = """---
title: "Unclosed Code"
category: "Systems & Networking"
tags: "linux"
---
```bash
echo "Hello"
"""
    temp_bad_code = temp_dir / "_test_bad_code.md"
    temp_bad_code.write_text(bad_codeblock, encoding="utf-8")

    report4 = gatekeeper.verify(str(temp_bad_code), platform_override="dev")
    assert not report4.is_passed, "Case 4: Unclosed code block should be REJECTED"
    assert any(v.rule_id == "G1_UNCLOSED_CODEBLOCK" for v in report4.violations), "Case 4: Unclosed code caught"
    print("  ✅ Test 4 Passed: Unclosed Code Block caught successfully.")

    # Case 5: 보안 시크릿 누출 (AWS Key) -> REJECT 기대
    bad_secret = """---
title: "AWS Credentials Guide"
category: "Cloud & DevOps"
tags: "aws"
---
AWS_KEY = "AKIA1234567890ABCDEF"
"""
    temp_bad_secret = temp_dir / "_test_bad_secret.md"
    temp_bad_secret.write_text(bad_secret, encoding="utf-8")

    report5 = gatekeeper.verify(str(temp_bad_secret), platform_override="dev")
    assert not report5.is_passed, "Case 5: Security secret leak should be REJECTED"
    assert any(v.gate_id == "GATE_7" for v in report5.violations), "Case 5: Gate 7 secret leak caught"
    print("  ✅ Test 5 Passed: Security & Secrets leak caught successfully.")

    # Case 6: 자본시장법 & 금소법 위반 (원금보장, 확정수익, 리딩방) -> REJECT 기대
    # (동일 라인에 면책문구를 혼합 삽입한 지능형 우회 시도 차단 검증 포함)
    bad_finance = """---
title: "특급 급등주 추천 및 확정 수익 비법"
category: "금융 & 재테크"
tags: "주식, 재테크"
---
이번에 발굴한 세력 매집주는 무조건 폭등하며 원금 보장과 함께 연 30% 확정 수익을 약속합니다. 투자의 최종 책임은 본인에게 있습니다.
VIP 리딩방에서만 제공하는 극비 정보주이므로 지금 당장 풀매수하세요.
"""
    temp_bad_fin = temp_dir / "_test_bad_fin.md"
    temp_bad_fin.write_text(bad_finance, encoding="utf-8")

    report6 = gatekeeper.verify(str(temp_bad_fin), platform_override="tistory")
    assert not report6.is_passed, "Case 6: Capital Markets & Consumer Protection violations should be REJECTED"
    assert any("G8_FIN_" in v.rule_id for v in report6.violations), "Case 6: Should detect Capital Markets & Consumer Protection violations"
    assert any(v.rule_id == "G8_FIN_PRINCIPAL_GUARANTEE" for v in report6.violations), "Case 6: Should detect principal guarantee even with disclaimer on same line"
    assert any(v.rule_id == "G8_FIN_CONFIRMED_PROFIT" for v in report6.violations), "Case 6: Should detect confirmed profit"
    print("  ✅ Test 6 Passed: Capital Markets & Financial Consumer Protection Law violations caught successfully.")

    # Case 7: 의료법 & 건강기능식품법 위반 (의약품 오인, 처방약 중단, 의료인 사칭) -> REJECT 기대
    # (동일 라인에 '의약품이 아닙니다' 면책 어구를 혼합한 우회 시도 차단 검증 포함)
    bad_medical = """---
title: "기적의 천연 치료제로 당뇨 잡는 법"
category: "건강"
tags: "당뇨, 영양제"
---
현직 의사로서 보증하건대, 이 성분은 인슐린 약 대신 복용할 수 있는 기적의 천연 치료제입니다. 본 제품은 질병 치료를 목적으로 하지 않으며 의약품이 아닙니다.
기존 병원 처방약을 끊고 이 건강기능식품만 섭취하면 체지방 100% 분해와 함께 완치됩니다.
"""
    temp_bad_med = temp_dir / "_test_bad_med.md"
    temp_bad_med.write_text(bad_medical, encoding="utf-8")

    report7 = gatekeeper.verify(str(temp_bad_med), platform_override="naver")
    assert not report7.is_passed, "Case 7: Medical law & drug confusion claims should be REJECTED"
    assert any("G8_MED_" in v.rule_id for v in report7.violations), "Case 7: Should detect medical law violations"
    assert any(v.rule_id == "G8_MED_NATURAL_MEDICINE" for v in report7.violations), "Case 7: Should detect natural medicine claim"
    assert any(v.rule_id == "G8_MED_STOP_PRESCRIPTION" for v in report7.violations), "Case 7: Should detect stopping prescription"
    assert any(v.rule_id == "G8_MED_IMPERSONATION_PROFESSIONAL" for v in report7.violations), "Case 7: Should detect medical impersonation"
    print("  ✅ Test 7 Passed: Medical Law & Health Functional Food Law violations caught successfully.")

    # Case 8: 공정거래위원회 추천·보증 심사지침 위반 (제휴 링크 있으나 대가성 고지 누락 및 기만적 스텔스 마케팅) -> REJECT 기대
    # (제휴 링크가 상단에 있고 내돈내산이 하단에 배치된 역순 기만 광고 차단 검증 포함)
    bad_ftc = """---
title: "내돈내산 무선 마우스 솔직 후기"
category: "IT / 소프트웨어 리뷰"
tags: "마우스, IT리뷰"
---
# 가성비 최고 무선 마우스 사용기

제품 구매 링크: https://link.coupang.com/a/bCdEf1234
쿠팡 파트너스 추천 상품으로 적극 권장합니다.
직접 구매해서 3달간 써본 솔직한 내돈내산 후기입니다. 광고 아닙니다.
"""
    temp_bad_ftc = temp_dir / "_test_bad_ftc.md"
    temp_bad_ftc.write_text(bad_ftc, encoding="utf-8")

    report8 = gatekeeper.verify(str(temp_bad_ftc), platform_override="tistory")
    assert not report8.is_passed, "Case 8: Missing FTC disclosure and covert ad should be REJECTED"
    assert any(v.rule_id == "G8_FTC_MISSING_DISCLOSURE" for v in report8.violations), "Case 8: Should detect missing FTC disclosure"
    assert any(v.rule_id == "G8_FTC_COVERT_MY_MONEY" for v in report8.violations), "Case 8: Should detect deceptive covert marketing"
    print("  ✅ Test 8 Passed: FTC Affiliate & Sponsored Advertising compliance caught successfully.")

    # Case 9: 공공누리(KOGL) 저작권 출처 표기 누락 (정부 지원금/정책 글에서 출처 미표기) -> REJECT 기대
    bad_kogl = """---
title: "2026 청년도약계좌 지원 조건 및 신청 방법 총정리"
category: "정부 정책 / 복지 지원금"
tags: "청년도약계좌, 정부지원금"
---
# 2026 청년도약계좌 완벽 가이드

보건복지부와 서민금융진흥원에서 발표한 2026년 청년도약계좌 정부 지원금 정책 안내입니다.
정부 지원금 매칭 혜택과 비과세 혜택을 통해 5천만 원의 목돈을 마련할 수 있습니다.
신청 자격은 만 19세~34세 청년이며 총급여 7,500만 원 이하입니다.
"""
    temp_bad_kogl = temp_dir / "_test_bad_kogl.md"
    temp_bad_kogl.write_text(bad_kogl, encoding="utf-8")

    report9 = gatekeeper.verify(str(temp_bad_kogl), platform_override="naver")
    assert not report9.is_passed, "Case 9: Missing KOGL attribution should be REJECTED"
    assert any(v.rule_id == "G8_KOGL_MISSING_ATTRIBUTION" for v in report9.violations), "Case 9: Should detect missing KOGL attribution"
    print("  ✅ Test 9 Passed: KOGL Public Copyright attribution requirement verified successfully.")

    # Case 10: 영문 글로벌 금융 규제 위반 (SEC Investment Advice & Guaranteed Return) -> REJECT 기대
    bad_sec = """---
title: "Guaranteed Profit Trading Strategy"
category: "Global Macro & Finance"
tags: "trading, stocks"
---
# S&P 500 High-Frequency Strategy

This quantitative model delivers a guaranteed return of 45% with risk-free profit.
Buy this stock now before market close today. It has a 100% win rate and cannot lose money.
"""
    temp_bad_sec = temp_dir / "_test_bad_sec.md"
    temp_bad_sec.write_text(bad_sec, encoding="utf-8")

    report10 = gatekeeper.verify(str(temp_bad_sec), platform_override="markets")
    assert not report10.is_passed, "Case 10: Global financial/SEC violations should be REJECTED"
    assert any(v.rule_id == "G8_GLOBAL_GUARANTEED_RETURNS" for v in report10.violations), "Case 10: Should detect guaranteed returns"
    assert any(v.rule_id == "G8_GLOBAL_URGENT_BUY_CALL" for v in report10.violations), "Case 10: Should detect direct buy command"
    assert any(v.rule_id == "G8_GLOBAL_MISSING_DISCLAIMER" for v in report10.violations), "Case 10: Should detect missing global financial disclaimer"

    # 동일 라인에 면책문구를 혼합 삽입한 우회 시도 차단 추가 검증
    sec_evasion_text = "This quantitative system delivers a guaranteed profit of 45%. This is for informational purposes only and not financial advice."
    sec_evasion_lines = [sec_evasion_text]
    sec_evasion_v = gatekeeper.verify_gate_8_legal_compliance(
        file_path="test_sec_evasion.md",
        content=sec_evasion_text,
        body=sec_evasion_text,
        fm_data={"category": "Finance", "title": "Trading"},
        lines=sec_evasion_lines,
        platform="markets"
    )
    assert any(v.rule_id == "G8_GLOBAL_GUARANTEED_RETURNS" for v in sec_evasion_v), "Case 10-2: Guaranteed profit must be caught even with disclaimer on same line"
    print("  ✅ Test 10 Passed: English SEC & Global Financial compliance violations caught successfully.")

    # Case 11: 법적 규정 100% 준수한 정상 콘텐츠 통과 검증 (Clean Compliant Post) -> PASS 기대
    # 1. KOGL 정책 공공 저작물 정상 포스트
    compliant_policy = """---
title: "2026 청년 자산 형성 정책 분석 가이드"
category: "정부 정책 / 복지 지원금"
tags: "청년도약계좌, 정책금융"
---
# 2026 청년 자산 형성 지원 정책 분석

본 포스팅은 대한민국 정부의 청년 금융 지원 복지 정책 구조를 객관적으로 분석합니다.
소득 구간별 정부기여금 매칭과 우대 금리 요건을 꼼꼼히 확인하여 자산 형성 계획을 수립해야 합니다.

신청 전 서민금융진흥원 및 취급 시중은행의 공식 공고를 확인하시기 바랍니다.

---
출처: 대한민국 정책브리핑 (공공누리 제1유형: 출처표시)

※ 본 글은 금융 지원 정책 이해를 돕기 위한 객관적 정보 제공용이며, 특정 금융회사나 금융투자상품 가입을 권유하지 않습니다.
"""
    cp_fm_text, cp_body, _ = gatekeeper.split_frontmatter_and_body(compliant_policy)
    cp_fm = gatekeeper.parse_frontmatter(cp_fm_text)
    cp_v = gatekeeper.verify_gate_8_legal_compliance(
        file_path="posts/test_compliant_policy.md",
        content=compliant_policy,
        body=cp_body,
        fm_data=cp_fm,
        lines=compliant_policy.splitlines(),
        platform="naver"
    )
    assert len(cp_v) == 0, f"Case 11-1: Compliant policy post should have 0 Gate 8 legal violations, found: {cp_v}"

    # 2. 식약처 고시 건기식 표준 면책문구 포스트
    compliant_health = """---
title: "마그네슘 흡수율 비교 분석"
category: "건강"
tags: "마그네슘"
---
# 마그네슘 형태별 생체이용률 과학

식약처 고시 기준에 따른 마그네슘 형태별 체내 흡수 메커니즘을 객관적으로 분석합니다.
킬레이트 마그네슘과 산화 마그네슘의 용해도 차이를 인체적용시험 데이터로 비교합니다.

---
※ 본 제품은 질병의 예방 및 치료를 위한 의약품이 아니며, 건강 증진을 위한 건강기능식품 정보입니다. 전문 의료인의 진단 및 처방을 대신할 수 없습니다.
"""
    ch_fm_text, ch_body, _ = gatekeeper.split_frontmatter_and_body(compliant_health)
    ch_fm = gatekeeper.parse_frontmatter(ch_fm_text)
    ch_v = gatekeeper.verify_gate_8_legal_compliance(
        file_path="posts/test_compliant_health.md",
        content=compliant_health,
        body=ch_body,
        fm_data=ch_fm,
        lines=compliant_health.splitlines(),
        platform="naver"
    )
    assert len(ch_v) == 0, f"Case 11-2: Compliant health post should have 0 Gate 8 legal violations, found: {ch_v}"

    # 3. 글로벌 영문 제휴 링크 & FTC 면책고지 준수 포스트
    compliant_ftc_en = """---
title: "Top Developer Keyboards"
category: "Cloud & DevOps"
tags: "hardware, dev"
---
# Essential Hardware for Engineers

A detailed review of ergonomic mechanical keyboards for infrastructure engineers.
Product link: https://amzn.to/3xyz123

Disclosure: This post contains affiliate links. As an Amazon Associate I earn from qualifying purchases at no additional cost to you.
"""
    ce_fm_text, ce_body, _ = gatekeeper.split_frontmatter_and_body(compliant_ftc_en)
    ce_fm = gatekeeper.parse_frontmatter(ce_fm_text)
    ce_v = gatekeeper.verify_gate_8_legal_compliance(
        file_path="blogs/dev/_posts/test_compliant_ftc.md",
        content=compliant_ftc_en,
        body=ce_body,
        fm_data=ce_fm,
        lines=compliant_ftc_en.splitlines(),
        platform="dev"
    )
    assert len(ce_v) == 0, f"Case 11-3: Compliant English affiliate post should have 0 Gate 8 legal violations, found: {ce_v}"

    # 4. 개발 블로그의 Portfolio Dashboard 튜토리얼 (금융 글 오탐 방지 검증)
    compliant_dev_portfolio = """---
title: "Building a Portfolio Dashboard with FastAPI"
category: "Cloud & DevOps"
tags: "fastapi, python"
---
# Building a Portfolio Dashboard

In this engineering tutorial, we implement an asynchronous worker pipeline to aggregate user metrics with FastAPI and Redis.
We deploy the containerized cluster across multiple availability zones.
"""
    cd_fm_text, cd_body, _ = gatekeeper.split_frontmatter_and_body(compliant_dev_portfolio)
    cd_fm = gatekeeper.parse_frontmatter(cd_fm_text)
    cd_v = gatekeeper.verify_gate_8_legal_compliance(
        file_path="blogs/dev/_posts/test_portfolio.md",
        content=compliant_dev_portfolio,
        body=cd_body,
        fm_data=cd_fm,
        lines=compliant_dev_portfolio.splitlines(),
        platform="dev"
    )
    assert len(cd_v) == 0, f"Case 11-4: Dev coding tutorial with 'portfolio' should have 0 Gate 8 legal violations, found: {cd_v}"

    print("  ✅ Test 11 Passed: Fully compliant legal & regulatory content verified across all domains with 0 violations.")

    # 임시 파일 정리
    all_temp_files = [
        temp_bad_en, temp_bad_drama, temp_bad_health, temp_bad_code, temp_bad_secret,
        temp_bad_fin, temp_bad_med, temp_bad_ftc, temp_bad_kogl, temp_bad_sec
    ]
    for p in all_temp_files:
        if p.exists():
            p.unlink()

    print(f"\n{Color.GREEN}{Color.BOLD}🎉 ALL 11 SELF-TESTS PASSED: 철벽 게이트 검증 엔진의 8대 품질 및 법적 컴플라이언스 룰이 100% 정상 동작합니다!{Color.RESET}\n")


# ==============================================================================
# 💻 CLI 실행 진입점 (Command Line Interface)
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="🏛️ 철벽 게이트 검증 시스템 CLI (Ironclad Gatekeeper)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
[사용 예시]
  1. 단건 글 정밀 검증:
     python ironclad_gatekeeper.py --file posts/70_trouble_example.md
  2. 개발 블로그 영문 글 검증:
     python ironclad_gatekeeper.py --file blogs/dev/_posts/2026-11-23-example.md --platform dev
  3. 특정 디렉터리 내 전체 글 일괄 검사:
     python ironclad_gatekeeper.py --dir posts/
  4. 내장 자체 무결성 단위 테스트:
     python ironclad_gatekeeper.py --self-test
  5. JSON 결과 출력:
     python ironclad_gatekeeper.py --file posts/70_trouble_example.md --json
        """
    )

    parser.add_argument("--file", "-f", help="검증할 마크다운 파일 경로")
    parser.add_argument("--dir", "-d", help="검증할 마크다운 디렉터리 경로 (내부 .md 일괄 검증)")
    parser.add_argument("--platform", "-p", choices=["auto", "dev", "tistory", "naver", "markets", "stock", "gear"], default="auto", help="타깃 플랫폼 (기본값: auto)")
    parser.add_argument("--strict", action="store_true", help="엄격 모드 (WARNING도 REJECT로 취급)")
    parser.add_argument("--self-test", action="store_true", help="내장 자체 단위 테스트 실행")
    parser.add_argument("--json", action="store_true", help="결과를 JSON 포맷으로 출력")
    parser.add_argument("--no-hints", action="store_true", help="교정 팁 출력 생략")

    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    gatekeeper = IroncladGatekeeper(strict_mode=args.strict)
    platform_override = None if args.platform == "auto" else args.platform

    # 단건 파일 검증
    if args.file:
        report = gatekeeper.verify(args.file, platform_override=platform_override)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        else:
            print_gate_report(report, show_hints=(not args.no_hints))
        sys.exit(0 if report.is_passed else 1)

    # 디렉터리 일괄 검증
    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"❌ 디렉터리를 찾을 수 없습니다: {args.dir}")
            sys.exit(1)

        files = list(dir_path.glob("*.md")) + list(dir_path.glob("**/*.md"))
        # 중복 제거
        files = sorted(list(set(files)))
        if not files:
            print(f"⚠️ 디렉터리 내에 .md 파일이 없습니다: {args.dir}")
            sys.exit(0)

        print(f"\n📂 총 {len(files)}개 마크다운 파일 일괄 철벽 검증 시작...")
        reports: List[GateReport] = []
        fail_count = 0

        for f in files:
            rep = gatekeeper.verify(str(f), platform_override=platform_override)
            reports.append(rep)
            if not rep.is_passed:
                fail_count += 1
                if not args.json:
                    print_gate_report(rep, show_hints=(not args.no_hints))

        if args.json:
            print(json.dumps([r.to_dict() for r in reports], indent=2, ensure_ascii=False))
        else:
            print("\n" + "=" * 60)
            print(f"📊 [일괄 검증 종합 결과: 총 {len(files)}편]")
            print(f"  - 통과: {Color.GREEN}{len(files) - fail_count}편{Color.RESET}")
            print(f"  - 차단: {Color.RED}{fail_count}편{Color.RESET}")
            print("=" * 60 + "\n")

        sys.exit(0 if fail_count == 0 else 1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
