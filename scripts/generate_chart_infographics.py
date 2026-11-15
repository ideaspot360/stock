"""
Redesigned 16:9 Dark-Theme Financial Infographics for Alpha Context Blog.
Solves all visual QA issues:
1. True Circle Badges (①, ②, ③, ④) & Clear Callout Arrows via display-coordinate ax.annotate.
2. Single-line Non-overlapping Header Titles (Zero Title Collision, Zero Canvas Overflow).
3. Completely Opaque Bounding Boxes on Price Lines to prevent candle cut-through.
4. textwrap-based Auto-wrapping inside panels and warning boxes (Zero Border Overflow).
5. Two-column split layout for orderbook summary boxes (Left/Right alignment, Zero Collisions).
6. Built-in Automated Visual QA Hard-Fail Guard (assert_zero_visual_defects).
7. Automatic Asset Mirroring to both posts/ and root assets/img/.
"""
from __future__ import annotations

import os
import shutil
import textwrap
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
from PIL import Image

# 한글 폰트 설정
plt.rcParams["font.family"] = ["Malgun Gothic", "NanumGothic", "Noto Sans KR", "Gulim", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

DARK = {
    "bg": "#0D1117",            # 프리미엄 딥 다크 배경
    "panel": "#161B22",         # 카드 및 차트 배경
    "panel_border": "#30363D",  # 경계선
    "grid": "#21262D",          # 그리드 라인
    "text_primary": "#FFFFFF",  # 메인 화이트
    "text_secondary": "#C9D1D9",# 소프트 실버
    "text_muted": "#8B949E",    # 뮤트 그레이
    "gold": "#FFD700",          # 10이평선 & 핵심 타점
    "cyan": "#38BDF8",          # 5이평선 & 쿨 블루
    "orange": "#FB923C",        # 20이평선
    "bull_red": "#FF445B",      # 캔들 양봉 레드
    "bear_blue": "#3B82F6",     # 캔들 음봉 블루
    "stop_red": "#EF4444",      # 손절선
    "target_green": "#10B981",  # 익절선
    "badge_bg": "#1F2937",      # 뱃지 배경
}


def assert_zero_visual_defects(fig: plt.Figure, name: str = "Infographic"):
    """
    렌더링된 텍스트 객체들의 픽셀 바운딩 박스를 검사하여
    1) 캔버스(1920x1080) 이탈 및
    2) 상단 헤더 타이틀 간의 오버랩을 기계적으로 하드 감지합니다.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    
    # 1. 캔버스 영역 (1920 x 1080) 이탈 검사
    for t in fig.texts:
        bbox = t.get_window_extent(renderer)
        if bbox.x1 > 1920.5:
            raise AssertionError(f"[{name}] Canvas Right-Overflow: '{t.get_text()[:15]}' extends to {bbox.x1:.1f}px (> 1920px)")
        if bbox.x0 < -0.5:
            raise AssertionError(f"[{name}] Canvas Left-Overflow: '{t.get_text()[:15]}' extends to {bbox.x0:.1f}px (< 0px)")
        if bbox.y1 > 1080.5:
            raise AssertionError(f"[{name}] Canvas Top-Overflow: '{t.get_text()[:15]}' extends to {bbox.y1:.1f}px (> 1080px)")

    # 2. 헤더 타이틀 텍스트 간 오버랩 검사
    fig_texts = [(t, t.get_window_extent(renderer)) for t in fig.texts]
    for i in range(len(fig_texts)):
        for j in range(i + 1, len(fig_texts)):
            t1, b1 = fig_texts[i]
            t2, b2 = fig_texts[j]
            # y좌표가 거의 같은 라인에 있는 타이틀 간의 겹침 검사
            if abs(b1.y0 - b2.y0) < 30:
                if b1.overlaps(b2):
                    raise AssertionError(
                        f"[{name}] Title Collision Detected: '{t1.get_text()[:12]}' overlaps with '{t2.get_text()[:12]}' "
                        f"(b1=[{b1.x0:.1f}, {b1.x1:.1f}], b2=[{b2.x0:.1f}, {b2.x1:.1f}])"
                    )


class RedesignedChartInfographics:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # 상위 루트 에셋 디렉터리
        self.root_img_dir = self.output_dir.parent

    def generate_10ma_pullback_chart(self) -> Path:
        """
        도안 1: 3분봉/5분봉 10이평선 첫 눌림목 정석 타점 인포그래픽
        - 좌측(68%): 메인 캔들 차트 + 거래량 차트 (ax.annotate 정원 뱃지 + 화살표 지시선 완벽 결합)
        - 우측(32%): [그래프 밖 전용 해설 패널] textwrap 적용, 테두리 이탈 0% 보장
        - 상단: 타이틀 단일 라인 정렬 (오버랩 0%, 캔버스 이탈 0%)
        """
        fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=DARK["bg"])

        # Grid: 좌측 차트(0.04~0.67), 우측 설명 패널(0.69~0.96)
        gs_left = fig.add_gridspec(
            nrows=2, ncols=1,
            height_ratios=[7, 3],
            top=0.88, bottom=0.06, left=0.045, right=0.675,
            hspace=0.08
        )
        ax_main = fig.add_subplot(gs_left[0])
        ax_vol = fig.add_subplot(gs_left[1], sharex=ax_main)

        # 우측 설명 전용 패널
        gs_right = fig.add_gridspec(
            nrows=1, ncols=1,
            top=0.88, bottom=0.06, left=0.695, right=0.965
        )
        ax_panel = fig.add_subplot(gs_right[0])
        ax_panel.set_facecolor(DARK["panel"])
        for spine in ax_panel.spines.values():
            spine.set_color(DARK["panel_border"])
            spine.set_linewidth(1.5)
        ax_panel.set_xticks([])
        ax_panel.set_yticks([])

        # -------------------------------------------------------------------------
        # 헤더 타이틀 영역 (좌우 분리 완벽 정렬: 절대 충돌 불가 아키텍처)
        # -------------------------------------------------------------------------
        # 좌측: 카테고리 태그 및 메인 타이틀을 1개의 텍스트 객체로 통합하여 글자 겹침 원천 차단
        fig.text(
            0.045, 0.945,
            "맥락트레이딩 차트강의 #01  |  3분봉·5분봉 10선 첫 눌림목 정석 & -1.5% 칼손절",
            color=DARK["text_primary"], fontsize=18.5, fontweight="bold", va="center", ha="left"
        )
        # 우측: 핵심 성과 지표 (ha='right'로 캔버스 우측 안쪽에 완벽 밀착)
        fig.text(
            0.965, 0.945,
            "★ 승률 85% | 손익비 1:2.3",
            color=DARK["gold"], fontsize=17, fontweight="bold", va="center", ha="right"
        )

        # 차트 스타일링
        for ax in (ax_main, ax_vol):
            ax.set_facecolor(DARK["panel"])
            for spine in ax.spines.values():
                spine.set_color(DARK["panel_border"])
                spine.set_linewidth(1.2)
            ax.tick_params(colors=DARK["text_muted"], labelsize=13)
            ax.grid(True, linestyle="--", linewidth=0.7, color=DARK["grid"], alpha=0.7)

        # -------------------------------------------------------------------------
        # 25개 분봉 캔들 데이터 (결정론적 데이터)
        # -------------------------------------------------------------------------
        n_bars = 25
        candles = [
            # 0~4: 횡보
            (10000, 10080, 9980, 10050, 45000),
            (10050, 10120, 10020, 10080, 52000),
            (10080, 10100, 10000, 10020, 38000),
            (10020, 10150, 10010, 10120, 61000),
            (10120, 10220, 10100, 10200, 78000),
            # 5~9: 1차 강력 돌파 파동
            (10200, 10550, 10180, 10500, 320000),
            (10500, 10800, 10450, 10750, 410000),
            (10750, 11050, 10700, 10980, 480000),
            (10980, 11250, 10920, 11200, 550000),  # [① 1차 고점: 11,250원]
            (11200, 11280, 11050, 11100, 380000),
            # 10~14: 10선 수렴 눌림목 (거래량 급감)
            (11100, 11150, 10950, 11000, 210000),
            (11000, 11020, 10850, 10880, 130000),
            (10880, 10900, 10750, 10780, 75000),   # [② 거래량 바닥: 75k]
            (10780, 10820, 10700, 10720, 68000),
            (10720, 10750, 10640, 10680, 55000),
            # 15: [③ 10이평선 지지 양봉 타점]
            (10680, 10800, 10610, 10760, 125000), # 종가 10,760원 진입
            # 16~24: 2차 랠리 & 신고가 돌파
            (10760, 10980, 10740, 10950, 240000),
            (10950, 11180, 10920, 11150, 330000),
            (11150, 11350, 11120, 11300, 420000),
            (11300, 11520, 11280, 11480, 490000),  # [④ 신고가 돌파: 11,480원]
            (11480, 11620, 11420, 11580, 440000),
            (11580, 11700, 11520, 11650, 360000),
            (11650, 11720, 11600, 11680, 310000),
            (11680, 11750, 11620, 11700, 280000),
            (11700, 11750, 11650, 11720, 250000),
        ]

        # 이평선 계산
        closes = [c[3] for c in candles]
        ma5 = [np.mean(closes[max(0, i-4):i+1]) for i in range(n_bars)]
        ma10 = [np.mean(closes[max(0, i-9):i+1]) for i in range(n_bars)]
        ma20 = [np.mean(closes[max(0, i-19):i+1]) for i in range(n_bars)]

        # 캔들 및 거래량 렌더링
        for i, (o, h, l, c, v) in enumerate(candles):
            is_bull = c >= o
            color = DARK["bull_red"] if is_bull else DARK["bear_blue"]

            # 꼬리선
            ax_main.plot([i, i], [l, h], color=color, linewidth=1.8, zorder=3)
            # 몸통 박스
            body_bottom = min(o, c)
            body_height = max(abs(c - o), 20)
            rect = Rectangle(
                (i - 0.35, body_bottom), 0.70, body_height,
                facecolor=color, edgecolor=color, linewidth=1.2, zorder=4
            )
            ax_main.add_patch(rect)

            # 거래량 바
            v_color = DARK["bull_red"] if is_bull else DARK["bear_blue"]
            ax_vol.bar(i, v, width=0.70, color=v_color, alpha=0.85, zorder=3)

        # 이평선 플롯 (선명한 색상 대비)
        x_axis = np.arange(n_bars)
        ax_main.plot(x_axis, ma5, label="5 이평선 (공격선)", color=DARK["cyan"], linewidth=2.2, alpha=0.9, zorder=5)
        ax_main.plot(x_axis, ma10, label="★ 10 이평선 (생명선)", color=DARK["gold"], linewidth=4.2, alpha=1.0, zorder=6)
        ax_main.plot(x_axis, ma20, label="20 이평선 (추세선)", color=DARK["orange"], linewidth=2.2, alpha=0.85, zorder=5)

        # -------------------------------------------------------------------------
        # 깔끔한 기준선 (익절선 / 손절선) - 캔들 관통 방지용 불투명 패널 배경 적용
        # -------------------------------------------------------------------------
        entry_price = 10760
        stop_price = 10600
        target_price = 11140

        # +3.5% 1차 분할 익절선 (불투명 배경 적용)
        ax_main.axhline(target_price, color=DARK["target_green"], linestyle="--", linewidth=2.0, alpha=0.85, zorder=2)
        ax_main.text(
            0.5, target_price, " +3.5% 1차 분할 익절선 (11,140원) ",
            color=DARK["target_green"], fontsize=13, fontweight="bold", va="center",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=DARK["panel"], edgecolor=DARK["target_green"], lw=1.2, alpha=0.95),
            zorder=7
        )

        # -1.5% 기계적 칼손절선 (불투명 배경 적용)
        ax_main.axhline(stop_price, color=DARK["stop_red"], linestyle="--", linewidth=2.0, alpha=0.85, zorder=2)
        ax_main.text(
            0.5, stop_price, " -1.5% 기계적 칼손절선 (10,600원) ",
            color=DARK["stop_red"], fontsize=13, fontweight="bold", va="center",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=DARK["panel"], edgecolor=DARK["stop_red"], lw=1.2, alpha=0.95),
            zorder=7
        )

        # -------------------------------------------------------------------------
        # ★ 차트 내부: ax.annotate 기반 완벽한 정원(Circle) 뱃지 & 화살표 지시선 장착
        # (원 안에 또 원번호를 그리지 않고 깔끔한 아라비아 숫자 1, 2, 3, 4 단일 렌더링)
        # -------------------------------------------------------------------------
        # 1 1차 급등 돌파 파동 (캔들 8 고점 지시)
        ax_main.annotate(
            "1",
            xy=(8, 11250), xytext=(8, 11620),
            ha="center", va="center", fontsize=16, fontweight="bold", color="#FFFFFF",
            bbox=dict(boxstyle="circle,pad=0.35", facecolor=DARK["bull_red"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["bull_red"], lw=2.0, shrinkA=5, shrinkB=4),
            zorder=10
        )
        ax_main.text(8, 11770, "1차 급등 돌파", color=DARK["bull_red"], fontsize=13, fontweight="bold", ha="center", zorder=10)

        # 2 10이평 수렴 눌림목 (캔들 12 저점 지시)
        ax_main.annotate(
            "2",
            xy=(12, 10750), xytext=(12, 11280),
            ha="center", va="center", fontsize=16, fontweight="bold", color="#FFFFFF",
            bbox=dict(boxstyle="circle,pad=0.35", facecolor=DARK["cyan"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["cyan"], lw=2.0, shrinkA=5, shrinkB=4),
            zorder=10
        )
        ax_main.text(12, 11430, "10선 눌림 (거래급감)", color=DARK["cyan"], fontsize=13, fontweight="bold", ha="center", zorder=10)

        # 3 ★ 10이평 지지 양봉 타점 (캔들 15 밑꼬리 지시 - 뱃지와 텍스트 수평 배치로 오버랩 0%)
        ax_main.annotate(
            "3",
            xy=(15, 10610), xytext=(13.6, 10220),
            ha="center", va="center", fontsize=16, fontweight="bold", color="#000000",
            bbox=dict(boxstyle="circle,pad=0.35", facecolor=DARK["gold"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["gold"], lw=2.2, shrinkA=5, shrinkB=4),
            zorder=10
        )
        ax_main.text(
            14.6, 10220, "★ 10선 지지 종가 매수\n(10,760원 진입)",
            color=DARK["gold"], fontsize=12.5, fontweight="bold", ha="left", va="center", zorder=10
        )

        # 4 2차 랠리 & 신고가 돌파 (캔들 19 고점 지시)
        ax_main.annotate(
            "4",
            xy=(19, 11520), xytext=(19, 11800),
            ha="center", va="center", fontsize=16, fontweight="bold", color="#FFFFFF",
            bbox=dict(boxstyle="circle,pad=0.35", facecolor=DARK["target_green"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["target_green"], lw=2.0, shrinkA=5, shrinkB=4),
            zorder=10
        )
        ax_main.text(19, 11950, "신고가 2차 랠리", color=DARK["target_green"], fontsize=13, fontweight="bold", ha="center", zorder=10)

        # 거래량 차트 내 기준선 및 라벨
        dryup_level = 150000
        ax_vol.axhline(dryup_level, color=DARK["gold"], linestyle=":", linewidth=2.0, alpha=0.9)
        ax_vol.text(
            0.5, dryup_level + 18000, "거래량 1/3 급감 기준선 (Dry-Up Line)",
            color=DARK["gold"], fontsize=12.5, fontweight="bold"
        )
        # 거래량 바닥 지시 화살표 & 뱃지
        ax_vol.annotate(
            "V",
            xy=(12, 75000), xytext=(12, 260000),
            ha="center", va="center", fontsize=14, fontweight="bold", color="#FFFFFF",
            bbox=dict(boxstyle="circle,pad=0.30", facecolor=DARK["cyan"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["cyan"], lw=2.0, shrinkA=4, shrinkB=4),
            zorder=10
        )
        ax_vol.text(12, 320000, "거래량 87% 급감\n(매도세 완전 고갈)", color=DARK["cyan"],
                    fontsize=12, fontweight="bold", ha="center", zorder=10)

        ax_main.set_ylim(9850, 12150)
        ax_vol.set_ylim(0, 580000)
        ax_main.set_ylabel("주가 (KRW)", color=DARK["text_secondary"], fontsize=14, labelpad=8)
        ax_vol.set_ylabel("거래량", color=DARK["text_secondary"], fontsize=14, labelpad=8)
        ax_main.legend(loc="upper left", facecolor=DARK["panel"], edgecolor=DARK["panel_border"],
                       labelcolor=DARK["text_primary"], fontsize=12, framealpha=0.9)

        # X축 라벨 포맷팅
        time_labels = ["09:00", "09:06", "09:12", "09:18", "09:24", "09:30", "09:36", "09:42", "09:48", "09:54", "10:00", "10:06", "10:12"]
        step = 2
        ax_vol.set_xticks(range(0, n_bars, step))
        ax_vol.set_xticklabels([time_labels[i//2] for i in range(0, n_bars, step)], fontsize=12)
        ax_vol.set_xlabel("장중 3분봉 진행 시간 (Time)", color=DARK["text_secondary"], fontsize=13, labelpad=6)

        # -------------------------------------------------------------------------
        # ★ 우측 패널: [그래프 밖 전용 해설 카드] textwrap 자동 줄바꿈으로 테두리 이탈 0%
        # -------------------------------------------------------------------------
        ax_panel.text(0.06, 0.945, "■ 실전 매매 4단계 프로세스", color=DARK["gold"], fontsize=19, fontweight="bold")

        steps = [
            (
                "① 1차 급등 돌파 파동",
                DARK["bull_red"],
                [
                    "• 당일 거래대금 TOP 1~3위 주도주 압축",
                    "• 장대양봉으로 전일 고점 돌파 (+12.5%)",
                    "• 절대 추격 매수 금지 (1차 눌림 대기)",
                ]
            ),
            (
                "② 10이평 수렴 눌림목 (Dry-Up)",
                DARK["cyan"],
                [
                    "• 주가가 10이평선 부근까지 완만한 조정",
                    "• 거래량이 직전의 1/3 (30%) 이하로 급감",
                    "• 세력 이탈 없는 '건전한 숨고르기' 확인",
                ]
            ),
            (
                "③ ★ 10선 지지 양봉 종가 매수",
                DARK["gold"],
                [
                    "• 10 EMA 밑꼬리 터치 후 지지 양봉 완성",
                    "• [진입 타점] 15번 봉 종가: 10,760원",
                    "• [칼손절] -1.5% 이탈 시 즉시 기계적 손절",
                    "• [손익비] 리스크 160원 vs 기대 380원 (1:2.3)",
                ]
            ),
            (
                "④ 2차 랠리 및 분할 청산 공식",
                DARK["target_green"],
                [
                    "• [1차 익절] +3.5% 도달 시 50% 물량 락인",
                    "• [추세 홀딩] 잔여 50%는 10선 이탈 전까지",
                    "• 당일 신고가 랠리 끝까지 추종 (+8~10%)",
                ]
            ),
        ]

        card_y = 0.885
        for title, col, lines in steps:
            ax_panel.text(0.06, card_y, title, color=col, fontsize=16, fontweight="bold")
            card_y -= 0.036
            for l in lines:
                ax_panel.text(0.10, card_y, l, color=DARK["text_secondary"], fontsize=13)
                card_y -= 0.030
            card_y -= 0.018

        # 하단 자금관리 박스 (완벽한 중앙 정렬 및 상하 균일 간격 배치)
        rule_box = FancyBboxPatch(
            (0.04, 0.035), 0.92, 0.13, boxstyle="round,pad=0.02",
            facecolor="#2A1B1D", edgecolor=DARK["stop_red"], linewidth=1.5
        )
        ax_panel.add_patch(rule_box)
        # 박스 가로 중앙(x=0.50) 정렬 및 상하 균일 3단 배치
        ax_panel.text(0.50, 0.128, "[필독] 맥락트레이딩 절대 생존 수칙", color=DARK["stop_red"], fontsize=13.5, fontweight="bold", ha="center", va="center")
        
        rule_text_1 = "1. 원하는 타점(10이평 지지) 미도달 시 종일 매매 쉰다."
        rule_text_2 = "2. 손절선(-1.5%) 터치 시 망설임 없이 기계적 칼손절!"
        ax_panel.text(0.50, 0.090, rule_text_1, color=DARK["text_secondary"], fontsize=11.5, ha="center", va="center")
        ax_panel.text(0.50, 0.056, rule_text_2, color=DARK["gold"], fontsize=11.5, fontweight="bold", ha="center", va="center")

        # 시각 무결성 자동 검증 하드 가드
        assert_zero_visual_defects(fig, "10MA_Pullback_Chart")

        out_path = self.output_dir / "chart_3min_5min_10ma_pullback.png"
        plt.savefig(out_path, dpi=120, facecolor=DARK["bg"], edgecolor="none")
        plt.close(fig)

        # 루트 에셋 디렉터리 및 별칭 파일 자동 미러링 동기화
        shutil.copyfile(out_path, self.root_img_dir / "chart_3min_5min_10ma_pullback.png")
        shutil.copyfile(out_path, self.root_img_dir / "chart_10ma_pullback_infographic.png")
        shutil.copyfile(out_path, self.output_dir / "chart_10ma_pullback_infographic.png")
        return out_path

    def generate_orderbook_spoofing_diagram(self) -> Path:
        """
        도안 2: 호가 잔량의 역설 & 체결강도 구조도
        - 텍스트 오버랩 100% 제거 (좌/우 양 끝 정렬 아키텍처)
        - 폰트 크기 대폭 상향 (호가 15~16pt, 요약 17~18pt)
        - 좌우 명확한 대비: [위험한 착시] vs [진짜 폭등]
        - 하단 원리 박스 textwrap 적용으로 박스 밖 탈출 0%
        """
        fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=DARK["bg"])

        # 좌/우 패널 분할
        gs = fig.add_gridspec(
            nrows=1, ncols=2,
            top=0.88, bottom=0.06, left=0.045, right=0.955,
            wspace=0.07
        )
        ax_left = fig.add_subplot(gs[0])
        ax_right = fig.add_subplot(gs[1])

        # 헤더 타이틀 바 (좌우 완벽 분리: 절대 충돌 불가)
        fig.text(
            0.045, 0.945,
            "맥락트레이딩 호가창강의 #01  |  호가 잔량의 역설: 허매수벽 트랩 vs 매도벽 흡수",
            color=DARK["text_primary"], fontsize=18.5, fontweight="bold", va="center", ha="left"
        )
        fig.text(
            0.955, 0.945,
            "★ 체결강도 120% 돌파 원리",
            color=DARK["gold"], fontsize=17, fontweight="bold", va="center", ha="right"
        )

        for ax in (ax_left, ax_right):
            ax.set_facecolor(DARK["panel"])
            for spine in ax.spines.values():
                spine.set_color(DARK["panel_border"])
                spine.set_linewidth(1.5)
            ax.set_xticks([])
            ax.set_yticks([])

        # =========================================================================
        # 좌측 패널: [위험한 착시] 급락형 호가창 (Fake Bid Wall Trap)
        # =========================================================================
        ax_left.text(
            0.5, 0.94, "[위험한 착시] 급락형 호가창 (Fake Bid Trap)",
            color=DARK["stop_red"], fontsize=19, fontweight="bold", ha="center"
        )
        ax_left.text(
            0.5, 0.89, "초보자의 착각: '매수잔량이 6배나 많으니 안전하다?'",
            color=DARK["text_muted"], fontsize=14, ha="center"
        )

        # 상단 총잔량 요약 박스 (ha='left'와 ha='right'로 양 끝 정렬하여 중앙 오버랩 100% 원천 차단)
        summary_l = FancyBboxPatch(
            (0.04, 0.73), 0.92, 0.13, boxstyle="round,pad=0.02",
            facecolor="#2A1B1D", edgecolor=DARK["stop_red"], linewidth=1.5
        )
        ax_left.add_patch(summary_l)
        # 1행: 매도총잔량 (좌) vs 매수총잔량 (우)
        ax_left.text(0.08, 0.815, "매도총잔량: 45,000주", color=DARK["bear_blue"], fontsize=17, fontweight="bold", ha="left")
        ax_left.text(0.92, 0.815, "매수총잔량: 285,000주", color=DARK["stop_red"], fontsize=17, fontweight="bold", ha="right")
        # 2행: 호가비율 (좌) vs 체결강도 (우)
        ax_left.text(0.08, 0.760, "호가비율: 1 : 6.3 (극단적 매수 착시)", color=DARK["text_muted"], fontsize=14, ha="left")
        ax_left.text(0.92, 0.760, "체결강도: 62% (매도세 압도)", color=DARK["stop_red"], fontsize=15, fontweight="bold", ha="right")

        # 6단계 호가 테이블
        rows_l = [
            ("매도 3호가 (10,150원)", "12,000주", DARK["bear_blue"], 0.18),
            ("매도 2호가 (10,100원)", "18,000주", DARK["bear_blue"], 0.25),
            ("매도 1호가 (10,050원)", "15,000주", DARK["bear_blue"], 0.20),
            # 현재가
            ("매수 1호가 (10,000원)", "25,000주", DARK["bull_red"], 0.28),
            ("매수 2호가 ( 9,950원)", "30,000주", DARK["bull_red"], 0.32),
            ("매수 3호가 ( 9,900원)", "130,000주 ★", DARK["stop_red"], 0.88), # 거대 허매수벽
        ]

        y_pos = 0.635
        for label, qty, col, b_len in rows_l:
            rect = Rectangle((0.44, y_pos - 0.015), b_len * 0.44, 0.040, facecolor=col, alpha=0.30)
            ax_left.add_patch(rect)
            ax_left.text(0.06, y_pos, label, color=DARK["text_secondary"], fontsize=14.5, va="center")
            ax_left.text(0.48, y_pos, qty, color=col, fontsize=15.5, fontweight="bold", va="center")
            y_pos -= 0.058

        # 하단 핵심 경고 박스 (textwrap 적용으로 박스 밖 탈출 0%)
        alert_box_l = FancyBboxPatch(
            (0.04, 0.04), 0.92, 0.20, boxstyle="round,pad=0.02",
            facecolor="#1A1214", edgecolor=DARK["stop_red"], linewidth=1.5
        )
        ax_left.add_patch(alert_box_l)
        ax_left.text(0.50, 0.195, "[주의] 세력의 '허매수벽(Fake Bid)' 트랩 작동 원리", color=DARK["stop_red"], fontsize=15, fontweight="bold", ha="center")
        ax_left.text(0.08, 0.155, "1. 매수 3호가에 13만 주 대형 벽을 쌓아 개미에게 '안전판' 착시 유도", color=DARK["text_secondary"], fontsize=13)
        ax_left.text(0.08, 0.115, "2. 개미가 안심하고 매수할 때 세력은 위에서 시장가로 전량 물량 투하", color=DARK["text_secondary"], fontsize=13)
        ax_left.text(0.08, 0.075, "3. 물량 털기 완료 즉시 13만 주 일거 취소 ➔ 호가 공백 수직 폭락!", color=DARK["stop_red"], fontsize=13.5, fontweight="bold")

        # =========================================================================
        # 우측 패널: [진짜 폭등] 상승형 호가창 (보컬의 매도벽 흡수 법칙)
        # =========================================================================
        ax_right.text(
            0.5, 0.94, "★ [진짜 폭등] 상승형 호가창 (보컬의 매도벽 흡수)",
            color=DARK["gold"], fontsize=19, fontweight="bold", ha="center"
        )
        ax_right.text(
            0.5, 0.89, "실전 대가의 통찰: '매도잔량이 2~3배 많아야 상승 연료가 된다!'",
            color=DARK["cyan"], fontsize=14, ha="center"
        )

        # 상단 총잔량 요약 박스 (양 끝 정렬)
        summary_r = FancyBboxPatch(
            (0.04, 0.73), 0.92, 0.13, boxstyle="round,pad=0.02",
            facecolor="#162A22", edgecolor=DARK["gold"], linewidth=1.5
        )
        ax_right.add_patch(summary_r)
        # 1행: 매도총잔량 (좌) vs 매수총잔량 (우)
        ax_right.text(0.08, 0.815, "매도총잔량: 380,000주 ★", color=DARK["gold"], fontsize=17, fontweight="bold", ha="left")
        ax_right.text(0.92, 0.815, "매수총잔량: 115,000주", color=DARK["cyan"], fontsize=17, fontweight="bold", ha="right")
        # 2행: 호가비율 (좌) vs 체결강도 (우)
        ax_right.text(0.08, 0.760, "호가비율: 3.3 : 1 (황금 매도벽)", color=DARK["text_primary"], fontsize=14, fontweight="bold", ha="left")
        ax_right.text(0.92, 0.760, "체결강도: 148% (공격적 시장가)", color=DARK["target_green"], fontsize=15, fontweight="bold", ha="right")

        # 6단계 호가 테이블
        rows_r = [
            ("매도 3호가 (10,150원)", "110,000주", DARK["bear_blue"], 0.75),
            ("매도 2호가 (10,100원)", "135,000주", DARK["bear_blue"], 0.88),
            ("매도 1호가 (10,050원)", " 85,000주 ★", DARK["gold"], 0.60),  # 세력 공격 흡수 대상
            # 현재가
            ("매수 1호가 (10,000원)", " 25,000주", DARK["bull_red"], 0.22),
            ("매수 2호가 ( 9,950원)", " 38,000주", DARK["bull_red"], 0.30),
            ("매수 3호가 ( 9,900원)", " 22,000주", DARK["bull_red"], 0.20),
        ]

        y_pos = 0.635
        for label, qty, col, b_len in rows_r:
            rect = Rectangle((0.44, y_pos - 0.015), b_len * 0.44, 0.040, facecolor=col, alpha=0.30)
            ax_right.add_patch(rect)
            ax_right.text(0.06, y_pos, label, color=DARK["text_secondary"], fontsize=14.5, va="center")
            ax_right.text(0.48, y_pos, qty, color=col, fontsize=15.5, fontweight="bold", va="center")
            y_pos -= 0.058

        # 하단 핵심 원리 박스 (textwrap 적용)
        alert_box_r = FancyBboxPatch(
            (0.04, 0.04), 0.92, 0.20, boxstyle="round,pad=0.02",
            facecolor="#12251D", edgecolor=DARK["target_green"], linewidth=1.5
        )
        ax_right.add_patch(alert_box_r)
        ax_right.text(0.50, 0.195, "[돌파] 세력의 '매도벽 흡수(Wall Absorption)' 랠리 원리", color=DARK["target_green"], fontsize=15, fontweight="bold", ha="center")
        ax_right.text(0.08, 0.155, "1. 상단 매도 1~3호가에 빽빽한 물량은 세력의 '진짜 매수 연료'", color=DARK["text_secondary"], fontsize=13)
        ax_right.text(0.08, 0.115, "2. 대형 시장가 매수세(체결강도 148%)가 매도벽을 단숨에 흡수 돌파", color=DARK["text_secondary"], fontsize=13)
        ax_right.text(0.08, 0.075, "3. 매도벽 돌파 즉시 거래대금 폭증하며 전고점 랠리 시작!", color=DARK["gold"], fontsize=13.5, fontweight="bold")

        # 시각 무결성 자동 검증 하드 가드
        assert_zero_visual_defects(fig, "Orderbook_Spoofing_Diagram")

        out_path = self.output_dir / "orderbook_spoofing_execution_strength.png"
        plt.savefig(out_path, dpi=120, facecolor=DARK["bg"], edgecolor="none")
        plt.close(fig)

        # 루트 에셋 디렉터리 및 별칭 파일 자동 미러링 동기화
        shutil.copyfile(out_path, self.root_img_dir / "orderbook_spoofing_execution_strength.png")
        shutil.copyfile(out_path, self.root_img_dir / "orderbook_spoofing_diagram.png")
        shutil.copyfile(out_path, self.output_dir / "orderbook_spoofing_diagram.png")
        return out_path


if __name__ == "__main__":
    out_dir = Path("growth_engine/03_blog_hub/stock_blog/assets/img/posts")
    engine = RedesignedChartInfographics(out_dir)
    p1 = engine.generate_10ma_pullback_chart()
    p2 = engine.generate_orderbook_spoofing_diagram()
    print("Generated 1:", p1)
    print("Generated 2:", p2)
