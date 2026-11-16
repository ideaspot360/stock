"""
Dedicated 16:9 Dark-Theme Infographics for STRAT-01 Practical Manual Post.
Generates:
1. chart_strat01_5step_protocol.png (5-Step Execution Protocol & HTS Road Map)
2. chart_strat01_condition_stoploss_guide.png (Universal HTS Condition Filter & Server Stop-Loss Guard)

Enforces VisualQAGuard 6-Gate Hard-Fail Verification & SHA-256 Layout Audit Manifest.
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

# Import VisualQAGuard and LayoutAuditManifest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from visual_qa_guard import VisualQAGuard, LayoutAuditManifest

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


class Strat01InfographicsGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.root_img_dir = self.output_dir.parent
        self.manifest = LayoutAuditManifest(self.output_dir / "layout_audit.json")

    def generate_5step_protocol_chart(self) -> Path:
        """
        도안 1: STRAT-01 주도주 10이평선 첫 눌림목 5단계 매매 프로토콜 & 차트 타점
        - 좌측(68%): 3분봉/5분봉 캔들 차트 + 거래량 차트 (ax.annotate 정원 뱃지 '1'~'5' + 화살표 지시선)
        - 우측(32%): [5단계 실전 매매 프로토콜] textwrap.wrap 기반 카드 스택
        - 상단: 타이틀 단일 라인 분리 정렬 (충돌 0%)
        - 하단: 증권사 공통 서버 자동감시 헌법 박스 (여백 25px+ 확보)
        """
        fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=DARK["bg"])

        # Grid: 좌측 차트(0.075~0.675, y축 라벨 안전 여백 확보), 우측 설명 패널(0.695~0.965)
        gs_left = fig.add_gridspec(
            nrows=2, ncols=1,
            height_ratios=[7, 3],
            top=0.88, bottom=0.080, left=0.075, right=0.675,
            hspace=0.08
        )
        ax_main = fig.add_subplot(gs_left[0])
        ax_vol = fig.add_subplot(gs_left[1], sharex=ax_main)

        # 우측 설명 패널
        gs_right = fig.add_gridspec(
            nrows=1, ncols=1,
            top=0.88, bottom=0.080, left=0.695, right=0.965
        )
        ax_panel = fig.add_subplot(gs_right[0])
        ax_panel.set_facecolor(DARK["panel"])
        for spine in ax_panel.spines.values():
            spine.set_color(DARK["panel_border"])
            spine.set_linewidth(1.5)
        ax_panel.set_xticks([])
        ax_panel.set_yticks([])

        # -------------------------------------------------------------------------
        # 헤더 타이틀 영역 (좌우 분리 완벽 정렬: 절대 충돌 불가)
        # -------------------------------------------------------------------------
        fig.text(
            0.050, 0.945,
            "맥락트레이딩 실전매뉴얼 #01  |  STRAT-01 주도주 10이평선 첫 눌림목 5단계 매매 프로토콜",
            color=DARK["text_primary"], fontsize=17.5, fontweight="bold", va="center", ha="left"
        )
        fig.text(
            0.965, 0.945,
            "★ HTS/MTS 5단계 스나이핑 로드맵",
            color=DARK["gold"], fontsize=16.5, fontweight="bold", va="center", ha="right"
        )

        for ax in (ax_main, ax_vol):
            ax.set_facecolor(DARK["panel"])
            for spine in ax.spines.values():
                spine.set_color(DARK["panel_border"])
                spine.set_linewidth(1.2)
            ax.tick_params(colors=DARK["text_muted"], labelsize=12)
            ax.grid(True, linestyle="--", linewidth=0.7, color=DARK["grid"], alpha=0.7)

        # -------------------------------------------------------------------------
        # 25개 분봉 캔들 데이터 (결정론적 데이터)
        # -------------------------------------------------------------------------
        n_bars = 25
        candles = [
            (10000, 10080, 9980, 10050, 42000),   # 0
            (10050, 10120, 10020, 10080, 51000),   # 1
            (10080, 10150, 10040, 10120, 63000),   # 2
            (10120, 10250, 10100, 10220, 85000),   # 3
            (10220, 10600, 10200, 10550, 310000),  # 4
            (10550, 10850, 10500, 10800, 420000),  # 5 [1단계: 장초반 수급 폭발]
            (10800, 11100, 10750, 11020, 490000),  # 6
            (11020, 11280, 10980, 11250, 580000),  # 7 [2단계: 1차 급등 고점 완성]
            (11250, 11300, 11100, 11150, 390000),  # 8
            (11150, 11200, 10980, 11020, 220000),  # 9
            (11020, 11050, 10880, 10900, 140000),  # 10
            (10900, 10920, 10780, 10800, 82000),   # 11
            (10800, 10820, 10690, 10720, 61000),   # 12 [3단계: 10선 터치 & 거래량 급감]
            (10720, 10750, 10620, 10660, 54000),   # 13
            (10660, 10800, 10610, 10760, 135000),  # 14 [4단계: 10선 지지양봉 종가 매수 10,760]
            (10760, 10980, 10740, 10950, 260000),  # 15
            (10950, 11180, 10920, 11140, 340000),  # 16 [+3.5% 1차 분할 익절 도달]
            (11140, 11350, 11100, 11300, 410000),  # 17
            (11300, 11520, 11280, 11480, 480000),  # 18 [5단계: 자동감시 & 신고가 랠리]
            (11480, 11650, 11430, 11600, 430000),  # 19
            (11600, 11720, 11550, 11680, 350000),  # 20
            (11680, 11760, 11620, 11720, 290000),  # 21
            (11720, 11780, 11680, 11750, 240000),  # 22
            (11750, 11800, 11700, 11760, 220000),  # 23
            (11760, 11820, 11720, 11780, 200000),  # 24
        ]

        closes = [c[3] for c in candles]
        ma5 = [np.mean(closes[max(0, i-4):i+1]) for i in range(n_bars)]
        # 10지수이평선(EMA): 지수 가중치 alpha = 2 / (10 + 1)
        def calc_ema(prices: list[float], span: int = 10) -> list[float]:
            alpha = 2.0 / (span + 1.0)
            ema = []
            for idx, p in enumerate(prices):
                if idx == 0:
                    ema.append(float(p))
                else:
                    ema.append(alpha * float(p) + (1.0 - alpha) * ema[-1])
            return ema

        ma10 = calc_ema(closes, span=10)
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

        # 이평선 플롯
        x_axis = np.arange(n_bars)
        ax_main.plot(x_axis, ma5, label="5 이평선 (공격선)", color=DARK["cyan"], linewidth=2.0, alpha=0.9, zorder=5)
        ax_main.plot(x_axis, ma10, label="★ 10 이평선 (생명선)", color=DARK["gold"], linewidth=4.0, alpha=1.0, zorder=6)
        ax_main.plot(x_axis, ma20, label="20 이평선 (추세선)", color=DARK["orange"], linewidth=2.0, alpha=0.85, zorder=5)

        # 기준선 (익절선 / 손절선)
        entry_price = 10760
        stop_price = 10600
        target_price = 11140

        # +3.5% 1차 분할 익절선 (매수 타점 x=13.5부터 우측으로 전개하여 1차 급등봉 가림 원천 차단)
        ax_main.hlines(target_price, xmin=13.5, xmax=24.5, color=DARK["target_green"], linestyle="--", linewidth=1.8, alpha=0.9, zorder=3)
        ax_main.text(
            20.5, target_price, " +3.5% 1차 분할 익절선 (11,140원) ",
            color=DARK["target_green"], fontsize=11.5, fontweight="bold", va="center", ha="center",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=DARK["panel"], edgecolor=DARK["target_green"], lw=1.2, alpha=0.95),
            zorder=7
        )

        # -1.5% 서버 자동감시 칼손절선 (매수 타점 x=13.5부터 우측으로 전개)
        ax_main.hlines(stop_price, xmin=13.5, xmax=24.5, color=DARK["stop_red"], linestyle="--", linewidth=1.8, alpha=0.9, zorder=3)
        ax_main.text(
            20.5, stop_price, " -1.5% 기계적 칼손절선 (10,600원) ",
            color=DARK["stop_red"], fontsize=11.5, fontweight="bold", va="center", ha="center",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=DARK["panel"], edgecolor=DARK["stop_red"], lw=1.2, alpha=0.95),
            zorder=7
        )

        # -------------------------------------------------------------------------
        # 차트 내부: ax.annotate 정원 뱃지 '1'~'5' & 지시선
        # -------------------------------------------------------------------------
        # 1: 당일 거래대금 상위 1차 수급 폭발
        ax_main.annotate(
            "1",
            xy=(5, 10850), xytext=(5, 11450),
            ha="center", va="center", fontsize=15, fontweight="bold", color="#FFFFFF",
            bbox=dict(boxstyle="circle,pad=0.35", facecolor=DARK["bull_red"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["bull_red"], lw=2.0, shrinkA=5, shrinkB=4),
            zorder=10
        )
        ax_main.text(5, 11620, "1단계: 주도주 수급", color=DARK["bull_red"], fontsize=12, fontweight="bold", ha="center", zorder=10)

        # 2: 1차 급등 돌파 완성 (추격 금지)
        ax_main.annotate(
            "2",
            xy=(7, 11280), xytext=(8.5, 11750),
            ha="center", va="center", fontsize=15, fontweight="bold", color="#FFFFFF",
            bbox=dict(boxstyle="circle,pad=0.35", facecolor=DARK["orange"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["orange"], lw=2.0, shrinkA=5, shrinkB=4),
            zorder=10
        )
        ax_main.text(8.5, 11930, "2단계: 돌파확인(추격금지)", color=DARK["orange"], fontsize=12, fontweight="bold", ha="center", zorder=10)

        # 3: 10이평 수렴 & 거래량 1/3 급감
        ax_main.annotate(
            "3",
            xy=(12, 10720), xytext=(11.5, 11300),
            ha="center", va="center", fontsize=15, fontweight="bold", color="#FFFFFF",
            bbox=dict(boxstyle="circle,pad=0.35", facecolor=DARK["cyan"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["cyan"], lw=2.0, shrinkA=5, shrinkB=4),
            zorder=10
        )
        ax_main.text(11.5, 11470, "3단계: 10선수렴(거래급감)", color=DARK["cyan"], fontsize=12, fontweight="bold", ha="center", zorder=10)

        # 4: 10선 지지양봉 종가 매수 스나이핑 (10,760원)
        ax_main.annotate(
            "4",
            xy=(14, 10610), xytext=(14, 10220),
            ha="center", va="center", fontsize=15, fontweight="bold", color="#000000",
            bbox=dict(boxstyle="circle,pad=0.35", facecolor=DARK["gold"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["gold"], lw=2.2, shrinkA=5, shrinkB=4),
            zorder=10
        )
        ax_main.text(
            15.0, 10220, "★ 4단계: 지지양봉 종가매수\n(10,760원 진입)",
            color=DARK["gold"], fontsize=12.0, fontweight="bold", ha="left", va="center", zorder=10
        )

        # 5: 서버 자동감시 가동 & +3.5% 분할 익절 / 10선 홀딩
        ax_main.annotate(
            "5",
            xy=(18, 11520), xytext=(18, 11800),
            ha="center", va="center", fontsize=15, fontweight="bold", color="#FFFFFF",
            bbox=dict(boxstyle="circle,pad=0.35", facecolor=DARK["target_green"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["target_green"], lw=2.0, shrinkA=5, shrinkB=4),
            zorder=10
        )
        ax_main.text(18, 11960, "5단계: 서버감시 & 분할익절", color=DARK["target_green"], fontsize=12, fontweight="bold", ha="center", zorder=10)

        # 거래량 차트 내 기준선 (차폐 박스 적용)
        dryup_level = 150000
        ax_vol.axhline(dryup_level, color=DARK["gold"], linestyle=":", linewidth=1.8, alpha=0.9, zorder=2)
        ax_vol.text(
            0.5, dryup_level, " 거래량 1/3 이하 급감선 (Dry-Up Line) ",
            color=DARK["gold"], fontsize=11.5, fontweight="bold", va="center",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=DARK["panel"], edgecolor=DARK["gold"], lw=1.0, alpha=0.95),
            zorder=7
        )
        ax_vol.annotate(
            "V",
            xy=(12, 61000), xytext=(12, 260000),
            ha="center", va="center", fontsize=13, fontweight="bold", color="#FFFFFF",
            bbox=dict(boxstyle="circle,pad=0.30", facecolor=DARK["cyan"], edgecolor="#FFFFFF", lw=1.5),
            arrowprops=dict(arrowstyle="->", color=DARK["cyan"], lw=2.0, shrinkA=4, shrinkB=4),
            zorder=10
        )
        ax_vol.text(12, 320000, "거래량 89% 급감\n(매도세 고갈 확인)", color=DARK["cyan"],
                    fontsize=11.5, fontweight="bold", ha="center", zorder=10)

        ax_main.set_ylim(9850, 12150)
        ax_vol.set_ylim(0, 600000)
        ax_main.set_ylabel("주가 (KRW)", color=DARK["text_secondary"], fontsize=12.5, labelpad=10)
        ax_vol.set_ylabel("거래량", color=DARK["text_secondary"], fontsize=12.5, labelpad=10)
        ax_main.legend(loc="upper left", facecolor=DARK["panel"], edgecolor=DARK["panel_border"],
                       labelcolor=DARK["text_primary"], fontsize=11.5, framealpha=0.9)

        time_labels = ["09:00", "09:06", "09:12", "09:18", "09:24", "09:30", "09:36", "09:42", "09:48", "09:54", "10:00", "10:06", "10:12"]
        step = 2
        ax_vol.set_xticks(range(0, n_bars, step))
        ax_vol.set_xticklabels([time_labels[i//2] for i in range(0, n_bars, step)], fontsize=11)
        ax_vol.set_xlabel("장중 3분봉/5분봉 진행 시간 (Time)", color=DARK["text_secondary"], fontsize=12, labelpad=5)

        # -------------------------------------------------------------------------
        # 우측 패널: [5단계 실전 매매 프로토콜] 균형 분할 카드 스택
        # -------------------------------------------------------------------------
        ax_panel.text(0.06, 0.948, "■ 5단계 실전 매매 프로토콜", color=DARK["gold"], fontsize=17.5, fontweight="bold")

        steps = [
            (
                "① 09:00~09:20 주도주 압축",
                DARK["bull_red"],
                [
                    "• 당일 거래대금 상위 1~3위 종목 선별",
                    "• 오전 500억↑ 대량 거래대금 집중 확인",
                ]
            ),
            (
                "② 1차 돌파 파동 확인 (추격 금지)",
                DARK["orange"],
                [
                    "• 3분봉/5분봉 장대양봉 전고 돌파 (+7%↑)",
                    "• 고점 추격 매수 100% 금지 (눌림 대기)",
                ]
            ),
            (
                "③ 10이평 수렴 & 거래량 급감",
                DARK["cyan"],
                [
                    "• 10 EMA 선으로 3~5개봉 완만 조정",
                    "• 거래량이 직전 1/3(30%) 이하로 마름",
                ]
            ),
            (
                "④ 10선 지지양봉 종가 매수",
                DARK["gold"],
                [
                    "• 10선 터치 후 지지 양봉 완성 시 진입",
                    "• 호가창 매도잔량 2:1 & 체결강도 120%",
                ]
            ),
            (
                "⑤ 서버 자동감시(-1.5% 손절)",
                DARK["target_green"],
                [
                    "• 매수 즉시 -1.5% 시장가 스탑로스 등록",
                    "• +3.5% 50% 분할 익절 & 10선 추세 홀딩",
                ]
            ),
        ]

        card_starts = [0.885, 0.745, 0.605, 0.465, 0.325]
        for idx, (title, col, lines) in enumerate(steps):
            y_pos = card_starts[idx]
            ax_panel.text(0.06, y_pos, title, color=col, fontsize=14.5, fontweight="bold")
            y_pos -= 0.038
            for raw_line in lines:
                wrapped = textwrap.wrap(raw_line, width=30)
                for w_l in wrapped:
                    ax_panel.text(0.10, y_pos, w_l, color=DARK["text_secondary"], fontsize=12.0)
                    y_pos -= 0.028

        # 하단 자금관리 및 자동감시 박스
        rule_box = FancyBboxPatch(
            (0.035, 0.032), 0.93, 0.140, boxstyle="round,pad=0.02",
            facecolor="#2A1B1D", edgecolor=DARK["stop_red"], linewidth=1.5
        )
        ax_panel.add_patch(rule_box)
        ax_panel.text(0.50, 0.138, "[필독] 증권사 공통 서버 자동감시 헌법", color=DARK["stop_red"], fontsize=12.5, fontweight="bold", ha="center", va="center")
        rule_text_1 = "1. 매수 체결 즉시 서버 감시(-1.5%) 자동 발동 필수"
        rule_text_2 = "2. 손절선 도달 시 이유 불문 100% 시장가 청산"
        ax_panel.text(0.50, 0.098, rule_text_1, color=DARK["text_secondary"], fontsize=11.0, ha="center", va="center")
        ax_panel.text(0.50, 0.062, rule_text_2, color=DARK["gold"], fontsize=11.0, fontweight="bold", ha="center", va="center")

        # VisualQAGuard 6대 게이트 검증
        qa_meta = VisualQAGuard.assert_zero_visual_defects(fig, "STRAT01_5Step_Protocol")

        out_path = self.output_dir / "chart_strat01_5step_protocol.png"
        plt.savefig(out_path, dpi=120, facecolor=DARK["bg"], edgecolor="none")
        plt.close(fig)

        # 루트 에셋 디렉터리 미러링
        shutil.copyfile(out_path, self.root_img_dir / "chart_strat01_5step_protocol.png")

        # SHA-256 감사 매니페스트 기록
        self.manifest.record_asset(out_path, qa_meta)
        return out_path

    def generate_condition_stoploss_diagram(self) -> Path:
        """
        도안 2: 범용 HTS 조건검색식 세팅 룰 & 서버 자동감시주문(-1.5% 칼손절)
        - 좌측(50%): 범용 HTS 조건검색식 4대 필터 룰 (독립 4대 서브 카드 균등 배치)
        - 우측(50%): 서버 자동감시주문(Stop-Loss) 3대 안전장치 (독립 3대 서브 카드 균등 배치)
        - 상단 메타 그리드 및 하단 슬림 경고 배너로 휑한 공백(Dead Space) 100% 해소
        - VisualQAGuard 6대 게이트 검증 및 layout_audit.json 기록
        """
        fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=DARK["bg"])

        # 좌/우 패널 분할 (대칭 여백 확보)
        gs = fig.add_gridspec(
            nrows=1, ncols=2,
            top=0.885, bottom=0.045, left=0.040, right=0.960,
            wspace=0.060
        )
        ax_left = fig.add_subplot(gs[0])
        ax_right = fig.add_subplot(gs[1])

        # 헤더 타이틀 바 (캔버스 안전 여백 준수)
        fig.text(
            0.040, 0.948,
            "맥락트레이딩 실전매뉴얼 #01  |  조건검색식 세팅 룰 & -1.5% 자동감시주문",
            color=DARK["text_primary"], fontsize=17.0, fontweight="bold", va="center", ha="left"
        )
        fig.text(
            0.960, 0.948,
            "★ 전 증권사 공통 표준 가이드",
            color=DARK["gold"], fontsize=15.0, fontweight="bold", va="center", ha="right"
        )

        for ax in (ax_left, ax_right):
            ax.set_facecolor(DARK["panel"])
            for spine in ax.spines.values():
                spine.set_color(DARK["panel_border"])
                spine.set_linewidth(1.5)
            ax.set_xticks([])
            ax.set_yticks([])

        # =========================================================================
        # 좌측 패널: ■ 범용 HTS 조건검색식 4대 필터 룰
        # =========================================================================
        ax_left.text(
            0.5, 0.960, "■ 범용 HTS 조건검색식 4대 필터 룰",
            color=DARK["gold"], fontsize=17.5, fontweight="bold", ha="center"
        )
        ax_left.text(
            0.5, 0.925, "키움·미래에셋·삼성·한국투자·토스 공통 조건식 아키텍처",
            color=DARK["cyan"], fontsize=12.5, ha="center"
        )

        # 1. 상단 요약 배너 (Summary Box)
        summary_l = FancyBboxPatch(
            (0.035, 0.815), 0.930, 0.088, boxstyle="round,pad=0.012,rounding_size=0.015",
            facecolor="#13202E", edgecolor=DARK["cyan"], linewidth=1.3
        )
        ax_left.add_patch(summary_l)
        ax_left.text(0.065, 0.865, "검색 주기: 3분봉 / 5분봉", color=DARK["cyan"], fontsize=13.0, fontweight="bold", ha="left")
        ax_left.text(0.905, 0.865, "검색 대상: 코스피·코스닥 보통주", color=DARK["text_primary"], fontsize=12.5, fontweight="bold", ha="right")
        ax_left.text(0.065, 0.832, "포착 목표: 주도주 1차 눌림목", color=DARK["gold"], fontsize=12.0, ha="left")
        ax_left.text(0.905, 0.832, "결합 룰: A and B and C and D", color=DARK["target_green"], fontsize=12.5, fontweight="bold", ha="right")

        # =========================================================================
        # [수학적 균등 그리드 엔진 (Mathematical Grid Layout Engine)]
        # 상단 배너 바닥(Y_top)과 하단 배너 상단(Y_bottom) 사이의 가용 높이를 기준으로
        # 모든 간격(gap)을 100% 동일하게 고정하고, N개 카드의 높이(h)를 기계적으로 역산 배치
        # =========================================================================
        Y_TOP = 0.815       # 상단 배너 바닥선
        Y_BOTTOM = 0.180    # 하단 배너 상단선 (y=0.040 + h=0.140)
        UNIFORM_GAP = 0.022 # 상단/중간/하단 모든 간격을 단 1px의 오차 없이 0.022로 완전 통일

        def compute_card_layout(y_top: float, y_bottom: float, n_items: int, gap: float) -> tuple[float, list[float]]:
            total_h = y_top - y_bottom
            card_h = (total_h - (n_items + 1) * gap) / n_items
            card_starts = []
            for i in range(n_items):
                b = y_top - (i + 1) * gap - (i + 1) * card_h
                card_starts.append(b)
            return card_h, card_starts

        # 2. 4대 조건 필터 카드 (수학적 균등 분할 배치)
        filter_cards = [
            {
                "id": "[조건 A]",
                "title": "당일 거래대금 최상위 필터",
                "badge": "상위 1~10위 or 300억↑",
                "accent": DARK["cyan"],
                "bg": "#151F2A",
                "lines": [
                    "• 당일 거래대금 상위 1~10위 이내 또는 장중 300억 이상 유입 종목",
                    "• 호가 공백과 잡주 슬리피지(체결 밀림 현상)를 원천적으로 배제"
                ]
            },
            {
                "id": "[조건 B]",
                "title": "1차 급등 모멘텀 필터",
                "badge": "주가등락률 +7% 이상 돌파",
                "accent": DARK["orange"],
                "bg": "#221C18",
                "lines": [
                    "• 09:00 개장 후 당일 주가등락률 +7% 이상 강력 돌파 확인",
                    "• 전일 대비 거래량 폭증을 동반한 장대양봉 발생 종목으로 압축"
                ]
            },
            {
                "id": "[조건 C]",
                "title": "10지수이평선(10 EMA) 이격도 필터",
                "badge": "이격도 98% ~ 102% 근접",
                "accent": DARK["gold"],
                "bg": "#232014",
                "lines": [
                    "• 현재가(종가)와 10 EMA 이격도 98% ~ 102% 이내 완만 수렴",
                    "• 1차 상승 파동 후 10이평선에 첫 번째로 접근(접촉)한 타점 포착"
                ]
            },
            {
                "id": "[조건 D]",
                "title": "거래량 급감(Volume Dry-Up) 필터",
                "badge": "거래량 1차 급등봉 대비 35%↓",
                "accent": DARK["target_green"],
                "bg": "#14221A",
                "lines": [
                    "• 현재 3분봉 거래량 < 1차 급등봉 최대 거래량 대비 35% 이하로 마름",
                    "• 매도세가 완전히 고갈된 '건전한 숨고르기' 여부를 시스템 검증"
                ]
            },
        ]

        card_h_l, card_starts_l = compute_card_layout(Y_TOP, Y_BOTTOM, len(filter_cards), UNIFORM_GAP)

        for idx, item in enumerate(filter_cards):
            c_y = card_starts_l[idx]
            card_patch = FancyBboxPatch(
                (0.035, c_y), 0.930, card_h_l, boxstyle="round,pad=0.010,rounding_size=0.012",
                facecolor=item["bg"], edgecolor=item["accent"], linewidth=1.2
            )
            ax_left.add_patch(card_patch)

            # 헤더: ID + 타이틀 (좌측) / 배지 요약 (우측)
            title_text = f"{item['id']} {item['title']}"
            ax_left.text(0.065, c_y + card_h_l * 0.76, title_text, color=item["accent"], fontsize=12.5, fontweight="bold", va="center")
            ax_left.text(0.920, c_y + card_h_l * 0.76, item["badge"], color=DARK["text_primary"], fontsize=11.5, fontweight="bold", ha="right", va="center")

            # 내부 설명 2줄 (높이 비례 균등 배치)
            ax_left.text(0.065, c_y + card_h_l * 0.47, item["lines"][0], color=DARK["text_secondary"], fontsize=11.0, va="center")
            ax_left.text(0.065, c_y + card_h_l * 0.20, item["lines"][1], color=DARK["text_secondary"], fontsize=11.0, va="center")

        # 3. 하단 핵심 안내 배너 (슬림형, 상단 y=0.180 고정)
        notice_box_l = FancyBboxPatch(
            (0.035, 0.040), 0.930, 0.140, boxstyle="round,pad=0.012,rounding_size=0.015",
            facecolor="#121D28", edgecolor=DARK["cyan"], linewidth=1.4
        )
        ax_left.add_patch(notice_box_l)
        ax_left.text(0.50, 0.142, "[핵심 원칙] 조건검색식은 '자동 매수'가 아닌 '1차 감시용 레이더'", color=DARK["cyan"], fontsize=12.5, fontweight="bold", ha="center")
        ax_left.text(0.50, 0.102, "조건식에 포착된 종목은 시스템이 자동으로 매수하는 것이 아닙니다.", color=DARK["text_secondary"], fontsize=11.5, ha="center")
        ax_left.text(0.50, 0.068, "10선 지지양봉 종가 & 호가창(매도잔량 2:1, 체결강도 120%) 확인 후 진입!", color=DARK["gold"], fontsize=11.5, fontweight="bold", ha="center")

        # =========================================================================
        # 우측 패널: ■ 서버 자동감시주문(Stop-Loss) 3대 안전장치
        # =========================================================================
        ax_right.text(
            0.5, 0.960, "■ 서버 자동감시주문(Stop-Loss) 3대 안전장치",
            color=DARK["target_green"], fontsize=17.5, fontweight="bold", ha="center"
        )
        ax_right.text(
            0.5, 0.925, "뇌동매매와 손절 망설임을 100% 차단하는 기계적 클라우드 시스템",
            color=DARK["text_secondary"], fontsize=12.5, ha="center"
        )

        # 1. 상단 요약 배너 (Summary Box)
        summary_r = FancyBboxPatch(
            (0.035, 0.815), 0.930, 0.088, boxstyle="round,pad=0.012,rounding_size=0.015",
            facecolor="#15241C", edgecolor=DARK["target_green"], linewidth=1.3
        )
        ax_right.add_patch(summary_r)
        ax_right.text(0.065, 0.865, "감시 주체: 클라우드 서버", color=DARK["target_green"], fontsize=13.0, fontweight="bold", ha="left")
        ax_right.text(0.905, 0.865, "환경: HTS 종료 후에도 100% 실행", color=DARK["gold"], fontsize=12.5, fontweight="bold", ha="right")
        ax_right.text(0.065, 0.832, "주문 방식: 조건 만족 시 시장가", color=DARK["stop_red"], fontsize=12.0, fontweight="bold", ha="left")
        ax_right.text(0.905, 0.832, "체결 지연: 0초 (감정 배제 실시간)", color=DARK["cyan"], fontsize=12.5, ha="right")

        # 2. 3대 안전장치 와이드 카드 (Equal Spacing 균등 배치: y=0.215 ~ 0.795)
        # card_h = 0.175, gap = 0.025 -> 3 * 0.175 + 2 * 0.025 = 0.575
        safety_cards = [
            {
                "id": "1. [손실 제한]",
                "title": "-1.5% 기계적 칼손절",
                "badge": "[계좌 생존 헌법]",
                "accent": DARK["stop_red"],
                "bg": "#251619",
                "lines": [
                    "• 설정 조건: 진입 평단가 대비 -1.5% 터치 시 0.1초 망설임 없이 즉시 발동",
                    "• 주문 방식: 서버 감시 기반 '시장가 매도'로 보유 수량 전량 즉시 청산",
                    "• 핵심 의의: 손실 비대칭성(Loss Asymmetry) 차단 및 단 1번의 뇌동 파멸 방어"
                ]
            },
            {
                "id": "2. [수익 락인]",
                "title": "+3.5% 1차 분할 익절",
                "badge": "[손익비 1:2.3 달성]",
                "accent": DARK["target_green"],
                "bg": "#14251B",
                "lines": [
                    "• 설정 조건: 진입 평단가 대비 +3.5% 도달 시 보유 물량의 50% 즉시 매도",
                    "• 심리 효과: 확정 수익 락인(Lock-in)으로 잔여 물량 홀딩 심리적 안정 확보",
                    "• 손익비 룰: 1회 손실 리스크 1.5% vs 1차 리워드 3.5% (기대값 양수 구조)"
                ]
            },
            {
                "id": "3. [추세 추종]",
                "title": "잔여 50% 10이평선 트레일링 스탑",
                "badge": "[신고가 랠리 완주]",
                "accent": DARK["gold"],
                "bg": "#231F14",
                "lines": [
                    "• 설정 조건: 3분봉/5분봉 10이평선을 종가상 하향 이탈하기 전까지 끝까지 홀딩",
                    "• 추세 효과: 당일 주도주의 2차 파동 및 신고가 랠리(+7%~+10%↑) 수익 극대화",
                    "• 본전 보존: 1차 익절 완료 즉시 스탑로스 기준을 매수가(본전)로 자동 상향"
                ]
            },
        ]

        card_h_r, card_starts_r = compute_card_layout(Y_TOP, Y_BOTTOM, len(safety_cards), UNIFORM_GAP)

        for idx, item in enumerate(safety_cards):
            c_y = card_starts_r[idx]
            card_patch = FancyBboxPatch(
                (0.035, c_y), 0.930, card_h_r, boxstyle="round,pad=0.010,rounding_size=0.012",
                facecolor=item["bg"], edgecolor=item["accent"], linewidth=1.2
            )
            ax_right.add_patch(card_patch)

            # 헤더: ID + 타이틀 (좌측) / 배지 요약 (우측)
            title_text = f"{item['id']} {item['title']}"
            ax_right.text(0.065, c_y + card_h_r * 0.80, title_text, color=item["accent"], fontsize=13.0, fontweight="bold", va="center")
            ax_right.text(0.920, c_y + card_h_r * 0.80, item["badge"], color=DARK["text_primary"], fontsize=11.5, fontweight="bold", ha="right", va="center")

            # 내부 설명 3줄 (높이 비례 균등 배치)
            ax_right.text(0.065, c_y + card_h_r * 0.56, item["lines"][0], color=DARK["text_secondary"], fontsize=11.0, va="center")
            ax_right.text(0.065, c_y + card_h_r * 0.35, item["lines"][1], color=DARK["text_secondary"], fontsize=11.0, va="center")
            ax_right.text(0.065, c_y + card_h_r * 0.14, item["lines"][2], color=DARK["text_secondary"], fontsize=11.0, va="center")

        # 3. 하단 경고 배너 (슬림형, 상단 y=0.180 고정)
        alert_box_r = FancyBboxPatch(
            (0.035, 0.040), 0.930, 0.140, boxstyle="round,pad=0.012,rounding_size=0.015",
            facecolor="#251619", edgecolor=DARK["stop_red"], linewidth=1.4
        )
        ax_right.add_patch(alert_box_r)
        ax_right.text(0.50, 0.142, "[필독 헌법] 맥락트레이딩 스탑로스 2대 절대 금지 수칙", color=DARK["stop_red"], fontsize=12.5, fontweight="bold", ha="center")
        ax_right.text(0.50, 0.102, "1. 주가 하락 시 손절선을 아래로 내리거나 취소하는 행위 0% 영구 금지", color=DARK["text_secondary"], fontsize=11.5, ha="center")
        ax_right.text(0.50, 0.068, "2. 지지선 이탈 시 평단가를 낮추기 위한 물타기(추가 매수) 영구 엄금!", color=DARK["gold"], fontsize=11.5, fontweight="bold", ha="center")

        # VisualQAGuard 6대 게이트 검증
        qa_meta = VisualQAGuard.assert_zero_visual_defects(fig, "STRAT01_Condition_StopLoss_Guide")

        out_path = self.output_dir / "chart_strat01_condition_stoploss_guide.png"
        plt.savefig(out_path, dpi=120, facecolor=DARK["bg"], edgecolor="none")
        plt.close(fig)

        # 루트 에셋 디렉터리 미러링
        shutil.copyfile(out_path, self.root_img_dir / "chart_strat01_condition_stoploss_guide.png")

        # SHA-256 감사 매니페스트 기록
        self.manifest.record_asset(out_path, qa_meta)
        return out_path

        # VisualQAGuard 6대 게이트 검증
        qa_meta = VisualQAGuard.assert_zero_visual_defects(fig, "STRAT01_Condition_StopLoss_Guide")

        out_path = self.output_dir / "chart_strat01_condition_stoploss_guide.png"
        plt.savefig(out_path, dpi=120, facecolor=DARK["bg"], edgecolor="none")
        plt.close(fig)

        # 루트 에셋 디렉터리 미러링
        shutil.copyfile(out_path, self.root_img_dir / "chart_strat01_condition_stoploss_guide.png")

        # SHA-256 감사 매니페스트 기록
        self.manifest.record_asset(out_path, qa_meta)
        return out_path


if __name__ == "__main__":
    out_dir = Path("growth_engine/03_blog_hub/stock_blog/assets/img/posts")
    generator = Strat01InfographicsGenerator(out_dir)
    p1 = generator.generate_5step_protocol_chart()
    p2 = generator.generate_condition_stoploss_diagram()
    print("Successfully Generated and Audited:")
    print("1:", p1)
    print("2:", p2)
