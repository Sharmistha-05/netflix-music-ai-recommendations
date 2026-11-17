"""Step 1: analysis tables, SQLite database and every figure.

    python build_visuals.py [path/to/CEP_Dataset.xlsx]

Writes output/tables/*.csv, output/database/netflix_music.{db,sql},
output/figures/*.png and output/trello_cards.csv.
"""
import sys
from pathlib import Path

import pandas as pd

from src import analysis as A
from src import charts as C
from src import database as D

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"


def run(data_path=A.DATA):
    tables, figs, dbdir = OUT / "tables", OUT / "figures", OUT / "database"
    for d in (tables, figs, dbdir):
        d.mkdir(parents=True, exist_ok=True)

    music = A.load_music(data_path)
    scored = A.score_music(music)
    corr = A.music_correlations(music)
    tasks = A.load_tasks(data_path)
    board = A.board(tasks)
    wsjf = A.wsjf_table()
    tsum = A.task_summary(tasks)
    dm, totals = A.decision_matrix()
    cm = A.cost_model()

    scored.to_csv(tables / "music_scored.csv", index=False)
    corr.to_csv(tables / "music_correlations.csv")
    wsjf.to_csv(tables / "backlog_wsjf.csv", index=False)
    board.to_csv(tables / "kanban_board.csv", index=False)
    dm.to_csv(tables / "genai_decision_matrix.csv", index=False)
    A.MODELS.to_csv(tables / "genai_models.csv", index=False)
    cm.to_csv(tables / "genai_cost_model.csv", index=False)
    pd.Series(totals).to_csv(tables / "genai_totals.csv", header=["score"])

    results, db_tables = D.build(scored, dbdir)

    names = dict(zip(board.task_id, board.task_name))
    short = {k: (v if len(v) <= 30 else v[:28] + "...") for k, v in names.items()}
    C.ai_score_by_song(scored, figs)
    C.skip_vs_rating(scored, corr, figs)
    C.correlation_heatmap(corr, figs)
    C.minutes_per_play(scored, figs)
    C.er_diagram(figs)
    C.status_priority(tsum, figs)
    C.wsjf_chart(wsjf, short, figs)
    C.kanban_board(board, wsjf, figs)
    C.genai_comparison(A.MODELS, figs)
    C.decision_scores(dm, totals, figs)
    C.cost_chart(cm, A.USAGE, figs)

    rank = dict(zip(wsjf.card, wsjf.backlog_rank))
    trello = board.assign(backlog_rank=board.task_id.map(rank))
    trello = trello.rename(columns={"status": "List", "task_name": "Card", "priority": "Label",
                                    "owner": "Member", "task_id": "ID", "source": "Source",
                                    "backlog_rank": "Backlog rank"})
    trello[["List", "ID", "Card", "Label", "Member", "Backlog rank", "Source"]].to_csv(OUT / "trello_cards.csv", index=False)

    return dict(music=music, scored=scored, corr=corr, tasks=tasks, board=board, wsjf=wsjf, tsum=tsum,
                dm=dm, totals=totals, cm=cm, results=results, db_tables=db_tables)


if __name__ == "__main__":
    ctx = run(Path(sys.argv[1]) if len(sys.argv) > 1 else A.DATA)
    print("Figures:", len(list((OUT / "figures").glob("*.png"))), "| DB tables:", len(ctx["db_tables"]))
    print("Decision totals:", ctx["totals"])
    print(ctx["wsjf"][["card", "wsjf", "backlog_rank"]].to_string(index=False))
    print(ctx["cm"].to_string(index=False))
