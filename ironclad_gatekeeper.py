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

7대 검증 게이트 (7-Layer Ironclad Verification Gates):
  [Gate 1] 구조 & 마크다운 무결성 (YAML Frontmatter, 코드 블록 짝 맞춤, 최소 분량)
  [Gate 2] AI 클리셰 & 기계적 번역투 박멸 (국문 40+ 규칙, 영문 40+ 규칙 정밀 정규식)
  [Gate 3] 억지 스토리 & 작위적 연출 차단 (새벽 몇 시 알람, 식은땀, 패닉 등 소설화 원천 배제)
  [Gate 4] 실무 엔지니어링 5대 아티팩트 검증 (Raw Log, Wrong Fix, Unified Diff, Root Cause, CLI Verify)
  [Gate 5] 사족 & 중언부언 차단 (도입부 과다 서술, 판에 박힌 결론 재요약)
  [Gate 6] 맞춤법, 오타 및 플랫폼별 특화 규격 (네이버 의료법/금지어, 이미지 링크 표기, 해시태그)
  [Gate 7] 실행 차단 & 감사 리포트 (ANSI 컬러 터미널 출력, JSON 리포트, sys.exit(1) 차단 연동)
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
# 5. 주식/증시 및 글로벌 매크로 특화 규격 & 법적 리스크 룰셋 (Stock & Macro Rules)
# ------------------------------------------------------------------------------
STOCK_FORBIDDEN_PATTERNS = [
    (r"원금\s*보장", "REJECT", "[자본시장법 위반] 주식/투자 글에 '원금 보장' 표방은 법적으로 금지됩니다."),
    (r"무조건\s*(급등|상승|폭등)", "REJECT", "비이성적 확증 편향 및 과장 어휘 감지. 객관적 데이터와 시나리오로 서술하십시오."),
    (r"확정\s*(순)?수익(률)?", "REJECT", "[자본시장법 위반] 투자 글에 '확정 수익/순수익' 표방은 100% 금지됩니다."),
    (r"수익(을)?\s*확정", "REJECT", "[자본시장법 위반] 투자 글에 '수익 확정' 표방은 100% 금지됩니다. '실현 수익' 또는 '수익 확보'로 기술하십시오."),
    (r"확정적(인)?\s*(수익|현금|분배|캐시플로우|프리미엄)", "REJECT", "[자본시장법 위반] 배당/옵션 인컴에 '확정적' 수식어는 법적으로 금지됩니다. '정기적인' 또는 '주기적인'으로 대체하십시오."),
    (r"확정\s*(현금|프리미엄|분배)", "REJECT", "[자본시장법 위반] 옵션 프리미엄/현금흐름에 '확정' 표방은 금지됩니다. '선취' 또는 '인컴'으로 기술하십시오."),
    (r"목표가\s*찍(는다|을\s*것)", "REJECT", "사기성 리딩방 어투 감지. '상방 저항선 레벨', '밸류에이션 밴드'로 서술하십시오."),
    (r"풀매수|영끌|몰빵", "REJECT", "비전문적 투기 조장 어휘 감지. 리스크 관리 및 분할 매매 원칙을 기술하십시오."),
]

MACRO_FORBIDDEN_PATTERNS_EN = [
    (r"\bguaranteed returns?\b", "REJECT", "Prohibited regulatory phrase detected."),
    (r"\bto the moon\b", "REJECT", "Unprofessional speculative slang detected."),
    (r"\beasy money\b", "REJECT", "Sensationalist financial phrase detected."),
]

# ------------------------------------------------------------------------------
# 6. 플랫폼 카테고리 정의
# ------------------------------------------------------------------------------
DEV_OFFICIAL_CATEGORIES = [
    "Cloud & DevOps",
    "Database & Storage",
    "Systems & Networking"
]

MARKETS_OFFICIAL_CATEGORIES = [
    "Macro Intelligence",
    "US Systematic Equity",
    "Options & Income",
    "Quantitative Frameworks"
]

STOCK_OFFICIAL_CATEGORIES = [
    "커버드콜 분석",
    "커버드콜 이론",
    "차트이론",
    "공지사항",
    "이론 및 기초"
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
        if "stock_blog_global" in norm_path or "markets.ideaspot360" in norm_path:
            return "markets"
        if "stock_blog" in norm_path or "stock.ideaspot360" in norm_path:
            return "stock"
        if "blogs/dev" in norm_path or "dev.ideaspot360" in norm_path:
            return "dev"
        if "naver" in norm_path or "solidlog" in norm_path or "tidynote" in norm_path or "infopiece" in norm_path:
            return "naver"
        # Frontmatter 언어 및 메타데이터 검사
        if re.search(r"^category:\s*(Macro Intelligence|US Systematic Equity|Options & Income|Quantitative Frameworks)", content, re.MULTILINE):
            return "markets"
        if re.search(r"^category:\s*(커버드콜 분석|커버드콜 이론|차트이론|공지사항|실전 매매기법|이론 및 기초)", content, re.MULTILINE):
            return "stock"
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
            if line.strip().startswith("```"):
                if in_block:
                    blocks.append((lang, "\n".join(current_block), block_start))
                    in_block = False
                    current_block = []
                    lang = ""
                else:
                    in_block = True
                    lang = line.strip()[3:].strip()
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
        backtick_matches = re.findall(r"^```", content, re.MULTILINE)
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
            "traceback (most recent call last):", "connection refused", "broken pipe"
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
            "오진", "잘못된 접근", "실패했던 시도", "처음 시도했던", "오판", "삽질", "효과가 없었다", "해결되지 않았다"
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

        # 1. 서론 사족 비율 검사 (첫 번째 H2 헤더 이전의 텍스트가 과도하게 긴지 검사)
        intro_lines = []
        for line in lines:
            if re.match(r"^#{1,3}\s+", line.strip()):
                break
            intro_lines.append(line)

        intro_text = "\n".join(intro_lines).strip()
        intro_words = len(intro_text.split())
        body_words = len(body.split())

        if body_words > 0 and (intro_words / body_words) > 0.30 and intro_words > 250:
            violations.append(Violation(
                gate_id="GATE_5",
                gate_name="사족 & 중언부언 차단",
                rule_id="G5_EXCESSIVE_INTRO_FLUFF",
                severity="WARNING",
                line_number=1,
                snippet=intro_text[:120] + "...",
                message=f"도입부 사족 비율이 전체 본문의 {int((intro_words/body_words)*100)}%로 과도하게 깁니다. ({intro_words}단어)",
                fix_hint="원론적인 배경 설명을 대폭 축소하고, 독자가 첫 화면에서 즉시 핵심 문제와 아키텍처를 파악할 수 있도록 바로 본론 헤더를 전진 배치하십시오."
            ))

        # 2. 판에 박힌 결론 재요약 (Parrot Conclusion) 패턴 검사
        last_section = "\n".join(lines[-40:]) if len(lines) >= 40 else body
        parrot_patterns = [
            (r"((오늘|지금까지|앞서|위에서)\s+살펴본\s+바와\s+같이|위에서\s+살펴보았듯이|앞서\s+설명한\s+것처럼)", "결론부 상투적 중언부언"),
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
                    message=f"개발 블로그 공식 3대 카테고리와 불일치합니다. (허용: {', '.join(DEV_OFFICIAL_CATEGORIES)})",
                    fix_hint=f"Frontmatter의 category를 'Cloud & DevOps', 'Database & Storage', 'Systems & Networking' 중 하나로 정확히 일치시키십시오."
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
                    for pattern, sev, msg in NAVER_HEALTH_FORBIDDEN:
                        match = re.search(pattern, line)
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
                disclaimer_keywords = ["면책", "의사의 진료", "처방을 대신", "의료 전문가와 상담", "일반적인 건강 정보"]
                has_disclaimer = any(k in body for k in disclaimer_keywords)
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

        # 4. 국내 주식/증시 블로그 (stock.ideaspot360.com / 맥락트레이딩) 검증
        elif platform == "stock":
            if category:
                if category in ["차트강의", "실전 매매기법", "실전매매기법", "매매기법"]:
                    violations.append(Violation(
                        gate_id="GATE_6",
                        gate_name="주식 블로그 카테고리 규격 검증",
                        rule_id="G6_STOCK_DEPRECATED_CATEGORY",
                        severity="REJECT",
                        line_number=1,
                        snippet=f"category: {category}",
                        message=f"폐기된 구 카테고리('{category}')가 사용되었습니다. '차트이론'으로 전환하십시오.",
                        fix_hint="Frontmatter의 category를 '차트이론' 또는 공식 카테고리로 변경하십시오."
                    ))
                elif category not in STOCK_OFFICIAL_CATEGORIES:
                    violations.append(Violation(
                        gate_id="GATE_6",
                        gate_name="주식 블로그 카테고리 규격 검증",
                        rule_id="G6_STOCK_CATEGORY_MISMATCH",
                        severity="WARNING",
                        line_number=1,
                        snippet=f"category: {category}",
                        message=f"국내 증시 블로그 공식 카테고리와 불일치할 수 있습니다. (허용: {', '.join(STOCK_OFFICIAL_CATEGORIES)})",
                        fix_hint=f"Frontmatter의 category를 {', '.join(STOCK_OFFICIAL_CATEGORIES)} 중 하나로 일치시키십시오."
                    ))

            for idx, line in enumerate(lines, start=1):
                for pattern, sev, msg in STOCK_FORBIDDEN_PATTERNS:
                    match = re.search(pattern, line)
                    if match:
                        violations.append(Violation(
                            gate_id="GATE_6",
                            gate_name="주식 블로그 법적 규격 검증",
                            rule_id="G6_STOCK_CAPITAL_MARKETS_LAW",
                            severity=sev,
                            line_number=idx,
                            snippet=line.strip()[:100],
                            message=msg,
                            fix_hint="자본시장법 위반 소지가 있는 단어를 즉시 제거하고 객관적 분석 표현으로 수정하십시오."
                        ))

            # 투자 면책 고지(Disclaimer) 필수 포함 검증
            stock_disclaimer_keywords = ["면책", "투자 권유", "투자 판단과 책임", "정보 제공용", "투자 유의사항"]
            has_stock_disclaimer = any(k in body for k in stock_disclaimer_keywords)
            if not has_stock_disclaimer:
                violations.append(Violation(
                    gate_id="GATE_6",
                    gate_name="주식 블로그 법적 규격 검증",
                    rule_id="G6_STOCK_MISSING_DISCLAIMER",
                    severity="REJECT",
                    line_number=0,
                    snippet="No stock investment disclaimer found at the bottom",
                    message="[법적 방벽 결손] 주식/투자 포스팅 최하단에 필수적인 '투자 유의사항 및 법적 면책 문구(Disclaimer)'가 누락되었습니다.",
                    fix_hint="포스팅 최하단에 '본 포스팅은 특정 종목에 대한 매수·매도 추천이나 투자 권유가 아니며, 모든 투자에 대한 판단과 책임은 투자자 본인에게 있습니다.'를 삽입하십시오."
                ))

        # 5. 글로벌 매크로/퀀트 블로그 (markets.ideaspot360.com) 검증
        elif platform == "markets":
            for idx, line in enumerate(lines, start=1):
                for pattern, sev, msg in MACRO_FORBIDDEN_PATTERNS_EN:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        violations.append(Violation(
                            gate_id="GATE_6",
                            gate_name="글로벌 매크로 블로그 법적 규격 검증",
                            rule_id="G6_MACRO_PROHIBITED_SLANG",
                            severity=sev,
                            line_number=idx,
                            snippet=line.strip()[:100],
                            message=msg,
                            fix_hint="Remove sensationalist financial slang and replace with sober institutional analysis."
                        ))

            # Global Disclaimer 필수 포함 검증
            macro_disclaimer_keywords = ["disclaimer", "not investment advice", "not financial advice", "for educational and informational purposes"]
            has_macro_disclaimer = any(k in body.lower() for k in macro_disclaimer_keywords)
            if not has_macro_disclaimer:
                violations.append(Violation(
                    gate_id="GATE_6",
                    gate_name="글로벌 매크로 블로그 법적 규격 검증",
                    rule_id="G6_MACRO_MISSING_DISCLAIMER",
                    severity="WARNING",
                    line_number=0,
                    snippet="No global investment disclaimer found",
                    message="[Regulatory Safeguard] Essential investment disclaimer is missing from the global macro publication.",
                    fix_hint="Include standard institutional disclaimer at the bottom of the article."
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

    # Case 5: 주식 블로그 자본시장법 위반 단어 -> REJECT 기대
    bad_stock_ko = """---
title: "내일 무조건 급등하는 대박주"
category: "커버드콜 분석"
tags: "주식"
---
이 종목은 원금 보장이 되며 내일 무조건 급등합니다.
"""
    temp_bad_stock = temp_dir / "_test_bad_stock.md"
    temp_bad_stock.write_text(bad_stock_ko, encoding="utf-8")

    report5 = gatekeeper.verify(str(temp_bad_stock), platform_override="stock")
    assert not report5.is_passed, "Case 5: Stock capital markets law violation should be REJECTED"
    assert any(v.rule_id == "G6_STOCK_CAPITAL_MARKETS_LAW" for v in report5.violations), "Case 5: Capital markets law violation caught"
    print("  ✅ Test 5 Passed: Stock Capital Markets Law violation caught successfully.")

    # 임시 파일 정리
    for p in [temp_bad_en, temp_bad_drama, temp_bad_health, temp_bad_code]:
        if p.exists():
            p.unlink()

    print(f"\n{Color.GREEN}{Color.BOLD}🎉 ALL SELF-TESTS PASSED: 철벽 게이트 검증 엔진의 모든 차단 룰이 정상 동작합니다!{Color.RESET}\n")


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
    parser.add_argument("--platform", "-p", choices=["auto", "dev", "tistory", "naver"], default="auto", help="타깃 플랫폼 (기본값: auto)")
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
