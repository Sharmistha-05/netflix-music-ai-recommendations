"""Every chart and diagram used in the report (matplotlib, PNG at 200 dpi).

Visual language matches the earlier Netflix Music deck: Netflix red for the
point being made, greys for context, no chart junk, direct labels.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

RED, INK, MUTED, GREY, LIGHT, GRID = "#E50914", "#1A1A1A", "#5F5F5F", "#B3B3B3", "#E6E6E6", "#DDDDDD"
AMBER, GREEN, BLUE = "#F2A900", "#3A9D5D", "#2F5D8A"

_family = "Arial" if any("Arial" in f.name for f in font_manager.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams.update({
    "font.family": _family, "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titleweight": "bold", "axes.titlesize": 13,
    "axes.titlecolor": INK, "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white",
})


def _clean(ax, grid="x"):
    ax.spines[["top", "right"]].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def _save(fig, out, name):
    p = Path(out) / f"{name}.png"
    fig.savefig(p)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- Sheet 1 charts
def ai_score_by_song(scored, out):
    s = scored.sort_values("ai_recommendation_score")
    fig, ax = plt.subplots(figsize=(8, 4.6))
    colors = [RED if r <= 3 else GREY for r in s["rank"]]
    ax.barh(s.song_id + "  " + s.genre, s.ai_recommendation_score, color=colors, height=0.62)
    for y, (v, seg) in enumerate(zip(s.ai_recommendation_score, s.segment)):
        ax.text(v + 0.012, y, f"{v:.2f}  ({seg})", va="center", fontsize=10, color=INK)
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("AI Recommendation Score (0 to 1)")
    _clean(ax)
    return _save(fig, out, "ai_score_by_song")


def skip_vs_rating(scored, corr, out):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    hi = scored.skip_rate >= 0.20
    ax.scatter(scored.skip_rate[~hi], scored.user_rating[~hi], s=scored.play_count[~hi] * 12,
               color=GREY, alpha=0.9, edgecolor="white")
    ax.scatter(scored.skip_rate[hi], scored.user_rating[hi], s=scored.play_count[hi] * 12,
               color=RED, alpha=0.9, edgecolor="white")
    for _, r in scored.iterrows():
        ax.annotate(r.genre, (r.skip_rate, r.user_rating), xytext=(8, 5), textcoords="offset points",
                    fontsize=9.5, color=INK)
    ax.axvline(0.20, color=RED, lw=0.8, ls="--")
    ax.text(0.202, 4.97, "skip-risk threshold 0.20", color=RED, fontsize=9, va="top")
    ax.set_xlabel("Skip rate")
    ax.set_ylabel("User rating (1 to 5)")
    ax.set_xlim(0.02, 0.28)
    ax.set_ylim(3.9, 5.05)
    _clean(ax, "both")
    ax.text(0.03, 3.95, f"r = {corr.loc['skip_rate', 'user_rating']}   bubble size = play count",
            fontsize=9.5, color=MUTED)
    return _save(fig, out, "skip_vs_rating")


def correlation_heatmap(corr, out):
    labels = ["Play count", "Skip rate", "User rating", "Listening min"]
    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("nr", ["#4A4A4A", "#FFFFFF", RED])
    ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
    ax.set_xticks(range(4), labels, rotation=30, ha="right")
    ax.set_yticks(range(4), labels)
    for i in range(4):
        for j in range(4):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=11,
                    color="white" if abs(v) > 0.55 else INK, weight="bold" if i != j else "normal")
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    return _save(fig, out, "correlation_heatmap")


def minutes_per_play(scored, out):
    s = scored.sort_values("minutes_per_play")
    fig, ax = plt.subplots(figsize=(8, 4.6))
    top = s.minutes_per_play >= s.minutes_per_play.quantile(0.7)
    ax.barh(s.genre, s.minutes_per_play, color=[RED if t else GREY for t in top], height=0.62)
    for y, v in enumerate(s.minutes_per_play):
        ax.text(v + 0.06, y, f"{v:.2f}", va="center", fontsize=10)
    ax.set_xlabel("Listening minutes per play")
    ax.set_xlim(0, 8.6)
    _clean(ax)
    return _save(fig, out, "minutes_per_play")


# --------------------------------------------------------------------------- ER diagram
ENTITIES = {
    # name: (column, row, group, attributes)
    "SUBSCRIPTION_PLANS": (0, 0, "user", ["PK plan_id", "plan_name", "monthly_price_usd", "ad_supported"]),
    "USERS": (0, 1, "user", ["PK user_id", "name", "FK plan_id", "country", "signup_date",
                             "personalization_consent"]),
    "WATCH_HISTORY": (0, 2, "user", ["PK watch_id", "FK user_id", "FK title_id", "watched_at", "minutes_watched"]),
    "RECOMMENDATION_LOGS": (1, 0, "ai", ["PK rec_id", "FK user_id", "FK song_id", "FK model_version",
                                         "ai_recommendation_score", "rank_position", "user_action"]),
    "LISTENING_BEHAVIOR": (1, 1, "user", ["PK,FK user_id", "PK,FK song_id", "play_count", "skip_rate",
                                          "user_rating", "listening_minutes"]),
    "NETFLIX_TITLES": (1, 2, "song", ["PK title_id", "title_name", "title_type", "primary_genre"]),
    "AI_MODELS": (2, 0, "ai", ["PK model_version", "algorithm", "FK training_dataset_id", "deployed_at", "status"]),
    "SONGS": (2, 1, "song", ["PK song_id", "song_title", "genre", "FK artist_id", "FK source_title_id",
                             "is_netflix_exclusive"]),
    "ARTISTS": (2, 2, "song", ["PK artist_id", "artist_name"]),
    "TRAINING_DATASETS": (3, 0, "ai", ["PK dataset_id", "dataset_name", "source_tables", "row_count"]),
    "PLAYLISTS": (3, 1, "song", ["PK playlist_id", "playlist_name", "FK owner_user_id", "playlist_type",
                                 "FK generated_by_model"]),
    "PLAYLIST_SONGS": (3, 2, "song", ["PK,FK playlist_id", "PK,FK song_id", "position"]),
}
RELATIONS = [
    # from, side, frac, to, side, frac, card_from, card_to, verb
    ("SUBSCRIPTION_PLANS", "b", 0.5, "USERS", "t", 0.5, "1", "N", "subscribes"),
    ("USERS", "b", 0.5, "WATCH_HISTORY", "t", 0.5, "1", "N", "watches"),
    ("WATCH_HISTORY", "r", 0.5, "NETFLIX_TITLES", "l", 0.5, "N", "1", "of title"),
    ("USERS", "r", 0.5, "LISTENING_BEHAVIOR", "l", 0.5, "1", "N", "listens"),
    ("LISTENING_BEHAVIOR", "r", 0.5, "SONGS", "l", 0.5, "N", "1", "for song"),
    ("USERS", "t", 0.8, "RECOMMENDATION_LOGS", "l", 0.5, "1", "N", "receives"),
    ("RECOMMENDATION_LOGS", "r", 0.6, "AI_MODELS", "l", 0.6, "N", "1", "produced by"),
    ("RECOMMENDATION_LOGS", "b", 0.85, "SONGS", "t", 0.2, "N", "1", "recommends"),
    ("AI_MODELS", "r", 0.6, "TRAINING_DATASETS", "l", 0.6, "N", "1", "trained on"),
    ("AI_MODELS", "b", 0.85, "PLAYLISTS", "t", 0.15, "1", "N", "generates"),
    ("NETFLIX_TITLES", "r", 0.5, "SONGS", "b", 0.2, "1", "N", "soundtrack of"),
    ("SONGS", "b", 0.65, "ARTISTS", "t", 0.65, "N", "1", "performed by"),
    ("SONGS", "r", 0.3, "PLAYLIST_SONGS", "l", 0.6, "1", "N", "listed in"),
    ("PLAYLISTS", "b", 0.5, "PLAYLIST_SONGS", "t", 0.5, "1", "N", "contains"),
]


def er_diagram(out):
    fills = {"user": "#FDE8E9", "song": "#EEF2F7", "ai": "#EEF6EE"}
    W, HEAD, LINE, GAPX = 3.9, 0.52, 0.37, 2.0
    tops = [12.0, 7.75, 3.55]
    fig, ax = plt.subplots(figsize=(19.5, 11.4))
    ax.set_xlim(-0.1, 4 * W + 3 * GAPX + 0.1)
    ax.set_ylim(0.85, 13.45)
    ax.axis("off")
    boxes = {}
    for name, (c, r, g, attrs) in ENTITIES.items():
        x = c * (W + GAPX)
        h = HEAD + LINE * len(attrs) + 0.14
        y = tops[r] - h
        ax.add_patch(FancyBboxPatch((x, y), W, h, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc=fills[g], ec="#7A7A7A", lw=1.1, zorder=3))
        ax.add_patch(FancyBboxPatch((x, y + h - HEAD), W, HEAD, boxstyle="round,pad=0,rounding_size=0.08",
                                    fc="#262626", ec="#262626", zorder=4))
        ax.text(x + W / 2, y + h - HEAD / 2, name, ha="center", va="center", color="white",
                fontsize=11.5, weight="bold", zorder=5)
        for i, a in enumerate(attrs):
            key = a.split(" ")[0] if a.startswith(("PK", "FK")) else ""
            label = a[len(key):].strip() if key else a
            yy = y + h - HEAD - LINE * (i + 0.62)
            if key:
                ax.text(x + 0.14, yy, key, fontsize=8, va="center", weight="bold", zorder=5,
                        color=RED if "PK" in key else BLUE)
            ax.text(x + 1.0, yy, label, fontsize=10, va="center", color=INK, zorder=5,
                    weight="bold" if "PK" in key else "normal")
        boxes[name] = (x, y, W, h)

    def anchor(n, side, f):
        x, y, w, h = boxes[n]
        return {"l": (x, y + h * (1 - f)), "r": (x + w, y + h * (1 - f)),
                "t": (x + w * f, y + h), "b": (x + w * f, y)}[side]

    for a, sa, fa, b, sb, fb, ca, cb, verb in RELATIONS:
        (x1, y1), (x2, y2) = anchor(a, sa, fa), anchor(b, sb, fb)
        ax.plot([x1, x2], [y1, y2], color="#555555", lw=1.3, zorder=2)
        for (px, py), (qx, qy), card, owner in (((x1, y1), (x2, y2), ca, a), ((x2, y2), (x1, y1), cb, b)):
            dx, dy = qx - px, qy - py
            L = (dx ** 2 + dy ** 2) ** 0.5 or 1
            ux, uy = dx / L, dy / L
            bx, by, bw, bh = boxes[owner]
            cx, cy = bx + bw / 2, by + bh / 2
            best = None
            for along in (0.32, 0.5, 0.7):        # step away from the box until the label is outside it
                for sgn in (1, -1):               # try both sides of the line
                    lx, ly = px + ux * along + sgn * -uy * 0.24, py + uy * along + sgn * ux * 0.24
                    inside = bx - 0.1 < lx < bx + bw + 0.1 and by - 0.1 < ly < by + bh + 0.1
                    if not inside:
                        best = (lx, ly)
                        break
                if best:
                    break
            lx, ly = best or (px + ux * 0.5, py + uy * 0.5)
            ax.text(lx, ly, card, fontsize=12, color=RED, weight="bold", ha="center", va="center", zorder=6)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, verb, fontsize=9, color=MUTED, style="italic", ha="center",
                va="center", zorder=6, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))

    legend = [("#FDE8E9", "Users and behaviour (Sheet 1 maps to LISTENING_BEHAVIOR)"),
              ("#EEF2F7", "Songs, playlists and catalog"), ("#EEF6EE", "AI model data")]
    lx = 0
    for fc, txt in legend:
        ax.add_patch(FancyBboxPatch((lx, 13.05), 0.35, 0.3, boxstyle="round,pad=0,rounding_size=0.04",
                                    fc=fc, ec="#7A7A7A"))
        ax.text(lx + 0.5, 13.2, txt, fontsize=10.5, va="center", color=INK)
        lx += 0.9 + len(txt) * 0.112
    ax.text(lx + 0.2, 13.2, "PK primary key   FK foreign key   1 / N cardinality", fontsize=10.5,
            va="center", color=MUTED)
    return _save(fig, out, "er_diagram")


# --------------------------------------------------------------------------- Agile charts
def status_priority(summary, out):
    sp = summary["status_priority"]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    left = [0] * len(sp)
    for col, color in (("High", RED), ("Medium", AMBER), ("Low", GREEN)):
        ax.barh(sp.index, sp[col], left=left, color=color, height=0.55, label=col)
        for i, (l, v) in enumerate(zip(left, sp[col])):
            if v:
                ax.text(l + v / 2, i, str(v), ha="center", va="center", color="white", weight="bold")
        left = [l + v for l, v in zip(left, sp[col])]
    ax.invert_yaxis()
    ax.set_xlabel("Number of tasks (Sheet 2)")
    ax.legend(frameon=False, ncol=3, loc="lower right", bbox_to_anchor=(1, 1.0))
    _clean(ax)
    return _save(fig, out, "sprint_status_priority")


def wsjf_chart(w, names, out):
    s = w.sort_values("backlog_rank", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4.4))
    lab = [f"#{r}  {c}  {names[c]}" for r, c in zip(s.backlog_rank, s.card)]
    ax.barh(lab, s.wsjf, color=[RED if r <= 2 else GREY for r in s.backlog_rank], height=0.6)
    for y, v in enumerate(s.wsjf):
        ax.text(v + 0.08, y, f"{v:.2f}", va="center", fontsize=10)
    ax.set_xlabel("WSJF = (Business value + Time criticality + Risk reduction) / Job size")
    ax.set_xlim(0, 9.2)
    ax.text(9.1, 0.2, "N02 ranks above N03 because\nsegmentation needs the prepared dataset",
            ha="right", va="bottom", fontsize=9, color=MUTED)
    _clean(ax)
    return _save(fig, out, "wsjf_backlog")


def kanban_board(board, wsjf, out):
    rank = dict(zip(wsjf.card, wsjf.backlog_rank))
    pc = {"High": RED, "Medium": AMBER, "Low": GREEN}
    lists = ["Backlog", "In Progress", "Completed"]
    fig, ax = plt.subplots(figsize=(15, 9))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 9.4)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 15, 9.4, boxstyle="square,pad=0", fc="#0B4F6C", ec="none"))
    ax.text(0.3, 9.0, "Netflix Music  |  AI Recommendations  |  Sprint 4", color="white", fontsize=18, weight="bold")
    ax.text(0.3, 8.62, "Labels: priority from Sheet 2   |   Backlog ordered by WSJF   |   "
                       "WIP limit In Progress = 5 (6 now: flagged)   |   N = card from problem statement",
            color="#D8E6EE", fontsize=11)
    for ci, lst in enumerate(lists):
        cards = board[board.status == lst].copy()
        if lst == "Backlog":
            cards["r"] = cards.task_id.map(rank)
            cards = cards.sort_values("r")
        else:
            cards["r"] = cards.priority.map({"High": 0, "Medium": 1, "Low": 2})
            cards = cards.sort_values(["r", "task_id"])
        x = 0.3 + ci * 4.85
        ax.add_patch(FancyBboxPatch((x, 0.2), 4.6, 8.2, boxstyle="round,pad=0,rounding_size=0.1",
                                    fc="#EBECF0", ec="none"))
        over = "  over WIP limit" if lst == "In Progress" and len(cards) > 5 else ""
        ax.text(x + 0.2, 8.0, f"{lst} ({len(cards)})", fontsize=15, weight="bold", color="#172B4D")
        if over:
            ax.text(x + 4.4, 8.0, over.strip(), fontsize=9.5, color=RED, weight="bold", ha="right")
        for k, (_, c) in enumerate(cards.iterrows()):
            y = 7.0 - k * 0.98
            ax.add_patch(FancyBboxPatch((x + 0.15, y), 4.3, 0.84, boxstyle="round,pad=0,rounding_size=0.06",
                                        fc="white", ec="#C1C7D0", lw=0.6))
            ax.add_patch(FancyBboxPatch((x + 0.3, y + 0.58), 0.78, 0.17, boxstyle="round,pad=0,rounding_size=0.05",
                                        fc=pc[c.priority], ec="none"))
            ax.text(x + 0.69, y + 0.665, c.priority, fontsize=7.5, color="white", ha="center", va="center",
                    weight="bold")
            meta = c.task_id + (f"   WSJF rank #{int(c.r)}" if lst == "Backlog" else "")
            ax.text(x + 1.2, y + 0.665, meta, fontsize=9.5, color="#5E6C84", va="center")
            ax.text(x + 0.3, y + 0.37, c.task_name, fontsize=11.5, color="#172B4D", va="center")
            ax.text(x + 0.3, y + 0.13, c.owner, fontsize=10, color="#5E6C84", va="center")
    return _save(fig, out, "trello_kanban_board")


# --------------------------------------------------------------------------- GenAI charts
def genai_comparison(models, out):
    m = models.set_index("model")
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.2))
    blend = lambda r: (3 * r.input_usd + r.output_usd) / 4
    names = ["GPT-6.1 Terra", "Gemini 3.8 Flash", "Gemini 3.8 Flash (from 1 Jan 2027)"]
    labels = ["GPT-6.1\nTerra", "Gemini 3.8 Flash\n(to 31 Dec 2026)", "Gemini 3.8 Flash\n(from 1 Jan 2027)"]
    vals = [blend(m.loc[n]) for n in names]
    axs[0].bar(labels, vals, color=[RED, GREY, "#6B6B6B"], width=0.62)
    for i, v in enumerate(vals):
        axs[0].text(i, v + 0.05, f"${v:.2f}", ha="center", fontsize=10.5)
    axs[0].set_title("Cost: blended $ per 1M tokens\n(3 input : 1 output)", loc="left", fontsize=11.5)
    tt = [m.loc["GPT-6.1 Terra"].ttft_s, m.loc["Gemini 3.8 Flash"].ttft_s]
    axs[1].bar(["GPT-6.1\nTerra", "Gemini 3.8\nFlash"], tt, color=[RED, GREY], width=0.55)
    for i, v in enumerate(tt):
        axs[1].text(i, v + 0.06, f"{v:.2f} s", ha="center", fontsize=10.5)
    axs[1].set_title("Latency: median time to\nfirst token (lower is better)", loc="left", fontsize=11.5)
    hl = [m.loc["GPT-6.1 Terra"].aa_hallucination, m.loc["Gemini 3.8 Flash"].aa_hallucination]
    axs[2].bar(["GPT-6.1\nTerra", "Gemini 3.8\nFlash"], hl, color=[RED, GREY], width=0.55)
    for i, v in enumerate(hl):
        axs[2].text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=10.5)
    axs[2].set_title("Accuracy: hallucination rate\nAA-Omniscience (lower is better)", loc="left", fontsize=11.5)
    for a in axs:
        _clean(a, "y")
        a.tick_params(axis="x", labelsize=9.5)
    plt.tight_layout()
    return _save(fig, out, "genai_comparison")


def decision_scores(d, totals, out):
    fig, ax = plt.subplots(figsize=(8, 4.4))
    y = range(len(d))
    ax.barh([i - 0.2 for i in y], d.openai, height=0.38, color=RED, label=f"OpenAI  (total {totals['openai']:.2f})")
    ax.barh([i + 0.2 for i in y], d.gemini, height=0.38, color=GREY, label=f"Gemini  (total {totals['gemini']:.2f})")
    for i, (o, g) in enumerate(zip(d.openai, d.gemini)):
        ax.text(o + 0.05, i - 0.2, f"{o:g}", va="center", fontsize=9.5)
        ax.text(g + 0.05, i + 0.2, f"{g:g}", va="center", fontsize=9.5, color=MUTED)
    ax.set_yticks(list(y), [f"{c}  ({int(w * 100)}%)" for c, w in zip(d.criterion, d.weight)])
    ax.invert_yaxis()
    ax.set_xlim(0, 5.4)
    ax.set_xlabel("Score (1 to 5)")
    ax.legend(frameon=False, loc="lower right", bbox_to_anchor=(1, 1.0), ncol=2)
    _clean(ax)
    return _save(fig, out, "genai_decision_scores")


def cost_chart(cm, usage, out):
    s = cm.sort_values("monthly_usd")
    fig, ax = plt.subplots(figsize=(8, 4.4))
    colors = [RED if "Recommended" in n else (GREY if v == "Google" else "#E88A8F") for n, v in zip(s.model, s.vendor)]
    ax.barh(s.model, s.monthly_usd / 1000, color=colors, height=0.6)
    for yy, (v, p) in enumerate(zip(s.monthly_usd, s.per_mau_usd)):
        ax.text(v / 1000 + 15, yy, rf"\${v / 1000:,.0f}K   (\${p:.3f} per MAU)", va="center", fontsize=10)
    ax.set_xlabel(f"Monthly GenAI API cost, $K  ({usage['mau'] / 1e6:.0f}M MAU, "
                  f"{usage['calls_per_user_month']} calls per user)")
    ax.set_xlim(0, s.monthly_usd.max() / 1000 * 1.45)
    _clean(ax)
    return _save(fig, out, "genai_cost_model")
