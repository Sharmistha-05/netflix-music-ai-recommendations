"""SQLite implementation of the Netflix Music ER diagram.

Builds the 12-table schema, loads Sheet 1 (Music Data) into LISTENING_BEHAVIOR,
adds clearly labelled placeholder rows for the entities Sheet 1 does not contain
(names, artists, titles), writes the baseline AI scores into RECOMMENDATION_LOGS
and runs the analysis queries used in the report.
"""
import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE subscription_plans (
  plan_id            INTEGER PRIMARY KEY,
  plan_name          TEXT UNIQUE NOT NULL,
  monthly_price_usd  REAL NOT NULL,
  ad_supported       INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE users (
  user_id                  INTEGER PRIMARY KEY,
  name                     TEXT NOT NULL,
  plan_id                  INTEGER NOT NULL REFERENCES subscription_plans(plan_id),
  country                  TEXT,
  signup_date              DATE,
  personalization_consent  INTEGER NOT NULL DEFAULT 0   -- opt-in to use watch history for music
);

CREATE TABLE netflix_titles (
  title_id       TEXT PRIMARY KEY,
  title_name     TEXT NOT NULL,
  title_type     TEXT CHECK (title_type IN ('Series','Film','Special')),
  primary_genre  TEXT
);

CREATE TABLE watch_history (
  watch_id         INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id          INTEGER NOT NULL REFERENCES users(user_id),
  title_id         TEXT NOT NULL REFERENCES netflix_titles(title_id),
  watched_at       TIMESTAMP,
  minutes_watched  INTEGER
);

CREATE TABLE artists (
  artist_id    TEXT PRIMARY KEY,
  artist_name  TEXT NOT NULL
);

CREATE TABLE songs (
  song_id               TEXT PRIMARY KEY,
  song_title            TEXT NOT NULL,
  genre                 TEXT NOT NULL,
  artist_id             TEXT NOT NULL REFERENCES artists(artist_id),
  source_title_id       TEXT REFERENCES netflix_titles(title_id),   -- soundtrack link
  duration_sec          INTEGER,
  is_netflix_exclusive  INTEGER NOT NULL DEFAULT 0
);

-- Sheet 1 (Music Data) lands here: one row per user and song.
CREATE TABLE listening_behavior (
  user_id            INTEGER NOT NULL REFERENCES users(user_id),
  song_id            TEXT NOT NULL REFERENCES songs(song_id),
  play_count         INTEGER NOT NULL CHECK (play_count >= 0),
  skip_rate          REAL CHECK (skip_rate BETWEEN 0 AND 1),
  user_rating        REAL CHECK (user_rating BETWEEN 1 AND 5),
  listening_minutes  INTEGER,
  PRIMARY KEY (user_id, song_id)
);

CREATE TABLE training_datasets (
  dataset_id     TEXT PRIMARY KEY,
  dataset_name   TEXT NOT NULL,
  source_tables  TEXT,
  row_count      INTEGER,
  snapshot_date  DATE
);

CREATE TABLE ai_models (
  model_version        TEXT PRIMARY KEY,
  algorithm            TEXT NOT NULL,
  training_dataset_id  TEXT NOT NULL REFERENCES training_datasets(dataset_id),
  deployed_at          DATE,
  status               TEXT CHECK (status IN ('Training','Testing','Deployed','Retired'))
);

CREATE TABLE playlists (
  playlist_id         TEXT PRIMARY KEY,
  playlist_name       TEXT NOT NULL,
  owner_user_id       INTEGER REFERENCES users(user_id),
  playlist_type       TEXT CHECK (playlist_type IN ('User','AI-Generated','Editorial','Watch-Inspired')),
  generated_by_model  TEXT REFERENCES ai_models(model_version),
  created_at          TIMESTAMP
);

CREATE TABLE playlist_songs (
  playlist_id  TEXT NOT NULL REFERENCES playlists(playlist_id),
  song_id      TEXT NOT NULL REFERENCES songs(song_id),
  position     INTEGER NOT NULL,
  PRIMARY KEY (playlist_id, song_id)
);

CREATE TABLE recommendation_logs (
  rec_id                   INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id                  INTEGER NOT NULL REFERENCES users(user_id),
  song_id                  TEXT NOT NULL REFERENCES songs(song_id),
  model_version            TEXT NOT NULL REFERENCES ai_models(model_version),
  ai_recommendation_score  REAL NOT NULL,
  rank_position            INTEGER,
  served_at                TIMESTAMP,
  user_action              TEXT CHECK (user_action IN ('Played','Skipped','Saved','Ignored'))
);

CREATE INDEX idx_listening_song ON listening_behavior(song_id);
CREATE INDEX idx_reclog_user    ON recommendation_logs(user_id, served_at);
"""

QUERIES = {
    "Q1": ("Top 5 songs by AI Recommendation Score (feeds 'Top Picks For You')",
           """SELECT s.song_id, s.genre, r.ai_recommendation_score AS score, r.rank_position AS rank
FROM recommendation_logs r JOIN songs s USING (song_id)
WHERE r.model_version = 'v1.0'
ORDER BY score DESC LIMIT 5;"""),
    "Q2": ("Genre engagement: minutes per play, skip rate and rating",
           """SELECT s.genre, lb.play_count, lb.listening_minutes,
       ROUND(1.0 * lb.listening_minutes / lb.play_count, 2) AS min_per_play,
       lb.skip_rate, lb.user_rating
FROM listening_behavior lb JOIN songs s USING (song_id)
ORDER BY min_per_play DESC;"""),
    "Q3": ("User segmentation by play count",
           """SELECT u.user_id, p.plan_name, lb.play_count,
       CASE WHEN lb.play_count >= 30 THEN 'Power'
            WHEN lb.play_count >= 20 THEN 'Regular'
            ELSE 'Casual' END AS segment
FROM users u
JOIN subscription_plans p USING (plan_id)
JOIN listening_behavior lb USING (user_id)
ORDER BY lb.play_count DESC;"""),
    "Q4": ("Songs at risk: skip rate of 0.20 or more",
           """SELECT song_id, genre, skip_rate, user_rating
FROM listening_behavior JOIN songs USING (song_id)
WHERE skip_rate >= 0.20
ORDER BY skip_rate DESC;"""),
    "Q5": ("Recommendation outcomes by model version",
           """SELECT model_version, COUNT(*) AS served,
       SUM(user_action = 'Saved')   AS saved,
       SUM(user_action = 'Skipped') AS skipped,
       ROUND(AVG(ai_recommendation_score), 3) AS avg_score
FROM recommendation_logs GROUP BY model_version;"""),
    "Q6": ("Watch-to-listen bridge: songs from titles the user watched",
           """SELECT w.user_id, t.title_name, s.song_id, s.genre
FROM watch_history w
JOIN netflix_titles t USING (title_id)
JOIN songs s ON s.source_title_id = t.title_id
WHERE w.user_id IN (SELECT user_id FROM users WHERE personalization_consent = 1)
ORDER BY w.user_id;"""),
}

PLANS = {101: 3, 102: 2, 103: 1, 104: 3, 105: 2, 106: 3, 107: 1, 108: 2, 109: 1, 110: 3}
SOUNDTRACK = {"Pop": "T-100", "EDM": "T-200", "Metal": "T-200", "Classical": "T-300"}


def _seed_sql(scored):
    out = ["INSERT INTO subscription_plans VALUES (1,'Standard with Ads',7.99,1),"
           "(2,'Standard',17.99,0),(3,'Premium',24.99,0);",
           "INSERT INTO netflix_titles VALUES ('T-100','Sample Series A','Series','Drama'),"
           "('T-200','Sample Film B','Film','Action'),('T-300','Sample Special C','Special','Music');"]
    for _, r in scored.sort_values("user_id").iterrows():
        i = int(r.song_id[1:])
        src = SOUNDTRACK.get(r.genre)
        out.append(f"INSERT INTO users VALUES ({r.user_id},'User {r.user_id}',{PLANS[r.user_id]},'US','2026-01-15',1);")
        out.append(f"INSERT INTO artists VALUES ('A{i:03d}','Artist {i:03d}');")
        out.append(f"INSERT INTO songs VALUES ('{r.song_id}','Song {r.song_id}','{r.genre}','A{i:03d}',"
                   f"{repr(src) if src else 'NULL'},210,{1 if src else 0});")
        out.append(f"INSERT INTO listening_behavior VALUES ({r.user_id},'{r.song_id}',{r.play_count},"
                   f"{r.skip_rate},{r.user_rating},{r.listening_minutes});")
    out.append("INSERT INTO watch_history (user_id,title_id,watched_at,minutes_watched) VALUES "
               "(101,'T-100','2026-02-01 20:00',55),(106,'T-200','2026-02-02 21:00',118),"
               "(110,'T-200','2026-02-03 22:00',120),(105,'T-300','2026-02-04 19:00',64);")
    out.append("INSERT INTO training_datasets VALUES ('DS-2026-01','Listening + watch signals v1',"
               "'listening_behavior,watch_history',10,'2026-03-10');")
    out.append("INSERT INTO ai_models VALUES ('v1.0','Weighted engagement score (baseline)','DS-2026-01','2026-03-15','Deployed'),"
               "('v2.0','Two-tower retrieval + gradient-boosted ranker','DS-2026-01',NULL,'Training');")
    for _, r in scored.iterrows():
        action = "Saved" if r.user_rating >= 4.7 else ("Skipped" if r.skip_rate >= 0.22 else "Played")
        out.append("INSERT INTO recommendation_logs (user_id,song_id,model_version,ai_recommendation_score,"
                   f"rank_position,served_at,user_action) VALUES ({r.user_id},'{r.song_id}','v1.0',"
                   f"{r.ai_recommendation_score},{r['rank']},'2026-03-16 09:00','{action}');")
    out.append("INSERT INTO playlists VALUES ('P-001','Top Picks For You',NULL,'AI-Generated','v1.0','2026-03-16'),"
               "('P-002','Because You Watched: Sample Film B',110,'Watch-Inspired','v1.0','2026-03-16');")
    for pos, s in enumerate(scored.song_id.head(5), 1):
        out.append(f"INSERT INTO playlist_songs VALUES ('P-001','{s}',{pos});")
    out.append("INSERT INTO playlist_songs VALUES ('P-002','S006',1),('P-002','S010',2);")
    return out


def build(scored, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    seed = _seed_sql(scored)
    sql = ["-- Netflix Music: schema, sample data and analysis queries (SQLite)",
           "-- Generated by code/src/database.py from CEP_Dataset.xlsx, Sheet 1 - Music Data", SCHEMA,
           "-- Sample data (names, artists and titles are placeholders: Sheet 1 has IDs only)"] + seed + [""]
    for k, (title, q) in QUERIES.items():
        sql += [f"-- {k}: {title}", q, ""]
    (out_dir / "netflix_music.sql").write_text("\n".join(sql))

    db = out_dir / "netflix_music.db"
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    con.executescript(SCHEMA + "\n".join(seed))
    con.commit()
    results = {}
    for k, (title, q) in QUERIES.items():
        cur = con.execute(q)
        results[k] = (title, q, [d[0] for d in cur.description], cur.fetchall())
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    con.close()
    return results, tables
