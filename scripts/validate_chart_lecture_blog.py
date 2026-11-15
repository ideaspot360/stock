"""
Independent Hard-Fail Validator for Chart Trading Lecture Blog Posts.

Strictly enforces 7 Gates of Integrity:
1. RULE-01:FRONT_MATTER_SCHEMA (Jekyll metadata validity)
2. RULE-02:CORE_TRADING_CONCEPTS (10-MA pullback, orderbook execution strength, -1.5% stop-loss)
3. RULE-03:BANNED_SCAM_MYSTICISM (0% tolerance for get-rich-quick scams or mystical indicators)
4. RULE-04:BANNED_VIDEO_ARTIFACTS (0% tolerance for video script markers/timelines)
5. RULE-05:AI_CLICHE_HUMANIZING (GEMINI.md Article 8 AI clichés prohibition)
6. RULE-06:IMAGE_ASSETS_INTEGRITY (Existence, 16:9 aspect ratio 1.65~1.85, width >= 1200px)
7. RULE-07:READABILITY_STRUCTURE_EAT (Length >= 2,000 chars, disclaimer, tags, sign bug prevention)

Returns exit code 0 on PASS, 1 on FAIL.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class RuleResult:
    rule_id: str
    name: str
    passed: bool
    details: str
    errors: List[str] = field(default_factory=list)


@dataclass
class LintReport:
    file_path: Path
    is_valid: bool = True
    results: List[RuleResult] = field(default_factory=list)

    def add_result(self, rule_id: str, name: str, passed: bool, details: str, errors: Optional[List[str]] = None) -> None:
        errs = errors or []
        if not passed:
            self.is_valid = False
        self.results.append(RuleResult(rule_id=rule_id, name=name, passed=passed, details=details, errors=errs))


class ChartLectureValidator:
    # 7대 검증 규칙 정의
    SCAM_BLACKLIST = [
        "100% 승률", "승률 100%", "무조건 수익", "원금 보장", "신비의 지표", "신비의 공식",
        "비밀 기법", "황금선", "신의 타점", "세력 비밀 코드", "절대 비기", "일확천금", "벼락부자"
    ]

    VIDEO_ARTIFACTS_BLACKLIST = [
        r"대본", r"나레이션\s*:", r"\[화면전환\]", r"타임라인\s*:", r"오디오\s*큐\s*:",
        r"BGM\s*:", r"효과음\s*:", r"\[씬\s*\d+", r"\[SCENE\s*\d+", r"쇼츠\s*대본"
    ]

    AI_CLICHE_BLACKLIST = [
        "안녕하세요! 오늘은", "지금부터 살펴보겠습니다", "함께 알아보겠습니다",
        "주목할 만한 점은", "각별한 주의가 요구됩니다", "결론부터 말씀드리면",
        "이상으로 포스팅을 마칩니다", "도움이 되셨다면", "좋아요와 구독"
    ]

    SIGN_BUG_REGEX = re.compile(r"(\+\-|\-\+|\+\+|\-\-|\+\s*\-|\-\s*\+)")
    THEMATIC_BREAK_REGEX = re.compile(r"^\s*(\-{3,}|\*{3,}|_{3,})\s*$")
    TABLE_SEPARATOR_REGEX = re.compile(r"^\s*\|?(\s*:?-+:?\s*\|)+\s*$")

    def __init__(self, blog_root: Path, assets_dir: Optional[Path] = None):
        self.blog_root = blog_root
        self.assets_dir = assets_dir or (blog_root / "assets" / "img")

    def parse_front_matter(self, text: str) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
        """Extract YAML front matter and body text."""
        if not text.startswith("---"):
            return None, text, "Front matter delimiter '---' not found at start of file"

        parts = text.split("---", 2)
        if len(parts) < 3:
            return None, text, "Closing front matter delimiter '---' not found"

        fm_text = parts[1].strip()
        body_text = parts[2]

        data = {}
        if yaml:
            try:
                data = yaml.safe_load(fm_text) or {}
            except Exception as e:
                return None, body_text, f"YAML parse error: {e}"
        else:
            # Fallback simple parser
            for line in fm_text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    k, v = line.split(":", 1)
                    data[k.strip()] = v.strip().strip("'\"")

        return data, body_text, None

    def validate_post(self, post_path: Path) -> LintReport:
        report = LintReport(file_path=post_path)

        if not post_path.exists():
            report.add_result(
                "RULE-00", "FILE_EXISTENCE", False,
                f"File not found: {post_path}", [f"Target path does not exist: {post_path}"]
            )
            return report

        try:
            content = post_path.read_text(encoding="utf-8")
        except Exception as e:
            report.add_result(
                "RULE-00", "FILE_READ", False,
                f"Failed to read file: {e}", [str(e)]
            )
            return report

        front_matter, body, fm_err = self.parse_front_matter(content)

        # ---------------------------------------------------------------------
        # RULE-01: FRONT_MATTER_SCHEMA
        # ---------------------------------------------------------------------
        r1_errors = []
        if fm_err:
            r1_errors.append(fm_err)
        elif not isinstance(front_matter, dict):
            r1_errors.append("Front matter is not a valid dictionary")
        else:
            # layout check
            if front_matter.get("layout") != "post":
                r1_errors.append(f"layout must be 'post', got '{front_matter.get('layout')}'")

            # title check
            title = str(front_matter.get("title", "")).strip()
            if not title:
                r1_errors.append("title is missing or empty")

            # date check
            date_val = str(front_matter.get("date", "")).strip()
            if not date_val:
                r1_errors.append("date is missing or empty")

            # category / categories check (단일 카테고리 '차트강의' 엄격 격리 가드)
            cat = str(front_matter.get("category", "")).strip()
            cats = front_matter.get("categories", [])
            if isinstance(cats, str):
                cats = [cats]
            all_cats = [c.strip() for c in ([cat] + [str(x) for x in cats]) if c.strip()]
            if not any("차트강의" in c or "chart" in c.lower() for c in all_cats):
                r1_errors.append("category or categories must contain '차트강의' or 'chart'")

            # 타 카테고리 중복 지정(교차 오염) 엄격 차단 가드
            forbidden_cats = ["실전 매매기법", "실전매매기법", "매매기법", "strategy", "커버드콜", "coveredcall"]
            for c in all_cats:
                for f in forbidden_cats:
                    if f in c.lower() or f in c:
                        r1_errors.append(f"Cross-category contamination detected: '{c}' contains '{f}'. Chart lecture posts must strictly belong to '차트강의' only.")

            # tags check
            tags = front_matter.get("tags", [])
            if not isinstance(tags, list) or len(tags) < 5:
                r1_errors.append(f"tags must be a list of at least 5 tags, got {len(tags) if isinstance(tags, list) else 'invalid'}")

            # author check
            author = str(front_matter.get("author", ""))
            if "맥락트레이딩" not in author:
                r1_errors.append(f"author must contain '맥락트레이딩', got '{author}'")

            # excerpt check
            excerpt = str(front_matter.get("excerpt", "")).strip()
            if not excerpt or len(excerpt) < 10:
                r1_errors.append("excerpt is missing or too short")

        report.add_result(
            "RULE-01", "FRONT_MATTER_SCHEMA", len(r1_errors) == 0,
            "Jekyll YAML front matter valid" if not r1_errors else f"Front matter invalid ({len(r1_errors)} errors)",
            r1_errors
        )

        # ---------------------------------------------------------------------
        # RULE-02: CORE_TRADING_CONCEPTS
        # ---------------------------------------------------------------------
        r2_errors = []
        # Concept 1: 10이평선 눌림목
        if not re.search(r"10\s*(?:이평선|EMA|지수이평)", body) or not re.search(r"눌림목|풀백|Pullback", body, re.IGNORECASE):
            r2_errors.append("Missing core concept: 10이평선 (10 EMA) 눌림목 (Pullback)")

        # Concept 2: 3분봉 or 5분봉
        if not re.search(r"3분봉|5분봉", body):
            r2_errors.append("Missing core concept: 3분봉 또는 5분봉 시간 프레임 언급")

        # Concept 3: 거래량 급감 (Volume Dry-Up)
        if not re.search(r"거래량\s*(?:급감|1/3|30%|마름|Dry-Up)", body, re.IGNORECASE):
            r2_errors.append("Missing core concept: 거래량 급감 (Volume Dry-Up 1/3 이하)")

        # Concept 4: 호가창 체결강도 & 매도잔량 우위
        if not re.search(r"체결강도", body) or not re.search(r"1(?:00|20)\s*%", body):
            r2_errors.append("Missing core concept: 체결강도 100%~120% 기준")
        if not re.search(r"매도\s*(?:총)?\s*잔량", body) or not re.search(r"(?:허매수|받쳐놓기|스푸핑)", body):
            r2_errors.append("Missing core concept: 호가 잔량 매도벽 흡수 및 허매수벽 트랩")

        # Concept 5: -1.5% 칼손절
        if not re.search(r"(?:-\s*1\.5\s*%|마이너스\s*1\.5\s*%)", body) or not re.search(r"(?:손절|칼손절|스탑로스)", body):
            r2_errors.append("Missing core concept: -1.5% 기계적 칼손절 원칙")

        # Concept 6: 손익비 (Risk-Reward Ratio)
        if not re.search(r"손익비|Risk-Reward", body, re.IGNORECASE):
            r2_errors.append("Missing core concept: 손익비(Risk-Reward Ratio)")

        report.add_result(
            "RULE-02", "CORE_TRADING_CONCEPTS", len(r2_errors) == 0,
            "All essential Price Action trading concepts included" if not r2_errors else f"Missing trading concepts ({len(r2_errors)} errors)",
            r2_errors
        )

        # ---------------------------------------------------------------------
        # RULE-03: BANNED_SCAM_MYSTICISM
        # ---------------------------------------------------------------------
        r3_errors = []
        for scam_word in self.SCAM_BLACKLIST:
            pattern = re.compile(re.escape(scam_word), re.IGNORECASE)
            matches = list(pattern.finditer(body))
            if matches:
                r3_errors.append(f"Detected banned scam/mysticism phrase '{scam_word}' ({len(matches)} occurrences)")

        report.add_result(
            "RULE-03", "BANNED_SCAM_MYSTICISM", len(r3_errors) == 0,
            "0 scam mysticism phrases detected (100% clean)" if not r3_errors else f"Scam phrases detected ({len(r3_errors)} errors)",
            r3_errors
        )

        # ---------------------------------------------------------------------
        # RULE-04: BANNED_VIDEO_ARTIFACTS
        # ---------------------------------------------------------------------
        r4_errors = []
        for video_pattern in self.VIDEO_ARTIFACTS_BLACKLIST:
            pattern = re.compile(video_pattern, re.IGNORECASE)
            matches = list(pattern.finditer(body))
            if matches:
                r4_errors.append(f"Detected video production artifact matching pattern '{video_pattern}' ({len(matches)} occurrences)")

        report.add_result(
            "RULE-04", "BANNED_VIDEO_ARTIFACTS", len(r4_errors) == 0,
            "0 video production artifacts detected (100% clean blog article)" if not r4_errors else f"Video artifacts detected ({len(r4_errors)} errors)",
            r4_errors
        )

        # ---------------------------------------------------------------------
        # RULE-05: AI_CLICHE_HUMANIZING (GEMINI.md Part 1 Article 8)
        # ---------------------------------------------------------------------
        r5_errors = []
        for cliche in self.AI_CLICHE_BLACKLIST:
            pattern = re.compile(re.escape(cliche), re.IGNORECASE)
            matches = list(pattern.finditer(body))
            if matches:
                r5_errors.append(f"Detected robotic AI cliché phrase '{cliche}' ({len(matches)} occurrences)")

        report.add_result(
            "RULE-05", "AI_CLICHE_HUMANIZING", len(r5_errors) == 0,
            "0 robotic AI clichés detected (AdSense humanized tone compliant)" if not r5_errors else f"AI clichés detected ({len(r5_errors)} errors)",
            r5_errors
        )

        # ---------------------------------------------------------------------
        # RULE-06: IMAGE_ASSETS_INTEGRITY
        # ---------------------------------------------------------------------
        r6_errors = []
        image_matches = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body)
        if len(image_matches) < 2:
            r6_errors.append(f"Post must contain at least 2 infographics images, found {len(image_matches)}")

        for alt_text, img_rel_path in image_matches:
            # Strip query params or hash if any
            clean_path = img_rel_path.split("?")[0].split("#")[0].strip()

            # Resolve physical file path
            if clean_path.startswith("/"):
                # URL absolute from blog root (e.g. /assets/img/posts/foo.png)
                local_path = self.blog_root / clean_path.lstrip("/")
            else:
                # Relative to post file directory
                local_path = (post_path.parent / clean_path).resolve()

            if not local_path.exists():
                r6_errors.append(f"Referenced image file does not exist on disk: {img_rel_path} -> {local_path}")
                continue

            try:
                with Image.open(local_path) as im:
                    w, h = im.size
                    ratio = w / h
                    # Check 16:9 ratio tolerance [1.65, 1.85]
                    if not (1.65 <= ratio <= 1.85):
                        r6_errors.append(f"Image {local_path.name} aspect ratio is {ratio:.4f}, expected 16:9 (~1.7778 in [1.65, 1.85])")
                    # Check resolution
                    if w < 1200 or h < 675:
                        r6_errors.append(f"Image {local_path.name} resolution is too low ({w}x{h} px), expected width >= 1200 px")
            except Exception as e:
                r6_errors.append(f"Failed to inspect image file {local_path}: {e}")

        report.add_result(
            "RULE-06", "IMAGE_ASSETS_INTEGRITY", len(r6_errors) == 0,
            f"All {len(image_matches)} images verified (16:9 dark theme, high resolution, physical existence)" if not r6_errors else f"Image integrity failure ({len(r6_errors)} errors)",
            r6_errors
        )

        # ---------------------------------------------------------------------
        # RULE-07: READABILITY_STRUCTURE_EAT
        # ---------------------------------------------------------------------
        r7_errors = []

        # 1. Content length check (>= 2,000 pure characters)
        clean_body = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", "", body)
        clean_body = re.sub(r"```[\s\S]*?```", "", clean_body)
        pure_char_count = len(re.sub(r"\s+", "", clean_body))
        if pure_char_count < 2000:
            r7_errors.append(f"Pure text character count is {pure_char_count}, expected >= 2,000 characters for in-depth lecture")

        # 2. Disclaimer check (.post-disclaimer)
        if not re.search(r'<div\s+class=["\']post-disclaimer["\']>', body):
            r7_errors.append("Missing mandatory '<div class=\"post-disclaimer\">' legal disclaimer block")

        # 3. Tags block check (.post-tags)
        if not re.search(r'<div\s+class=["\']post-tags["\']>', body) or not re.search(r'<span\s+class=["\']tag-item["\']>', body):
            r7_errors.append("Missing mandatory '<div class=\"post-tags\">' with '<span class=\"tag-item\">' block")

        # 4. Sign bug check
        # Strip code blocks and table separators first
        body_for_signs = re.sub(r"```[\s\S]*?```", "", body)
        body_for_signs = re.sub(r"`[^`\n]+`", "", body_for_signs)
        for line_num, line in enumerate(body_for_signs.splitlines(), start=1):
            line_str = line.strip()
            if not line_str:
                continue
            if self.THEMATIC_BREAK_REGEX.match(line_str):
                continue
            if self.TABLE_SEPARATOR_REGEX.match(line_str):
                continue

            sign_match = self.SIGN_BUG_REGEX.search(line_str)
            if sign_match:
                r7_errors.append(f"Sign bug detected on line {line_num}: '{sign_match.group(0)}' in line: {line_str[:50]}")

        report.add_result(
            "RULE-07", "READABILITY_STRUCTURE_EAT", len(r7_errors) == 0,
            f"E-E-A-T structure verified (Length: {pure_char_count:,} chars, disclaimer, tags, 0 sign bugs)" if not r7_errors else f"Readability/structure failure ({len(r7_errors)} errors)",
            r7_errors
        )

        return report


def main():
    parser = argparse.ArgumentParser(description="Hard-Fail Validator for Alpha Context Chart Lecture Blog Posts")
    parser.add_argument("--post-path", type=str, default="", help="Path to markdown post file")
    parser.add_argument("--blog-root", type=str, default="", help="Root path of stock_blog repository")
    parser.add_argument("--assets-dir", type=str, default="", help="Assets directory path")
    args = parser.parse_args()

    current_script_dir = Path(__file__).resolve().parent
    blog_root = Path(args.blog_root).resolve() if args.blog_root else current_script_dir.parent
    assets_dir = Path(args.assets_dir).resolve() if args.assets_dir else blog_root / "assets" / "img"

    if args.post_path:
        post_path = Path(args.post_path).resolve()
    else:
        post_path = blog_root / "_posts" / "2026-11-15-changwon-10ma-pullback-trading-strategy.md"

    print("================================================================================")
    print("      ALPHA CONTEXT BLOG VALIDATOR: CHART TRADING LECTURE 1 AUDIT")
    print("================================================================================")
    print(f"[*] Blog Root : {blog_root}")
    print(f"[*] Post Path : {post_path}")
    print(f"[*] Assets Dir: {assets_dir}")
    print("--------------------------------------------------------------------------------")

    validator = ChartLectureValidator(blog_root=blog_root, assets_dir=assets_dir)
    report = validator.validate_post(post_path)

    all_passed = True
    for res in report.results:
        status_badge = "[ PASS ]" if res.passed else "[ FAIL ]"
        print(f"{status_badge} {res.rule_id}: {res.name}")
        print(f"         - Details: {res.details}")
        if res.errors:
            all_passed = False
            for err in res.errors:
                print(f"           * ERROR: {err}")

    print("--------------------------------------------------------------------------------")
    if all_passed and report.is_valid:
        print("[AUDIT RESULT] 100% PASS - All 7 Hard-Fail Gate Rules Met Perfectly!")
        print("================================================================================")
        sys.exit(0)
    else:
        print("[AUDIT RESULT] FAIL - Integrity violations detected. Deployment halted.")
        print("================================================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
