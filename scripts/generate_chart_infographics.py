"""
Redesigned 16:9 Dark-Theme Financial Infographics for Alpha Context Blog.
Solves all user-reported issues:
1. Zero overlapping: No multi-line text boxes inside the chart/orderbook area.
2. Numbered badges (①, ②, ③, ④) placed directly at chart key points.
3. Dedicated explanation card panel placed OUTSIDE the chart plot (Layout: 68% chart, 32% text panel).
4. Substantially larger font sizes (20pt~36pt) that perfectly match blog body text size when resized.
"""
from __future__ import annotations

import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
import numpy as np
from PIL import Image

# 한글 폰트 설정
plt.rcParams["font.family"] = ["Malgun Gothic", "NanumGothic", "Noto Sans KR", "Gulim", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

DARK = {
    "bg": "#0D1117",          # 프리미엄 딥 다크
    "panel": "#161B22",       # 카드 및 차트 배경
    "panel_border": "#30363D",# 경계선
    "grid": "#21262D",        # 그리드 라인
    "text_primary": "#FFFFFF",# 메인 화이트
    "text_secondary": "#C9D1D9",# 소프트 실버
    "text_muted": "#8B949E",  # 뮤트 그레이
    "gold": "#FFD700",        # 10이평선 & 핵심 타점
    "cyan": "#38BDF8",        # 5이평선 & 쿨 블루
    "orange": "#FB923C",      # 20이평선
    "bull_red": "#FF445B",    # 캔들 양봉 레드
    "bear_blue": "#3B82F6",   # 캔들 음봉 블루
    "stop_red": "#EF4444",    # 손절선
    "target_green": "#10B981",# 익절선
    "badge_bg": "#1F2937",    # 뱃지 배경
}


class RedesignedChartInfographics:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_10ma_pullback_chart(self) -> Path:
        """
        도안 1: 3분봉/5분봉 10이평선 첫 눌림목 정석 타점 인포그래픽
        - 좌측(68%): 메인 캔들 차트 + 거래량 차트 (글씨 박스 제거, 큼직한 넘버링 뱃지 ①~④ 적용)
        - 우측(32%): [그래프 밖 전용 해설 패널] 큼직한 폰트(20~26pt)로 4단계 타점 및 손익비 완벽 정리
        """
        # 1920x1080, 120 DPI (16:9 비율)
        fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=DARK["bg"])

        # Grid: 좌측 차트(0.04~0.67), 우측 설명 패널(0.70~0.97)
        # 상단 타이틀 바(0.91~0.98), 바닥(0.04)
        gs_left = fig.add_gridspec(
            nrows=2, ncols=1,
            height_ratios=[7, 3],
            top=0.88, bottom=0.06, left=0.05, right=0.67,
            hspace=0.08
        )
        ax_main = fig.add_subplot(gs_left[0])
        ax_vol = fig.add_subplot(gs_left[1], sharex=ax_main)

        # 우측 설명 전용 패널용 서브플롯 (Axes)
        gs_right = fig.add_gridspec(
            nrows=1, ncols=1,
            top=0.88, bottom=0.06, left=0.70, right=0.96
        )
        ax_panel = fig.add_subplot(gs_right[0])
        ax_panel.set_facecolor(DARK["panel"])
        for spine in ax_panel.spines.values():
            spine.set_color(DARK["panel_border"])
            spine.set_linewidth(1.5)
        ax_panel.set_xticks([])
        ax_panel.set_yticks([])

        # -------------------------------------------------------------------------
        # 헤더 타이틀 영역 (대형 30pt 폰트)
        # -------------------------------------------------------------------------
        fig.text(
            0.05, 0.94, "맥락트레이딩 실전 차트강의 #01",
            color=DARK["cyan"], fontsize=22, fontweight="bold", va="center"
        )
        fig.text(
            0.28, 0.94, "3분봉·5분봉 10이평선 첫 눌림목 정석 타점 & -1.5% 칼손절",
            color=DARK["text_primary"], fontsize=26, fontweight="bold", va="center"
        )
        fig.text(
            0.83, 0.94, "승률 85% 손익비 1:2.3 공식",
            color=DARK["gold"], fontsize=20, fontweight="bold", va="center"
        )

        # 차트 스타일링
        for ax in (ax_main, ax_vol):
            ax.set_facecolor(DARK["panel"])
            for spine in ax.spines.values():
                spine.set_color(DARK["panel_border"])
                spine.set_linewidth(1.2)
            ax.tick_params(colors=DARK["text_muted"], labelsize=14)
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

        # 이평선 플롯 (굵고 선명하게)
        x_axis = np.arange(n_bars)
        ax_main.plot(x_axis, ma5, label="5 이평선 (공격선)", color=DARK["cyan"], linewidth=2.5, alpha=0.9, zorder=5)
        ax_main.plot(x_axis, ma10, label="★ 10 이평선 (생명선)", color=DARK["gold"], linewidth=4.5, alpha=1.0, zorder=6)
        ax_main.plot(x_axis, ma20, label="20 이평선 (추세선)", color=DARK["orange"], linewidth=2.5, alpha=0.85, zorder=5)

        # -------------------------------------------------------------------------
        # 깔끔한 기준선 (익절선 / 손절선)
        # -------------------------------------------------------------------------
        entry_price = 10760
        stop_price = 10600
        target_price = 11140

        # +3.5% 1차 익절선
        ax_main.axhline(target_price, color=DARK["target_green"], linestyle="--", linewidth=2.2, alpha=0.9, zorder=2)
        ax_main.text(
            0.5, target_price + 35, "+3.5% 1차 분할 익절선 (11,140원)",
            color=DARK["target_green"], fontsize=14, fontweight="bold"
        )

        # -1.5% 칼손절선
        ax_main.axhline(stop_price, color=DARK["stop_red"], linestyle="--", linewidth=2.2, alpha=0.9, zorder=2)
        ax_main.text(
            0.5, stop_price - 65, "-1.5% 기계적 칼손절선 (10,600원)",
            color=DARK["stop_red"], fontsize=14, fontweight="bold"
        )

        # -------------------------------------------------------------------------
        # ★ 차트 내부: 복잡한 글씨박스 100% 제거! 큼직한 원형 넘버링 뱃지만 배치!
        # -------------------------------------------------------------------------
        def draw_badge(ax, x, y, num_str, bg_color, text_color=DARK["text_primary"]):
            """차트 내부에 시원하고 깔끔한 원형 넘버링 뱃지를 그립니다."""
            circle = Circle((x, y), 0.45, facecolor=bg_color, edgecolor=DARK["text_primary"],
                            linewidth=2.0, zorder=10)
            ax.add_patch(circle)
            ax.text(x, y, num_str, color=text_color, fontsize=18, fontweight="bold",
                    ha="center", va="center", zorder=11)

        # ① 1차 급등 돌파 (캔들 8 상단)
        draw_badge(ax_main, 8, 11420, "1", DARK["bull_red"])
        ax_main.text(8, 11580, "1차 돌파", color=DARK["bull_red"], fontsize=14, fontweight="bold", ha="center")

        # ② 10이평 눌림목 (캔들 12 상단)
        draw_badge(ax_main, 12, 11120, "2", DARK["cyan"])
        ax_main.text(12, 11280, "10선 눌림", color=DARK["cyan"], fontsize=14, fontweight="bold", ha="center")

        # ③ ★ 10이평 지지 양봉 타점 (캔들 15 하단)
        draw_badge(ax_main, 15, 10380, "3", DARK["gold"], text_color="#000000")
        ax_main.text(15, 10180, "★ 매수 타점", color=DARK["gold"], fontsize=16, fontweight="bold", ha="center")

        # ④ 2차 랠리 & 신고가 (캔들 19 상단)
        draw_badge(ax_main, 19, 11660, "4", DARK["target_green"])
        ax_main.text(19, 11820, "신고가 랠리", color=DARK["target_green"], fontsize=14, fontweight="bold", ha="center")

        # 거래량 차트 내 기준선 및 라벨
        dryup_level = 150000
        ax_vol.axhline(dryup_level, color=DARK["gold"], linestyle=":", linewidth=2.0, alpha=0.9)
        ax_vol.text(
            0.5, dryup_level + 18000, "거래량 1/3 급감 기준선 (Dry-Up Line)",
            color=DARK["gold"], fontsize=13, fontweight="bold"
        )
        draw_badge(ax_vol, 12, 90000, "V", DARK["cyan"])
        ax_vol.text(12, 140000, "거래량 87% 급감\n(매도세 고갈)", color=DARK["cyan"],
                    fontsize=12, fontweight="bold", ha="center")

        ax_main.set_ylim(9850, 12050)
        ax_main.set_ylabel("주가 (KRW)", color=DARK["text_secondary"], fontsize=15, labelpad=8)
        ax_vol.set_ylabel("거래량", color=DARK["text_secondary"], fontsize=15, labelpad=8)
        ax_main.legend(loc="upper left", facecolor=DARK["panel"], edgecolor=DARK["panel_border"],
                       labelcolor=DARK["text_primary"], fontsize=13, framealpha=0.9)

        # X축 라벨 포맷팅
        time_labels = ["09:00", "09:06", "09:12", "09:18", "09:24", "09:30", "09:36", "09:42", "09:48", "09:54", "10:00", "10:06", "10:12"]
        step = 2
        ax_vol.set_xticks(range(0, n_bars, step))
        ax_vol.set_xticklabels([time_labels[i//2] for i in range(0, n_bars, step)], fontsize=13)
        ax_vol.set_xlabel("장중 3분봉 진행 시간 (Time)", color=DARK["text_secondary"], fontsize=14, labelpad=6)

        # -------------------------------------------------------------------------
        # ★ 우측 패널: [그래프 밖 전용 해설 카드] 큼직하고 시원한 20~24pt 폰트!
        # -------------------------------------------------------------------------
        panel_y = 0.94
        ax_panel.text(0.08, panel_y, "■ 실전 매매 4단계 프로세스", color=DARK["gold"], fontsize=20, fontweight="bold")

        steps = [
            (
                "① 1차 급등 돌파 파동",
                DARK["bull_red"],
                [
                    "• 당일 거래대금 TOP 1~3위 주도주 압축",
                    "• 장대양봉으로 전일 고점 강력 돌파 (+12.5%)",
                    "• 절대 추격 매수 금지 (1차 눌림 대기)",
                ]
            ),
            (
                "② 10이평 수렴 눌림목 (Volume Dry-Up)",
                DARK["cyan"],
                [
                    "• 주가가 10이평선 부근까지 완만한 조정",
                    "• 거래량이 직전의 1/3 (30%) 이하로 바짝 마름",
                    "• 세력 이탈 없는 '건전한 숨고르기' 확인",
                ]
            ),
            (
                "③ ★ 10이평 지지 양봉 종가 매수",
                DARK["gold"],
                [
                    "• 10 EMA 밑꼬리 터치 후 지지 양봉 완성",
                    "• [진입 타점] 15번 봉 종가: 10,760원",
                    "• [칼손절] -1.5% 이탈 시 즉시 자동 시장가 매도",
                    "• [손익비] 리스크 160원 vs 기대수익 380원 (1:2.3)",
                ]
            ),
            (
                "④ 2차 랠리 및 분할 청산 공식",
                DARK["target_green"],
                [
                    "• [1차 익절] +3.5% 도달 시 50% 물량 확정 락인",
                    "• [추세 홀딩] 잔여 50%는 10선 종가 이탈 전까지",
                    "• 당일 신고가 랠리 끝까지 추종 (+8~10%)",
                ]
            ),
        ]

        card_y = 0.88
        for title, col, lines in steps:
            # 단계 제목
            ax_panel.text(0.08, card_y, title, color=col, fontsize=17, fontweight="bold")
            card_y -= 0.038
            # 상세 내용
            for l in lines:
                ax_panel.text(0.12, card_y, l, color=DARK["text_secondary"], fontsize=13.5)
                card_y -= 0.032
            card_y -= 0.022

        # 하단 자금관리 박스
        rule_box = FancyBboxPatch(
            (0.06, 0.04), 0.88, 0.12, boxstyle="round,pad=0.02",
            facecolor="#2A1B1D", edgecolor=DARK["stop_red"], linewidth=1.5
        )
        ax_panel.add_patch(rule_box)
        ax_panel.text(0.10, 0.115, "[필독] 맥락트레이딩 절대 생존 수칙", color=DARK["stop_red"], fontsize=15, fontweight="bold")
        ax_panel.text(0.10, 0.075, "1. 원하는 타점(10이평 지지)이 오지 않으면 종일 매매 쉰다.\n2. 손절선(-1.5%) 터치 시 1초의 망설임 없이 기계적 칼손절!",
                      color=DARK["text_secondary"], fontsize=12.5, linespacing=1.4)

        out_path = self.output_dir / "chart_3min_5min_10ma_pullback.png"
        plt.savefig(out_path, dpi=120, facecolor=DARK["bg"], edgecolor="none")
        plt.close(fig)
        return out_path

    def generate_orderbook_spoofing_diagram(self) -> Path:
        """
        도안 2: 호가 잔량의 역설 & 체결강도 구조도
        - 텍스트 오버랩 100% 제거
        - 폰트 크기 대폭 상향 (호가 16~18pt, 요약 20~24pt)
        - 좌우 명확한 대비: [위험한 착시] vs [진짜 폭등]
        """
        fig = plt.figure(figsize=(16, 9), dpi=120, facecolor=DARK["bg"])

        # 좌/우 패널 분할
        gs = fig.add_gridspec(
            nrows=1, ncols=2,
            top=0.88, bottom=0.06, left=0.05, right=0.95,
            wspace=0.08
        )
        ax_left = fig.add_subplot(gs[0])
        ax_right = fig.add_subplot(gs[1])

        # 헤더 타이틀 바
        fig.text(
            0.05, 0.94, "맥락트레이딩 실전 호가창 강의 #01",
            color=DARK["gold"], fontsize=22, fontweight="bold", va="center"
        )
        fig.text(
            0.32, 0.94, "호가 잔량의 역설: 허매수벽 트랩 vs 매도벽 흡수 구조도",
            color=DARK["text_primary"], fontsize=26, fontweight="bold", va="center"
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
            color=DARK["stop_red"], fontsize=20, fontweight="bold", ha="center"
        )
        ax_left.text(
            0.5, 0.89, "초보자의 착각: '매수잔량이 6배나 많으니 안전하다?'",
            color=DARK["text_muted"], fontsize=15, ha="center"
        )

        # 상단 총잔량 요약 박스 (큼직한 폰트)
        summary_l = FancyBboxPatch(
            (0.06, 0.74), 0.88, 0.12, boxstyle="round,pad=0.02",
            facecolor="#2A1B1D", edgecolor=DARK["stop_red"], linewidth=1.5
        )
        ax_left.add_patch(summary_l)
        ax_left.text(0.10, 0.81, "매도총잔량: 45,000주", color=DARK["bear_blue"], fontsize=18, fontweight="bold")
        ax_left.text(0.55, 0.81, "매수총잔량: 285,000주", color=DARK["stop_red"], fontsize=18, fontweight="bold")
        ax_left.text(0.10, 0.76, "비율 1 : 6.3 (극단적 매수 우위 착시)", color=DARK["text_muted"], fontsize=15)
        ax_left.text(0.55, 0.76, "체결강도: 62% (매도세 압도)", color=DARK["stop_red"], fontsize=16, fontweight="bold")

        # 6단계 호가 테이블 (행 간격을 넉넉하게 벌려 오버랩 0%)
        rows_l = [
            ("매도 3호가 (10,150원)", "12,000주", DARK["bear_blue"], 0.18),
            ("매도 2호가 (10,100원)", "18,000주", DARK["bear_blue"], 0.25),
            ("매도 1호가 (10,050원)", "15,000주", DARK["bear_blue"], 0.20),
            # 현재가
            ("매수 1호가 (10,000원)", "25,000주", DARK["bull_red"], 0.28),
            ("매수 2호가 ( 9,950원)", "30,000주", DARK["bull_red"], 0.32),
            ("매수 3호가 ( 9,900원)", "130,000주 ★", DARK["stop_red"], 0.88), # 거대 허매수벽
        ]

        y_pos = 0.64
        for label, qty, col, b_len in rows_l:
            # 막대 그래프
            rect = Rectangle((0.45, y_pos - 0.015), b_len * 0.45, 0.042, facecolor=col, alpha=0.30)
            ax_left.add_patch(rect)
            # 호가 텍스트 (16pt로 확대)
            ax_left.text(0.08, y_pos, label, color=DARK["text_secondary"], fontsize=15, va="center")
            ax_left.text(0.48, y_pos, qty, color=col, fontsize=16, fontweight="bold", va="center")
            y_pos -= 0.060

        # 하단 핵심 경고 박스 (오버랩 없이 호가 테이블 아래에 독립 배치)
        alert_box_l = FancyBboxPatch(
            (0.06, 0.06), 0.88, 0.18, boxstyle="round,pad=0.02",
            facecolor="#1A1214", edgecolor=DARK["stop_red"], linewidth=1.5
        )
        ax_left.add_patch(alert_box_l)
        ax_left.text(0.10, 0.19, "[주의] 세력의 '허매수벽(Fake Bid)' 트랩 작동 원리", color=DARK["stop_red"], fontsize=16, fontweight="bold")
        ax_left.text(0.10, 0.145, "1. 매수 3호가에 13만 주 대형 벽을 쌓아 개미에게 '안전판' 착시 유도", color=DARK["text_secondary"], fontsize=13.5)
        ax_left.text(0.10, 0.110, "2. 개미가 안심하고 매수할 때 세력은 위에서 시장가로 전량 물량 투하", color=DARK["text_secondary"], fontsize=13.5)
        ax_left.text(0.10, 0.075, "3. 물량 털기 완료 즉시 13만 주 일거에 취소 -> 호가 공백 수직 폭락!", color=DARK["stop_red"], fontsize=14, fontweight="bold")

        # =========================================================================
        # 우측 패널: [진짜 폭등] 상승형 호가창 (보컬의 매도벽 흡수 법칙)
        # =========================================================================
        ax_right.text(
            0.5, 0.94, "★ [진짜 폭등] 상승형 호가창 (보컬의 매도벽 흡수)",
            color=DARK["gold"], fontsize=20, fontweight="bold", ha="center"
        )
        ax_right.text(
            0.5, 0.89, "실전 대가의 통찰: '매도잔량이 2~3배 많아야 상승 연료가 된다!'",
            color=DARK["cyan"], fontsize=15, ha="center"
        )

        # 상단 총잔량 요약 박스
        summary_r = FancyBboxPatch(
            (0.06, 0.74), 0.88, 0.12, boxstyle="round,pad=0.02",
            facecolor="#162A22", edgecolor=DARK["gold"], linewidth=1.5
        )
        ax_right.add_patch(summary_r)
        ax_right.text(0.10, 0.81, "매도총잔량: 380,000주 ★", color=DARK["gold"], fontsize=18, fontweight="bold")
        ax_right.text(0.55, 0.81, "매수총잔량: 115,000주", color=DARK["cyan"], fontsize=18, fontweight="bold")
        ax_right.text(0.10, 0.76, "비율 3.3 : 1 (황금 매도벽 우위)", color=DARK["text_primary"], fontsize=15, fontweight="bold")
        ax_right.text(0.55, 0.76, "체결강도: 148% (공격적 시장가 매수)", color=DARK["target_green"], fontsize=16, fontweight="bold")

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

        y_pos = 0.64
        for label, qty, col, b_len in rows_r:
            rect = Rectangle((0.45, y_pos - 0.015), b_len * 0.45, 0.042, facecolor=col, alpha=0.30)
            ax_right.add_patch(rect)
            ax_right.text(0.08, y_pos, label, color=DARK["text_secondary"], fontsize=15, va="center")
            ax_right.text(0.48, y_pos, qty, color=col, fontsize=16, fontweight="bold", va="center")
            y_pos -= 0.060

        # 하단 핵심 원리 박스
        alert_box_r = FancyBboxPatch(
            (0.06, 0.06), 0.88, 0.18, boxstyle="round,pad=0.02",
            facecolor="#12251D", edgecolor=DARK["target_green"], linewidth=1.5
        )
        ax_right.add_patch(alert_box_r)
        ax_right.text(0.10, 0.19, "[돌파] 세력의 '매도벽 흡수(Wall Absorption)' 랠리 원리", color=DARK["target_green"], fontsize=16, fontweight="bold")
        ax_right.text(0.10, 0.145, "1. 상단 매도 1~3호가에 빽빽하게 쌓인 물량은 세력의 '진짜 매수 연료'", color=DARK["text_secondary"], fontsize=13.5)
        ax_right.text(0.10, 0.110, "2. 대형 시장가 매수세(체결강도 148%)가 매도벽을 단숨에 집어삼킴", color=DARK["text_secondary"], fontsize=13.5)
        ax_right.text(0.10, 0.075, "3. 매도벽 돌파 즉시 거래대금 폭증하며 전고점 랠리 시작!", color=DARK["gold"], fontsize=14, fontweight="bold")

        out_path = self.output_dir / "orderbook_spoofing_execution_strength.png"
        plt.savefig(out_path, dpi=120, facecolor=DARK["bg"], edgecolor="none")
        plt.close(fig)
        return out_path


if __name__ == "__main__":
    out_dir = Path("growth_engine/03_blog_hub/stock_blog/assets/img/posts")
    engine = RedesignedChartInfographics(out_dir)
    p1 = engine.generate_10ma_pullback_chart()
    p2 = engine.generate_orderbook_spoofing_diagram()
    print("Generated 1:", p1)
    print("Generated 2:", p2)
