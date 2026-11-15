"""
16:9 Dark-Theme Financial Infographic Generator for Alpha Context Blog.
Generates:
1. chart_3min_5min_10ma_pullback.png (Candlestick chart, 10MA neon gold, volume dry-up, buy/stop/target callouts)
2. orderbook_spoofing_execution_strength.png (Orderbook depth paradox, fake bid trap vs ask wall absorption, execution strength)

100% Deterministic, pure matplotlib/PIL/numpy offline execution (0% external network).
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Arrow
import numpy as np
from PIL import Image

# 1. 한글 폰트 및 글로벌 렌더링 설정
font_candidates = ["Malgun Gothic", "NanumGothic", "Noto Sans KR", "Gulim", "sans-serif"]
plt.rcParams["font.family"] = font_candidates
plt.rcParams["axes.unicode_minus"] = False

DARK_THEME = {
    "bg": "#121212",
    "panel": "#181B20",
    "panel_border": "#2D333B",
    "grid": "#22272E",
    "text_primary": "#FFFFFF",
    "text_secondary": "#C9D1D9",
    "text_muted": "#8B949E",
    "gold": "#FFD700",
    "cyan": "#38BDF8",
    "orange": "#FB923C",
    "bull_red": "#FF334B",
    "bear_blue": "#2979FF",
    "stop_red": "#FF5252",
    "target_green": "#00E676",
    "card_dark": "#21262D",
}


class ChartInfographicsEngine:
    def __init__(self, blog_root: Path):
        self.blog_root = blog_root
        self.posts_img_dir = blog_root / "assets" / "img" / "posts"
        self.root_img_dir = blog_root / "assets" / "img"
        self.posts_img_dir.mkdir(parents=True, exist_ok=True)
        self.root_img_dir.mkdir(parents=True, exist_ok=True)

    def generate_10ma_pullback_chart(self) -> Path:
        """
        도안 1: 3분봉/5분봉 10이평선 첫 눌림목 정석 타점 인포그래픽
        16:9 비율 (1920x1080 px, 120 DPI)
        """
        fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=DARK_THEME["bg"])

        # GridSpec: Header (0.0~0.12), Main Chart (0.16~0.68), Volume Chart (0.72~0.96)
        gs = fig.add_gridspec(
            nrows=2, ncols=1,
            height_ratios=[7, 3],
            top=0.88, bottom=0.08, left=0.06, right=0.94,
            hspace=0.10
        )
        ax_main = fig.add_subplot(gs[0])
        ax_vol = fig.add_subplot(gs[1], sharex=ax_main)

        for ax in (ax_main, ax_vol):
            ax.set_facecolor(DARK_THEME["panel"])
            for spine in ax.spines.values():
                spine.set_color(DARK_THEME["panel_border"])
                spine.set_linewidth(1.2)
            ax.tick_params(colors=DARK_THEME["text_muted"], labelsize=11)
            ax.grid(True, linestyle="--", linewidth=0.7, color=DARK_THEME["grid"], alpha=0.7)

        # -------------------------------------------------------------------------
        # 결정론적 25개 분봉 캔들 데이터 생성
        # 0~4: 횡보/준비 -> 5~9: 1차 급등(+10%) -> 10~14: 거래량 급감 눌림목 -> 15: 10선 지지 양봉(타점) -> 16~24: 2차 랠리
        # -------------------------------------------------------------------------
        n_bars = 25
        # O, H, L, C, Volume
        candles = [
            # 0~4: 횡보
            (10000, 10080, 9980, 10050, 45000),
            (10050, 10120, 10020, 10080, 52000),
            (10080, 10100, 10000, 10020, 38000),
            (10020, 10150, 10010, 10120, 61000),
            (10120, 10220, 10100, 10200, 78000),
            # 5~9: 1차 강력 돌파 파동 (장대양봉 + 초대형 거래대금)
            (10200, 10550, 10180, 10500, 320000),
            (10500, 10800, 10450, 10750, 410000),
            (10750, 11050, 10700, 10980, 480000),
            (10980, 11250, 10920, 11200, 550000), # 1차 파동 고점 (11,250원, +12.5%)
            (11200, 11280, 11050, 11100, 380000),
            # 10~14: 10이평선 수렴 눌림목 (거래량 1/3 급감)
            (11100, 11150, 10900, 10950, 145000),
            (10950, 11000, 10820, 10850, 110000),
            (10850, 10900, 10740, 10760, 85000),
            (10760, 10820, 10680, 10700, 72000),
            (10700, 10750, 10640, 10660, 68000), # 거래량 최저치 (피크 대비 12%)
            # 15: ★ 10이평선 지지 반등 타점 캔들 (긴 밑꼬리 + 10선 지지 양봉)
            (10660, 10800, 10610, 10760, 195000), # 저가 10,610원 터치 후 10,760원 양봉 마감
            # 16~24: 2차 상승 랠리 (+3.5% 1차 익절 도달 및 전고점 돌파)
            (10760, 10950, 10740, 10920, 260000),
            (10920, 11150, 10900, 11120, 340000), # +3.5% 1차 익절 도달 (11,130원)
            (11120, 11300, 11080, 11260, 420000),
            (11260, 11420, 11220, 11380, 470000),
            (11380, 11500, 11340, 11460, 390000),
            (11460, 11580, 11420, 11540, 350000),
            (11540, 11620, 11480, 11580, 310000),
            (11580, 11650, 11520, 11620, 280000),
            (11620, 11700, 11580, 11680, 260000),
        ]

        closes = [c[3] for c in candles]
        highs = [c[1] for c in candles]
        lows = [c[2] for c in candles]
        opens = [c[0] for c in candles]
        volumes = [c[4] for c in candles]

        # 이동평균선 계산 (SMA / EMA)
        def calc_ema(series, period):
            res = []
            multiplier = 2 / (period + 1)
            ema = series[0]
            for val in series:
                ema = (val - ema) * multiplier + ema
                res.append(ema)
            return res

        ma5 = [np.mean(closes[max(0, i-4):i+1]) for i in range(n_bars)]
        ma10 = calc_ema(closes, 10)
        ma20 = [np.mean(closes[max(0, i-19):i+1]) for i in range(n_bars)]

        # 캔들스틱 작도
        for i in range(n_bars):
            o, h, l, c, v = candles[i]
            is_bull = c >= o
            color = DARK_THEME["bull_red"] if is_bull else DARK_THEME["bear_blue"]

            # 심지 (Wick)
            ax_main.plot([i, i], [l, h], color=color, linewidth=1.5, zorder=3)

            # 몸통 (Body)
            body_bottom = min(o, c)
            body_height = max(abs(c - o), 15)
            rect = Rectangle(
                (i - 0.32, body_bottom), 0.64, body_height,
                facecolor=color, edgecolor=color, linewidth=1.0, zorder=4
            )
            ax_main.add_patch(rect)

            # 거래량 바
            v_color = DARK_THEME["bull_red"] if is_bull else DARK_THEME["bear_blue"]
            ax_vol.bar(i, v, width=0.64, color=v_color, alpha=0.85, zorder=3)

        # 이동평균선 플롯
        x_axis = np.arange(n_bars)
        ax_main.plot(x_axis, ma5, label="5선 (단기 공격선)", color=DARK_THEME["cyan"], linewidth=1.8, alpha=0.9, zorder=5)
        ax_main.plot(x_axis, ma10, label="★ 10선 (핵심 생명선)", color=DARK_THEME["gold"], linewidth=3.4, alpha=1.0, zorder=6)
        ax_main.plot(x_axis, ma20, label="20선 (단기 추세선)", color=DARK_THEME["orange"], linewidth=1.8, alpha=0.85, zorder=5)

        # -------------------------------------------------------------------------
        # 중요 가격 기준선 및 손익비 라벨링
        # 진입가: 15번 봉 종가 10,760원
        # -1.5% 칼손절가: 10,760 * 0.985 = 10,598원 (~10,600원)
        # +3.5% 1차 익절가: 10,760 * 1.035 = 11,136원 (~11,140원)
        # -------------------------------------------------------------------------
        entry_price = 10760
        stop_loss_price = 10600
        take_profit_price = 11140

        # 손절선 (-1.5%)
        ax_main.axhline(stop_loss_price, color=DARK_THEME["stop_red"], linestyle="--", linewidth=1.8, alpha=0.9, zorder=2)
        ax_main.text(
            0.5, stop_loss_price - 60, "[손절] -1.5% 기계적 칼손절선 (10,600원 | HTS 0621 자동 시장가 청산)",
            color=DARK_THEME["stop_red"], fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor=DARK_THEME["bg"], edgecolor=DARK_THEME["stop_red"], alpha=0.85)
        )

        # 1차 익절선 (+3.5%)
        ax_main.axhline(take_profit_price, color=DARK_THEME["target_green"], linestyle="--", linewidth=1.8, alpha=0.9, zorder=2)
        ax_main.text(
            0.5, take_profit_price + 40, "[익절] +3.5% 1차 분할 익절선 (11,140원 | 50% 물량 확정 락인, 손익비 1:2.3 달성)",
            color=DARK_THEME["target_green"], fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor=DARK_THEME["bg"], edgecolor=DARK_THEME["target_green"], alpha=0.85)
        )

        # -------------------------------------------------------------------------
        # 주요 국면 콜아웃 배지 (4단계 프로세스)
        # -------------------------------------------------------------------------
        # 1. 1차 급등 파동 (캔들 8 상단)
        ax_main.annotate(
            "① 1차 급등 돌파 (+12.5%)\n- 당일 거래대금 최상위 주도주\n- 강력한 연속 장대양봉",
            xy=(8, 11250), xytext=(4.5, 11520),
            arrowprops=dict(facecolor=DARK_THEME["bull_red"], edgecolor="none", width=2, headwidth=7),
            fontsize=10.5, color=DARK_THEME["text_primary"], fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=DARK_THEME["card_dark"], edgecolor=DARK_THEME["bull_red"], linewidth=1.5)
        )

        # 2. 거래량 급감 눌림목 (캔들 12)
        ax_main.annotate(
            "② 10이평선 수렴 눌림목\n- 거래량 직전 대비 1/3 이하 급감\n- 매도 주체 부재(스마트머니 잠김)",
            xy=(12, 10850), xytext=(10.0, 11350),
            arrowprops=dict(facecolor=DARK_THEME["cyan"], edgecolor="none", width=1.8, headwidth=6),
            fontsize=10, color=DARK_THEME["text_primary"],
            bbox=dict(boxstyle="round,pad=0.4", facecolor=DARK_THEME["card_dark"], edgecolor=DARK_THEME["cyan"], linewidth=1.2)
        )

        # 3. ★ 10이평선 지지 양봉 타점 (캔들 15)
        ax_main.annotate(
            "★ ③ 10선 지지 양봉 종가 매수!\n- 10 EMA 밑꼬리 터치 반등 확인\n- 진입가: 10,760원 (손익비 1:2.3)",
            xy=(15, 10610), xytext=(14.2, 10180),
            arrowprops=dict(facecolor=DARK_THEME["gold"], edgecolor="none", width=2.5, headwidth=9),
            fontsize=11.5, color=DARK_THEME["gold"], fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=DARK_THEME["card_dark"], edgecolor=DARK_THEME["gold"], linewidth=2.0)
        )

        # 4. 2차 랠리 및 전고점 돌파 (캔들 19)
        ax_main.annotate(
            "④ 2차 랠리 & 신고가 돌파\n- 잔여 50% 10선 이탈 전까지 홀딩\n- 추세 극대화 (+8~10%)",
            xy=(19, 11420), xytext=(18.5, 11000),
            arrowprops=dict(facecolor=DARK_THEME["target_green"], edgecolor="none", width=1.8, headwidth=6),
            fontsize=10, color=DARK_THEME["text_primary"],
            bbox=dict(boxstyle="round,pad=0.4", facecolor=DARK_THEME["card_dark"], edgecolor=DARK_THEME["target_green"], linewidth=1.2)
        )

        # 거래량 차트 내 기준선 및 주석
        dryup_level = 150000 # 550,000의 1/3 미만 기준선
        ax_vol.axhline(dryup_level, color=DARK_THEME["gold"], linestyle=":", linewidth=1.5, alpha=0.9)
        ax_vol.text(
            0.5, dryup_level + 15000, "── 거래량 1/3 (30%) 급감 기준선 (Dry-Up Line) ──",
            color=DARK_THEME["gold"], fontsize=9.5, fontweight="bold"
        )
        ax_vol.text(
            11.5, 50000, "거래량 87% 급감\n(매도세 고갈 증명)",
            color=DARK_THEME["cyan"], fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=DARK_THEME["bg"], edgecolor=DARK_THEME["cyan"], alpha=0.8)
        )

        # 축 레이블 및 범위
        ax_main.set_ylim(9900, 11800)
        ax_main.set_ylabel("주가 (KRW)", color=DARK_THEME["text_secondary"], fontsize=12, labelpad=8)
        ax_main.legend(loc="upper left", facecolor=DARK_THEME["card_dark"], edgecolor=DARK_THEME["panel_border"],
                       labelcolor=DARK_THEME["text_primary"], fontsize=10.5)

        ax_vol.set_ylim(0, 650000)
        ax_vol.set_ylabel("거래량 (Volume)", color=DARK_THEME["text_secondary"], fontsize=11, labelpad=8)
        ax_vol.set_xlabel("장중 3분봉 / 5분봉 진행 캔들 순서 (Time Elapsed)", color=DARK_THEME["text_secondary"], fontsize=11, labelpad=8)

        # 시간 표시 가상 레이블
        time_labels = [f"09:{i*3:02d}" if i*3 < 60 else f"10:{(i*3)-60:02d}" for i in range(n_bars)]
        ax_vol.set_xticks(range(0, n_bars, 2))
        ax_vol.set_xticklabels([time_labels[i] for i in range(0, n_bars, 2)])

        # 상단 통합 헤더 박스
        fig.text(
            0.06, 0.945, "맥락트레이딩 실전 차트강의 #01: 3분봉·5분봉 10이평선 첫 눌림목 정석 매수 타점 & -1.5% 칼손절",
            color=DARK_THEME["text_primary"], fontsize=16, fontweight="bold"
        )
        fig.text(
            0.06, 0.915, "대량 수급 주도주 1차 돌파 ➔ 거래량 1/3 급감(Volume Dry-Up) ➔ 10선 지지 밑꼬리 양봉 종가 진입 공식",
            color=DARK_THEME["gold"], fontsize=11.5
        )

        out_path = self.posts_img_dir / "chart_3min_5min_10ma_pullback.png"
        fig.savefig(out_path, facecolor=DARK_THEME["bg"], edgecolor="none", dpi=120)
        plt.close(fig)

        # 루트 에셋 디렉터리 및 별칭 동기화
        shutil.copyfile(out_path, self.root_img_dir / "chart_3min_5min_10ma_pullback.png")
        shutil.copyfile(out_path, self.posts_img_dir / "chart_10ma_pullback_infographic.png")
        shutil.copyfile(out_path, self.root_img_dir / "chart_10ma_pullback_infographic.png")
        shutil.copyfile(out_path, self.posts_img_dir / "chart_lecture_01_pullback_setup.png")
        shutil.copyfile(out_path, self.root_img_dir / "chart_lecture_01_pullback_setup.png")
        return out_path

    def generate_orderbook_diagram(self) -> Path:
        """
        도안 2: 호가 잔량의 역설 & 허매수벽 트랩 vs 매도벽 흡수 구조도
        16:9 비율 (1920x1080 px, 120 DPI)
        """
        fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=DARK_THEME["bg"])

        # 좌측 패널(착시 급락형 호가창) vs 우측 패널(진짜 폭등형 호가창)
        gs = fig.add_gridspec(
            nrows=1, ncols=2,
            top=0.86, bottom=0.14, left=0.06, right=0.94,
            wspace=0.12
        )
        ax_left = fig.add_subplot(gs[0])
        ax_right = fig.add_subplot(gs[1])

        for ax in (ax_left, ax_right):
            ax.set_facecolor(DARK_THEME["panel"])
            for spine in ax.spines.values():
                spine.set_color(DARK_THEME["panel_border"])
                spine.set_linewidth(1.2)
            ax.set_xticks([])
            ax.set_yticks([])

        # =========================================================================
        # 좌측 패널: [위험한 착시] 급락형 호가창 (Fake Bid Trap)
        # =========================================================================
        ax_left.text(
            0.5, 0.95, "[위험한 착시] 급락형 호가창 (Fake Bid Wall Trap)",
            color=DARK_THEME["stop_red"], fontsize=14, fontweight="bold", ha="center"
        )
        ax_left.text(
            0.5, 0.90, "초보자의 오판: '매수잔량이 매도잔량보다 6배 많으니 든든하다?'",
            color=DARK_THEME["text_muted"], fontsize=10.5, ha="center"
        )

        # 상단 총잔량 요약 박스
        left_summary = FancyBboxPatch(
            (0.08, 0.77), 0.84, 0.10, boxstyle="round,pad=0.02",
            facecolor="#2A1B1D", edgecolor=DARK_THEME["stop_red"], linewidth=1.5
        )
        ax_left.add_patch(left_summary)
        ax_left.text(0.12, 0.83, "매도총잔량: 45,000주", color=DARK_THEME["bear_blue"], fontsize=11.5, fontweight="bold")
        ax_left.text(0.55, 0.83, "매수총잔량: 285,000주", color=DARK_THEME["stop_red"], fontsize=11.5, fontweight="bold")
        ax_left.text(0.12, 0.79, "비율: 1 : 6.3 (극단적 매수 우위 착시)", color=DARK_THEME["text_muted"], fontsize=10)
        ax_left.text(0.55, 0.79, "체결강도: 62% (매도세 압도)", color=DARK_THEME["stop_red"], fontsize=10.5, fontweight="bold")

        # 6단계 호가 테이블 (매도 3호가 + 매수 3호가)
        order_rows_left = [
            ("매도 3호가 (10,150원)", "12,000주", DARK_THEME["bear_blue"], 0.15),
            ("매도 2호가 (10,100원)", "18,000주", DARK_THEME["bear_blue"], 0.22),
            ("매도 1호가 (10,050원)", "15,000주", DARK_THEME["bear_blue"], 0.18),
            # 현재가 기준선 (10,000원)
            ("매수 1호가 (10,000원)", "25,000주", DARK_THEME["bull_red"], 0.25),
            ("매수 2호가 ( 9,950원)", "30,000주", DARK_THEME["bull_red"], 0.30),
            ("매수 3호가 ( 9,900원)", "130,000주 ★", DARK_THEME["stop_red"], 0.85), # 거대 허매수벽
        ]

        y_start = 0.68
        for i, (label, qty, col, bar_len) in enumerate(order_rows_left):
            y = y_start - i * 0.072
            # 호가 배경 바
            bar_color = col
            rect = Rectangle((0.45, y - 0.015), bar_len * 0.45, 0.05, facecolor=bar_color, alpha=0.25)
            ax_left.add_patch(rect)
            # 호가 텍스트
            ax_left.text(0.08, y, label, color=DARK_THEME["text_secondary"], fontsize=10.5)
            ax_left.text(0.48, y, qty, color=col, fontsize=10.5, fontweight="bold")

        # 허매수벽 강조 박스
        fake_wall_callout = FancyBboxPatch(
            (0.08, 0.22), 0.84, 0.09, boxstyle="round,pad=0.02",
            facecolor=DARK_THEME["card_dark"], edgecolor=DARK_THEME["stop_red"], linewidth=1.2
        )
        ax_left.add_patch(fake_wall_callout)
        ax_left.text(0.11, 0.27, "[주의] 매수 3호가 13만 주: 세력의 '허매수벽(Fake Bid)' 트랩", color=DARK_THEME["stop_red"], fontsize=10.5, fontweight="bold")
        ax_left.text(0.11, 0.235, "개미에게 '안전판' 착시를 주며 위에서 시장가로 매도 물량 투하 후, 취소!", color=DARK_THEME["text_muted"], fontsize=9.5)

        # 결과 배지
        result_left = FancyBboxPatch(
            (0.08, 0.08), 0.84, 0.09, boxstyle="round,pad=0.02",
            facecolor="#3D1216", edgecolor=DARK_THEME["stop_red"], linewidth=1.5
        )
        ax_left.add_patch(result_left)
        ax_left.text(0.12, 0.13, "[결과] 매수벽 순간 취소 -> 호가 공백(Air Pocket) 수직 폭락", color="#FFA4A4", fontsize=11, fontweight="bold")
        ax_left.text(0.12, 0.095, "매수잔량만 보고 진입한 개미 전원 물림 (체결강도 62% = 시장가 매도 폭탄)", color=DARK_THEME["text_muted"], fontsize=9.5)

        # =========================================================================
        # 우측 패널: [진짜 폭등] 상승형 호가창 (보컬의 매도벽 흡수 법칙)
        # =========================================================================
        ax_right.text(
            0.5, 0.95, "★ [진짜 폭등] 상승형 호가창 (보컬의 매도벽 흡수 법칙)",
            color=DARK_THEME["gold"], fontsize=14, fontweight="bold", ha="center"
        )
        ax_right.text(
            0.5, 0.90, "실전 대가의 통찰: '매도잔량이 2~3배 많아야 상승 연료가 된다!'",
            color=DARK_THEME["cyan"], fontsize=10.5, ha="center"
        )

        # 상단 총잔량 요약 박스
        right_summary = FancyBboxPatch(
            (0.08, 0.77), 0.84, 0.10, boxstyle="round,pad=0.02",
            facecolor="#162A22", edgecolor=DARK_THEME["gold"], linewidth=1.5
        )
        ax_right.add_patch(right_summary)
        ax_right.text(0.12, 0.83, "매도총잔량: 380,000주 ★", color=DARK_THEME["gold"], fontsize=11.5, fontweight="bold")
        ax_right.text(0.55, 0.83, "매수총잔량: 115,000주", color=DARK_THEME["cyan"], fontsize=11.5, fontweight="bold")
        ax_right.text(0.12, 0.79, "비율: 3.3 : 1 (황금 매도벽 우위)", color=DARK_THEME["text_primary"], fontsize=10, fontweight="bold")
        ax_right.text(0.55, 0.79, "체결강도: 148% (공격적 시장가 매수)", color=DARK_THEME["target_green"], fontsize=10.5, fontweight="bold")

        # 6단계 호가 테이블 (매도 3호가 + 매수 3호가)
        order_rows_right = [
            ("매도 3호가 (10,150원)", "110,000주", DARK_THEME["bear_blue"], 0.75),
            ("매도 2호가 (10,100원)", "135,000주", DARK_THEME["bear_blue"], 0.88),
            ("매도 1호가 (10,050원)", " 85,000주 ★", DARK_THEME["gold"], 0.60), # 공격 매수 흡수 대상
            # 현재가 기준선 (10,000원)
            ("매수 1호가 (10,000원)", " 25,000주", DARK_THEME["bull_red"], 0.20),
            ("매수 2호가 ( 9,950원)", " 38,000주", DARK_THEME["bull_red"], 0.28),
            ("매수 3호가 ( 9,900원)", " 22,000주", DARK_THEME["bull_red"], 0.18),
        ]

        for i, (label, qty, col, bar_len) in enumerate(order_rows_right):
            y = y_start - i * 0.072
            # 호가 배경 바
            bar_color = col
            rect = Rectangle((0.45, y - 0.015), bar_len * 0.45, 0.05, facecolor=bar_color, alpha=0.30)
            ax_right.add_patch(rect)
            # 호가 텍스트
            ax_right.text(0.08, y, label, color=DARK_THEME["text_secondary"], fontsize=10.5)
            ax_right.text(0.48, y, qty, color=col, fontsize=10.5, fontweight="bold")

        # 매도벽 흡수 강조 박스
        absorption_callout = FancyBboxPatch(
            (0.08, 0.22), 0.84, 0.09, boxstyle="round,pad=0.02",
            facecolor=DARK_THEME["card_dark"], edgecolor=DARK_THEME["gold"], linewidth=1.2
        )
        ax_right.add_patch(absorption_callout)
        ax_right.text(0.11, 0.27, "[원리] 매도 1~3호가 대량 물량: 세력의 '공격적 흡수(Absorption)'", color=DARK_THEME["gold"], fontsize=10.5, fontweight="bold")
        ax_right.text(0.11, 0.235, "상단 매도벽을 거대한 시장가 매수 빅오더로 격파하며 가볍게 주가 부양!", color=DARK_THEME["text_muted"], fontsize=9.5)

        # 결과 배지
        result_right = FancyBboxPatch(
            (0.08, 0.08), 0.84, 0.09, boxstyle="round,pad=0.02",
            facecolor="#103822", edgecolor=DARK_THEME["target_green"], linewidth=1.5
        )
        ax_right.add_patch(result_right)
        ax_right.text(0.12, 0.13, "[결과] 매도벽 돌파 -> 거래대금 폭증 및 상방 신고가 랠리", color=DARK_THEME["target_green"], fontsize=11, fontweight="bold")
        ax_right.text(0.12, 0.095, "매도총잔량이 상승의 연료로 작용 (체결강도 148% = 강력한 매수 드라이브)", color=DARK_THEME["text_muted"], fontsize=9.5)

        # 상단 통합 헤더
        fig.text(
            0.06, 0.945, "맥락트레이딩 실전 호가창 강의 #01: 호가 잔량의 역설 & 허매수벽 트랩 vs 매도벽 흡수 구조도",
            color=DARK_THEME["text_primary"], fontsize=16, fontweight="bold"
        )
        fig.text(
            0.06, 0.915, "지정가 대기 잔량의 착시 타파 | 매도총잔량 2~3배 우위 법칙 & 체결강도 120% 돌파의 미시 수급 물리학",
            color=DARK_THEME["gold"], fontsize=11.5
        )

        # 하단 통합 미시수급 원리 띠 배너
        bottom_banner = FancyBboxPatch(
            (0.06, 0.02), 0.88, 0.05, boxstyle="round,pad=0.01",
            facecolor="#1A1F29", edgecolor=DARK_THEME["panel_border"], linewidth=1.0
        )
        fig.patches.append(bottom_banner)
        fig.text(
            0.50, 0.045, "[미시수급 절대 공식]  지정가(Limit) = 대기 물량 (주가를 올리지 못함)  vs  시장가(Market) = 공격 물량 (매도벽을 돈으로 부숴야 주가 폭등)",
            color=DARK_THEME["cyan"], fontsize=11, fontweight="bold", ha="center"
        )

        out_path = self.posts_img_dir / "orderbook_spoofing_execution_strength.png"
        fig.savefig(out_path, facecolor=DARK_THEME["bg"], edgecolor="none", dpi=120)
        plt.close(fig)

        # 루트 에셋 디렉터리 및 별칭 동기화
        shutil.copyfile(out_path, self.root_img_dir / "orderbook_spoofing_execution_strength.png")
        shutil.copyfile(out_path, self.posts_img_dir / "orderbook_power_structure.png")
        shutil.copyfile(out_path, self.root_img_dir / "orderbook_power_structure.png")
        shutil.copyfile(out_path, self.posts_img_dir / "chart_lecture_01_orderbook_dynamics.png")
        shutil.copyfile(out_path, self.root_img_dir / "chart_lecture_01_orderbook_dynamics.png")
        return out_path


def main():
    blog_root = Path(__file__).resolve().parent.parent
    print(f"[*] Initializing Chart Infographics Engine (Root: {blog_root})")
    engine = ChartInfographicsEngine(blog_root)

    p1 = engine.generate_10ma_pullback_chart()
    print(f"[+] Successfully generated pullback chart: {p1}")

    p2 = engine.generate_orderbook_diagram()
    print(f"[+] Successfully generated orderbook diagram: {p2}")

    # 검증 출력
    for p in [p1, p2]:
        im = Image.open(p)
        w, h = im.size
        ratio = round(w / h, 4)
        print(f"    - Image: {p.name} | Size: {w}x{h} px | Ratio: {ratio} (Target: 1.7778)")

    print("[SUCCESS] All 16:9 dark theme chart infographics generated and verified.")


if __name__ == "__main__":
    main()
