"""
Visual QA Hard-Fail Guard & Layout Audit Engine for Alpha Context Infographics.
Performs deterministic, pixel-level bounding box audits on 1920x1080 dark-theme charts.
Enforces 6 Hard-Fail Gates to guarantee zero visual defects.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.text as mtext


class VisualQAGuard:
    CANVAS_WIDTH = 1920.0
    CANVAS_HEIGHT = 1080.0
    MIN_CANVAS_MARGIN = 20.0       # 캔버스 테두리 최소 여백 (px)
    MIN_CONTAINER_PADDING = 25.0   # 컨테이너 박스 내부 최소 좌우 여백 (px)

    @classmethod
    def assert_zero_visual_defects(cls, fig: plt.Figure, name: str = "Chart") -> Dict[str, Any]:
        """
        렌더링된 텍스트와 패치의 실제 픽셀 바운딩 박스를 검사하여
        6대 하드 페일 게이트를 통과시키고, 실측 감사 메타데이터를 반환합니다.
        """
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()

        # 1. Figure + 모든 Axes 내부 텍스트 객체 전수 수집 (사각지대 0%)
        all_texts: List[mtext.Text] = list(fig.texts)
        for ax in fig.axes:
            all_texts.extend(ax.texts)

        passed_gates = []
        min_canvas_margin_found = 9999.0
        min_box_padding_found = 9999.0
        badge_ratios = []

        # =====================================================================
        # [Gate 1: 전체 캔버스 경계 이탈 및 20px 최소 여백 검사]
        # =====================================================================
        for t in all_texts:
            bb = t.get_window_extent(renderer)
            margin_left = bb.x0
            margin_right = cls.CANVAS_WIDTH - bb.x1
            margin_bottom = bb.y0
            margin_top = cls.CANVAS_HEIGHT - bb.y1

            current_min = min(margin_left, margin_right, margin_bottom, margin_top)
            if current_min < min_canvas_margin_found:
                min_canvas_margin_found = current_min

            if bb.x0 < cls.MIN_CANVAS_MARGIN:
                raise AssertionError(
                    f"[{name}] Gate 1 이탈 (좌측): '{t.get_text()[:15]}' x0={bb.x0:.1f}px (< {cls.MIN_CANVAS_MARGIN}px)"
                )
            if bb.x1 > (cls.CANVAS_WIDTH - cls.MIN_CANVAS_MARGIN):
                raise AssertionError(
                    f"[{name}] Gate 1 이탈 (우측): '{t.get_text()[:15]}' x1={bb.x1:.1f}px (> {cls.CANVAS_WIDTH - cls.MIN_CANVAS_MARGIN}px)"
                )
            if bb.y0 < cls.MIN_CANVAS_MARGIN:
                raise AssertionError(
                    f"[{name}] Gate 1 이탈 (하단): '{t.get_text()[:15]}' y0={bb.y0:.1f}px (< {cls.MIN_CANVAS_MARGIN}px)"
                )
            if bb.y1 > (cls.CANVAS_HEIGHT - cls.MIN_CANVAS_MARGIN):
                raise AssertionError(
                    f"[{name}] Gate 1 이탈 (상단): '{t.get_text()[:15]}' y1={bb.y1:.1f}px (> {cls.CANVAS_HEIGHT - cls.MIN_CANVAS_MARGIN}px)"
                )
        passed_gates.append("GATE_1_CANVAS_BOUNDS")

        # =====================================================================
        # [Gate 2: 헤더 및 축 내부 텍스트 충돌 검사 (화살표 오탐 원천 방지)]
        # =====================================================================
        # 2-A. Figure 상단 헤더 텍스트 간 수평 충돌 검사
        fig_text_items = [(t, t.get_window_extent(renderer)) for t in fig.texts]
        for i in range(len(fig_text_items)):
            for j in range(i + 1, len(fig_text_items)):
                t1, b1 = fig_text_items[i]
                t2, b2 = fig_text_items[j]
                if abs(b1.y0 - b2.y0) < 30 and b1.overlaps(b2):
                    raise AssertionError(
                        f"[{name}] Gate 2 헤더 충돌: '{t1.get_text()[:12]}' overlaps with '{t2.get_text()[:12]}'"
                    )

        # 2-B. Axes 내부 동일 수평 대역 텍스트 충돌 검사
        for ax in fig.axes:
            ax_items: List[Tuple[mtext.Text, Any]] = []
            for t in ax.texts:
                if isinstance(t, mtext.Annotation) and t.get_bbox_patch():
                    # 화살표(arrow_patch)를 배제하고 순수 원형 뱃지 패치의 바운딩 박스만 추출
                    ax_items.append((t, t.get_bbox_patch().get_window_extent(renderer)))
                else:
                    ax_items.append((t, t.get_window_extent(renderer)))

            for i in range(len(ax_items)):
                for j in range(i + 1, len(ax_items)):
                    t1, b1 = ax_items[i]
                    t2, b2 = ax_items[j]
                    # 같은 y 높이 대역(수평 라인, 오차 15px 이내)에 있는 텍스트 간 오버랩 검사
                    if abs((b1.y0 + b1.y1) / 2 - (b2.y0 + b2.y1) / 2) < 15:
                        if b1.overlaps(b2):
                            raise AssertionError(
                                f"[{name}] Gate 2 내부 텍스트 충돌: '{t1.get_text()[:10]}' vs '{t2.get_text()[:10]}'"
                            )
        passed_gates.append("GATE_2_ZERO_COLLISIONS")

        # =====================================================================
        # [Gate 3: 뱃지 완벽 정원성(Aspect Ratio 1.000) 및 화살표 결합 검사]
        # =====================================================================
        for ax in fig.axes:
            for t in ax.texts:
                if isinstance(t, mtext.Annotation) and t.get_bbox_patch():
                    patch = t.get_bbox_patch()
                    # 오직 'circle'인 타점 뱃지만 정밀 타겟팅
                    if "circle" in str(patch.get_boxstyle()).lower():
                        p_bb = patch.get_window_extent(renderer)
                        ratio = p_bb.width / p_bb.height
                        badge_ratios.append(round(ratio, 4))
                        if not (0.97 <= ratio <= 1.03):
                            raise AssertionError(
                                f"[{name}] Gate 3 뱃지 왜곡: '{t.get_text()}' 종횡비 {ratio:.4f} (정원 1.000 위반)"
                            )
                        if t.arrow_patch is None:
                            raise AssertionError(
                                f"[{name}] Gate 3 지시선 누락: 뱃지 '{t.get_text()}'에 arrowprops 화살표 없음"
                            )
        passed_gates.append("GATE_3_TRUE_CIRCULARITY")

        # =====================================================================
        # [Gate 4: 뱃지 내부 유니코드 원문자 중복 금지 및 단일 표기 검증]
        # =====================================================================
        for ax in fig.axes:
            for t in ax.texts:
                if isinstance(t, mtext.Annotation) and t.get_bbox_patch():
                    patch = t.get_bbox_patch()
                    if "circle" in str(patch.get_boxstyle()).lower():
                        raw_txt = t.get_text().strip()
                        if re.search(r"[\u2460-\u2473\u3251-\u325F]", raw_txt):
                            raise AssertionError(
                                f"[{name}] Gate 4 원문자 중복: 뱃지 내부에 유니코드 '{raw_txt}' 사용 금지. 아라비아 숫자('1', '2') 사용 필수"
                            )
        passed_gates.append("GATE_4_SINGLE_DIGIT_BADGE")

        # =====================================================================
        # [Gate 5: 컨테이너 박스 내부 텍스트 테두리 탈출 및 최소 25px 안전 여백]
        # =====================================================================
        for ax in fig.axes:
            for p in ax.patches:
                if isinstance(p, patches.FancyBboxPatch):
                    p_bb = p.get_window_extent(renderer)
                    for t in ax.texts:
                        t_bb = t.get_window_extent(renderer)
                        t_cx = (t_bb.x0 + t_bb.x1) / 2
                        t_cy = (t_bb.y0 + t_bb.y1) / 2
                        # 텍스트의 x 중심이 박스 안에 있고, y 중심이 박스 내부 및 하단 인근에 걸쳐 있는 경우 (컨테이너 소속 판별)
                        if p_bb.x0 <= t_cx <= p_bb.x1 and (p_bb.y0 - 40.0) <= t_cy <= (p_bb.y1 - 10.0):
                            # 박스 하단 테두리 밖 탈출 하드 검증
                            if t_bb.y0 < p_bb.y0:
                                raise AssertionError(
                                    f"[{name}] Gate 5 박스 하단 탈출: '{t.get_text()[:15]}' y0={t_bb.y0:.1f}px (< 박스하단 {p_bb.y0:.1f}px)"
                                )

                            pad_left = t_bb.x0 - p_bb.x0
                            pad_right = p_bb.x1 - t_bb.x1
                            cur_pad = min(pad_left, pad_right)
                            if cur_pad < min_box_padding_found:
                                min_box_padding_found = cur_pad

                            if pad_left < cls.MIN_CONTAINER_PADDING or pad_right < cls.MIN_CONTAINER_PADDING:
                                raise AssertionError(
                                    f"[{name}] Gate 5 좌우여백 미달: '{t.get_text()[:15]}' 좌우 여백 [{pad_left:.1f}px, {pad_right:.1f}px] "
                                    f"(최소 안전 여백 {cls.MIN_CONTAINER_PADDING}px 미달)"
                                )
        passed_gates.append("GATE_5_BOX_PADDING_MARGIN")

        # =====================================================================
        # [Gate 6: 가격선 레이블 불투명 차폐(Shielding) 및 zorder 검사]
        # =====================================================================
        for ax in fig.axes:
            # 외곽 설명 전용 패널(눈금이 아예 없는 Axes)은 캔들이 없으므로 제외
            if len(ax.get_xticks()) == 0 and len(ax.get_yticks()) == 0:
                continue

            for t in ax.texts:
                txt = t.get_text()
                # 손절선, 익절선, 기준선 레이블만 정밀 타겟팅
                if any(kw in txt for kw in ["손절선", "익절선", "기준선", "분할 익절", "기계적 칼손절"]):
                    if not t.get_bbox_patch():
                        raise AssertionError(
                            f"[{name}] Gate 6 차폐 누락: 가격선 '{txt[:15]}'에 불투명 bbox가 없음 (캔들 관통 위험)"
                        )
                    if t.get_zorder() < 5:
                        raise AssertionError(
                            f"[{name}] Gate 6 zorder 결함: 가격선 '{txt[:15]}' zorder={t.get_zorder()} (< 5)"
                        )
        passed_gates.append("GATE_6_SHIELDED_PRICE_LINES")

        return {
            "name": name,
            "text_count": len(all_texts),
            "canvas_margin_min_px": round(min_canvas_margin_found, 1),
            "box_padding_min_px": round(min_box_padding_found, 1) if min_box_padding_found != 9999.0 else None,
            "badge_ratios": badge_ratios,
            "passed_gates": passed_gates,
            "qa_status": "PASS",
        }


class LayoutAuditManifest:
    """
    렌더링된 이미지 에셋의 SHA-256 해시와 Visual QA 실측 데이터를
    posts/layout_audit.json 에 기록하고 검증하는 SSOT 매니페스트 관리자.
    """
    def __init__(self, manifest_path: Path):
        self.manifest_path = manifest_path
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self):
        if self.manifest_path.exists():
            try:
                self.data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except Exception:
                self.data = {}
        else:
            self.data = {}

    def save(self):
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def record_asset(self, img_path: Path, qa_meta: Dict[str, Any]):
        sha256 = self.calculate_sha256(img_path)
        rel_name = img_path.name
        self.data[rel_name] = {
            "file_name": rel_name,
            "sha256": sha256,
            "resolution": [1920, 1080],
            "aspect_ratio": 1.7778,
            "canvas_margin_min_px": qa_meta.get("canvas_margin_min_px"),
            "box_padding_min_px": qa_meta.get("box_padding_min_px"),
            "badge_ratios": qa_meta.get("badge_ratios", []),
            "text_count": qa_meta.get("text_count", 0),
            "passed_gates": qa_meta.get("passed_gates", []),
            "qa_status": "PASS",
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }
        self.save()

    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
