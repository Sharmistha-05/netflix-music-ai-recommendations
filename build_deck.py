"""Step 2: build the PowerPoint project report.

    python build_deck.py            # runs build_visuals first, then writes the deck
Output: output/Netflix_Music_AI_Experience_Report.pptx
"""
from pathlib import Path

from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor

import build_visuals
from src import analysis as A
from src.deck import (Deck, RED, INK, INK2, PANEL, PINK, WHITE, DARK, HEAD, GREEN, AMBER, LINE)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
FIG = OUT / "figures"
DECK = OUT / "Netflix_Music_AI_Experience_Report.pptx"
GREY_TXT = RGBColor(0xBF, 0xBF, 0xBF)
B = {"bold": True}
R = {"bold": True, "color": RED}


def build():
    ctx = build_visuals.run()
    d = Deck()
    scored, corr, wsjf, tsum = ctx["scored"], ctx["corr"], ctx["wsjf"], ctx["tsum"]
    dm, totals, cm, results = ctx["dm"], ctx["totals"], ctx["cm"], ctx["results"]
    ms = A.music_summary(ctx["music"])
    mix = cm[cm.model.str.startswith("Recommended")].iloc[0]
    flash = cm[cm.model == "Gemini 3.8 Flash"].iloc[0]
    flash27 = cm[cm.model.str.contains("2027")].iloc[0]
    top3 = scored.head(3)

    # ================================================================== 1 Title
    s = d.prs.slides.add_slide(d.blank)
    d.rect(s, 0, 0, 13.333, 7.5, DARK)
    d.rect(s, 0, 0, 13.333, 0.1, RED)
    d.text(s, 0.9, 0.95, 11, 0.4, "PRODUCT MANAGEMENT", size=13, bold=True, color=RED)
    d.text(s, 0.9, 1.4, 11.6, 1.5, ["AI-Driven Music Experience", "for Netflix Music"], size=40, bold=True, color=WHITE, spacing=0.05)
    d.text(s, 0.9, 2.95, 11.3, 0.9, "Technology stack, data model, GenAI model selection and Agile delivery "
           "for AI-powered music recommendations", size=18, color=GREY_TXT)
    d.rect(s, 0.9, 3.9, 10.8, 0.015, RGBColor(0x55, 0x55, 0x55))
    meta = [("SUBMITTED BY", "Sharmistha Chakrabortty"), ("ROLE", "Aspiring Product Manager"),
            ("UNIVERSITY", "UC San Diego Extended Studies"),
            ("PROGRAM", "AI-Powered Product Management Professional Program"),
            ("COURSE", "Technology Essentials for Product Managers"), ("DATE", "November 17, 2026")]
    for i, (k, v) in enumerate(meta):
        y = 4.1 + i * 0.47
        d.text(s, 0.9, y + 0.04, 2.4, 0.35, k, size=10, bold=True, color=RED)
        d.text(s, 3.3, y, 8.5, 0.4, v, size=15 if i else 17, bold=(i == 0), color=WHITE)
    d.notes(s, "Course-end project: build the technical foundation for Netflix Music's AI recommendations. "
               "It continues the earlier Netflix Music product-sense project (why, who, MVP) with how to build it.")

    # ================================================================== 2 Agenda
    s = d.base("Agenda", "Four tasks from the brief, framed by research and closed with results")
    parts = [("01", "Where we start", "Context from the earlier project and the STAR map of this brief"),
             ("02", "How the leaders recommend", "Recommendation models at Netflix, Spotify, YouTube, Pandora, Apple"),
             ("03", "Task 1  Technology stack", "Frontend, real-time backend, databases and third-party APIs"),
             ("04", "Task 2  ER diagram and data", "12-entity model, Sheet 1 analysis, SQL and the AI score"),
             ("05", "Task 3  GenAI model selection", "OpenAI vs Gemini on cost, latency, tokens, accuracy, ethics"),
             ("06", "Task 4  Agile workflow and Trello", "Kanban board, WSJF backlog, sprint plan and metrics"),
             ("07", "Results", "Outcomes, roadmap, risks and conclusion")]
    for i, (n, t, sub) in enumerate(parts):
        y = 1.75 + i * 0.73
        d.text(s, 0.6, y, 0.8, 0.5, n, size=22, bold=True, color=RED)
        d.text(s, 1.5, y + 0.02, 4.6, 0.4, t, size=17, bold=True)
        d.text(s, 6.2, y + 0.05, 6.5, 0.4, sub, size=14, color=INK2)
        if i < len(parts) - 1:
            d.rect(s, 1.5, y + 0.6, 11.2, 0.01, LINE)

    # ================================================================== 3 Executive summary
    s = d.base("Executive summary", "Netflix Music can ship AI recommendations on a stack Netflix already runs, "
               "with OpenAI as the GenAI layer", source="CEP_Dataset.xlsx (Sheets 1 and 2); vendor pricing and "
               "benchmarks read 17 Nov 2026; report analysis")
    cards = [
        ("Task 1  Technology stack", ["React Native apps with native audio, Java + Spring Boot microservices, "
         "Kafka and WebSockets for real-time updates, polyglot data on AWS (PostgreSQL, Cassandra, Redis, "
         "OpenSearch, S3 + Iceberg). React Native scores 4.6 / 5 against Flutter (3.75) and native (3.6)."]),
        ("Task 2  ER diagram", [f"12 entities in third normal form cover users, songs, playlists and AI model "
         f"data. Sheet 1 maps to LISTENING_BEHAVIOR. Skip rate is the strongest negative signal "
         f"(r = {corr.loc['skip_rate', 'user_rating']}); the baseline score ranks "
         f"{', '.join(top3.genre)} top."]),
        ("Task 3  GenAI model", [f"OpenAI (GPT-6.1 Terra for volume, Sol for hard queries) scores "
         f"{totals['openai']:.2f} vs Gemini {totals['gemini']:.2f}: faster first token, fewer hallucinations, "
         f"stable price. About ${mix.per_mau_usd:.3f} per user per month at 5M MAU."]),
        ("Task 4  Agile and Trello", ["Kanban board with Backlog, In Progress and Completed holds 17 cards "
         "(10 from Sheet 2, 7 from the brief). WSJF orders the backlog: GenAI model selection, then Data "
         "Security Review. The WIP limit flags In Progress (6 cards vs limit 5)."]),
    ]
    for i, (lab, body) in enumerate(cards):
        x, y = 0.6 + (i % 2) * 6.13, 1.7 + (i // 2) * 2.62
        d.card(s, x, y, 6.0, 2.48, lab, body, size=14.5)

    # ================================================================== 4 Building on earlier work
    s = d.base("This project picks up where the product-sense work stopped",
               "The earlier project answered why and what; this one answers how to build it",
               source="Earlier project: Netflix_Music_Project_Report_v2.pptx and Netflix_Dataset.xlsx")
    d.card(s, 0.6, 1.7, 3.8, 4.95, "Earlier project: product sense", [
        [("Why: ", B), "listening hours Netflix monetizes at zero today"],
        [("Who: ", B), "three personas: Binge-Watcher, Casual Listener, Regional Listener"],
        [("What: ", B), "MVP = AI-generated playlists (RICE 144,000) and watch-history discovery (129,600)"],
        [("When: ", B), "MVP by mid-2027, then growth and monetization phases"]], size=14.5)
    d.arrow(s, 4.55, 3.95, 0.5, 0.45)
    d.card(s, 5.2, 1.7, 7.53, 4.95, "This project: technical delivery of that MVP", [
        [("Task 1  Stack: ", B), "the systems that serve AI playlists and watch-history discovery in real time"],
        [("Task 2  Data model: ", B), "how watch history, listening behaviour and AI scores connect"],
        [("Task 3  GenAI: ", B), "which model writes playlist copy, powers the AI DJ and conversational search"],
        [("Task 4  Agile: ", B), "how the team prioritises, tracks and ships the work in sprints"],
        [("Thread through every slide: ", R), "the question from the earlier deck, "
         "“How might we turn what members watch into what they love to listen to?”"]],
        fill=PINK, size=14.5)

    # ================================================================== 5 STAR map
    s = d.base("The brief in STAR form, and where each part is answered",
               "Situation, Task, Action, Result mapped to the slides that deliver them")
    rows = [["", "What the brief says", "How this report answers it", "Slides"],
            ["Situation", "Netflix enters music streaming; must beat Spotify and Apple Music with AI, data and Agile",
             "Research on leading recommenders; differentiators turned into product principles", "7-10"],
            ["Task", "Choose a stack; design an ER diagram; pick OpenAI vs Gemini; run Agile in Trello",
             "One part per task, each ending in a decision and its justification", "11-54"],
            ["Action", "Components, frontend, real-time backend, databases, APIs; entities; cost, latency, "
             "tokens, accuracy; Kanban lists", "Scored comparisons, SQL on Sheet 1, weighted decision matrix, "
             "WSJF on Sheet 2", "12-54"],
            ["Result", "Stack report, ER diagram, GenAI selection report, Kanban workflow",
             "Results checklist, roadmap, risks; code, database and board export delivered", "56-59"]]
    d.table(s, 0.6, 1.75, [1.5, 4.6, 4.9, 1.1], rows, size=12, row_h=0.95, bold_first_col=True)

    # ================================================================== PART 1
    d.section("Part 1", "How the leaders recommend",
              "What successful streaming platforms teach us before we choose any technology")

    # ================================================================== 7 Platform research
    s = d.base("Leading recommenders blend methods, and each teaches one lesson",
               "Public descriptions of the recommendation approaches at five platforms",
               source="Gomez-Uribe & Hunt, ACM TMIS 2015 (Netflix); Covington et al., RecSys 2016 (YouTube); "
                      "Spotify and Pandora engineering and press materials")
    rows = [["Platform", "How it recommends", "Signals used", "What Netflix Music takes"],
            ["Netflix (video)", "Personalized ranking of rows and titles; contextual bandits choose artwork",
             "Plays, completion, time of day, device", "Personalize the presentation, not only the ranking"],
            ["Spotify", "Discover Weekly blends collaborative filtering, NLP on text about music and audio models; "
             "AI DJ adds generative voice", "Playlists, skips, saves, audio features", "Hybrid model plus a GenAI "
             "explanation layer"],
            ["YouTube", "Two-stage deep network: candidate generation, then ranking",
             "Watch time, satisfaction surveys", "Two-stage architecture to scale to millions of songs"],
            ["Pandora", "Music Genome Project: analysts tag songs on hundreds of musical attributes",
             "Content attributes, thumbs", "Content features solve cold start for new exclusives"],
            ["Apple Music", "Human editorial curation combined with algorithmic personalization",
             "Library, plays, editorial picks", "Editorial trust for Netflix soundtracks and originals"]]
    d.table(s, 0.6, 1.65, [1.6, 4.4, 2.9, 3.23], rows, size=11.5, row_h=0.86, bold_first_col=True)
    d.notes(s, "About 80% of hours streamed on Netflix come from recommendations (Gomez-Uribe & Hunt, 2015).")

    # ================================================================== 8 Pipeline
    s = d.base("The recommendation pipeline for Netflix Music",
               "Classical ML ranks the songs; GenAI explains and converses. The two do different jobs")
    steps = [("Signals", "Watch history (with consent), listening behaviour, context, catalog metadata"),
             ("Candidate generation", "Two-tower model picks ~1,000 songs from millions in milliseconds"),
             ("Ranking", "Gradient-boosted ranker scores each candidate; the AI score lives here"),
             ("Re-ranking", "Diversity, freshness, exclusives, artist fairness, kids-profile rules"),
             ("GenAI layer", "Playlist titles, AI DJ narration, “why this song”, conversational search")]
    for i, (t, body) in enumerate(steps):
        x = 0.6 + i * 2.47
        fill = PINK if i == 4 else PANEL
        d.rect(s, x, 1.75, 2.2, 3.15, fill)
        d.text(s, x + 0.15, 1.88, 1.9, 0.3, f"STEP {i + 1}", size=10, bold=True, color=RED)
        d.text(s, x + 0.15, 2.2, 1.9, 0.6, t, size=15, bold=True)
        d.text(s, x + 0.15, 2.9, 1.9, 1.9, body, size=12, color=INK2)
        if i < 4:
            d.arrow(s, x + 2.22, 3.15, 0.23, 0.3)
    d.rect(s, 0.6, 5.15, 12.13, 0.7, RGBColor(0xEE, 0xF6, 0xEE))
    d.text(s, 0.8, 5.25, 11.8, 0.5, [[("Feedback loop: ", B), "every recommendation is logged with model "
           "version, score and user action (played, skipped, saved). Logs retrain the models; skip rate is the "
           "fastest negative signal."]], size=13, anchor=MSO_ANCHOR.MIDDLE)
    d.text(s, 0.6, 6.05, 12.1, 0.8, [[("Why GenAI does not rank: ", R), "ranking needs millisecond latency at "
           "millions of calls and a measurable objective. LLMs are slower, costlier per call and harder to "
           "evaluate. They add the most value on the words around the music."]], size=13)

    # ================================================================== 9 Principles
    s = d.base("Five product principles from the research",
               "These principles drive the decisions in every later part")
    pr = [("Blend, don't pick", "Hybrid of collaborative, content and context signals beats any single method"),
          ("Two stages for scale", "Retrieve broadly, then rank precisely: the only way to serve millions fast"),
          ("Explain the pick", "“Because you watched” builds trust; GenAI writes the reason"),
          ("Satisfaction over clicks", "Optimize saves and listen-through; treat skips as negative feedback"),
          ("Win the cold start", "Watch history and content tags recommend well before any listening exists")]
    for i, (t, body) in enumerate(pr):
        y = 1.7 + i * 1.03
        d.rect(s, 0.6, y, 12.13, 0.9, PANEL)
        d.text(s, 0.8, y + 0.2, 0.6, 0.5, str(i + 1), size=24, bold=True, color=RED)
        d.text(s, 1.5, y + 0.25, 3.6, 0.45, t, size=16, bold=True)
        d.text(s, 5.2, y + 0.25, 7.4, 0.45, body, size=14, color=INK2)

    # ================================================================== 10 Differentiators
    s = d.base("Netflix Music's three differentiators need three technical capabilities",
               "The brief's differentiators translated into what the platform must do")
    diff = [("Curated playlists from viewing habits", "Join watch history to songs; real-time features; "
             "consent-aware data access", "WATCH_HISTORY, NETFLIX_TITLES, SONGS.source_title_id"),
            ("AI-powered personalized recommendations", "Two-stage recommender, feature store, model registry, "
             "A/B testing", "LISTENING_BEHAVIOR, AI_MODELS, RECOMMENDATION_LOGS"),
            ("Exclusive audio: podcasts and original soundtracks", "DRM streaming, long-context GenAI for "
             "summaries and chapters, editorial tools", "SONGS.is_netflix_exclusive, PLAYLISTS (Editorial)")]
    for i, (t, cap, ent) in enumerate(diff):
        x = 0.6 + i * 4.1
        d.rect(s, x, 1.75, 3.93, 4.9, PANEL)
        d.text(s, x + 0.2, 1.9, 3.5, 0.3, f"DIFFERENTIATOR {i + 1}", size=10, bold=True, color=RED)
        d.text(s, x + 0.2, 2.25, 3.5, 1.0, t, size=17, bold=True)
        d.text(s, x + 0.2, 3.4, 3.5, 0.3, "CAPABILITY NEEDED", size=10, bold=True, color=INK2)
        d.text(s, x + 0.2, 3.7, 3.5, 1.3, cap, size=13)
        d.text(s, x + 0.2, 5.1, 3.5, 0.3, "WHERE IT LIVES IN THE DATA MODEL", size=10, bold=True, color=INK2)
        d.text(s, x + 0.2, 5.4, 3.5, 1.1, ent, size=12, color=INK2)

    # ================================================================== PART 2
    d.section("Part 2  |  Task 1", "Technology stack",
              "Chosen for performance, scalability and integration with what Netflix already runs")

    # ================================================================== 12 Requirements
    s = d.base("Requirements first: the targets the stack must hit",
               "Non-functional requirements set before choosing any technology (planning targets)")
    rows = [["Requirement", "Target", "Why it matters for Netflix Music"],
            ["Playback start", "Under 1 second", "Music is skipped in seconds; slow starts lose the session"],
            ["Recommendation API", "p95 under 150 ms", "Home and Up Next must render instantly"],
            ["Real-time adaptation", "New skip or play reflected in under 5 s", "The next song should react to "
             "the last skip"],
            ["GenAI response", "First token under 3 s, streamed", "AI DJ and conversational search feel live"],
            ["Scale", "5M MAU at launch, 50M+ without redesign", "Netflix can cross-promote to its whole base"],
            ["Availability", "99.99% across regions", "Music plays in cars and on commutes: no outages"],
            ["Integration", "Netflix account SSO, watch history, CDN, billing", "Reuse beats rebuild; one "
             "account, one bill"],
            ["Privacy", "Opt-in for watch-to-listen; GDPR / CCPA", "Viewing history is personal data"]]
    d.table(s, 0.6, 1.65, [2.6, 3.9, 5.63], rows, size=12, row_h=0.56, bold_first_col=True)

    # ================================================================== 13 Components
    s = d.base("Key technical components of Netflix Music",
               "Eight building blocks; each maps to a layer of the reference architecture")
    comps = [("Client apps", "iOS, Android, web, TV, car; offline downloads; background audio"),
             ("Audio delivery", "Adaptive HLS / DASH (AAC, Opus), DRM, CDN caching near users"),
             ("API gateway", "Auth, routing, rate limits; GraphQL for apps, REST for partners"),
             ("Core services", "Catalog, playback, playlists, profiles, entitlements, search"),
             ("Event streaming", "Every play, skip and save as an event, processed in real time"),
             ("ML platform", "Feature store, training pipelines, model registry, online serving, A/B tests"),
             ("Data stores", "Relational, wide-column, cache, search, vector and lakehouse storage"),
             ("GenAI service", "Model gateway, prompts, guardrails, caching, cost and quality monitoring")]
    for i, (t, body) in enumerate(comps):
        x, y = 0.6 + (i % 4) * 3.07, 1.75 + (i // 4) * 2.5
        d.rect(s, x, y, 2.9, 2.3, PANEL)
        d.text(s, x + 0.2, y + 0.18, 2.5, 0.3, f"{i + 1:02d}", size=12, bold=True, color=RED)
        d.text(s, x + 0.2, y + 0.5, 2.5, 0.4, t, size=16, bold=True)
        d.text(s, x + 0.2, y + 1.0, 2.5, 1.2, body, size=12, color=INK2)

    # ================================================================== 14 Stack table
    s = d.base("The technology stack at a glance",
               "Each choice with the main alternative considered",
               source="Netflix Tech Blog (DGS, EVCache, Iceberg, Metaflow, Open Connect); report analysis")
    rows = [["Layer", "Choice", "Alternative considered", "Deciding reason"],
            ["Mobile frontend", "React Native + native audio modules (Media3 / ExoPlayer, AVPlayer)",
             "Flutter; fully native", "Code reuse with Netflix's React web stack; native-grade audio"],
            ["Web frontend", "React + Next.js", "Angular", "Server rendering for fast first paint; team skills"],
            ["Backend services", "Java 21 + Spring Boot, GraphQL (Netflix DGS)", "Node.js; Go",
             "Netflix's proven service stack and resilience tooling"],
            ["Real-time", "Apache Kafka + Apache Flink; WebSockets / gRPC streams", "Polling; RabbitMQ",
             "Durable, replayable events; push updates to apps"],
            ["ML and serving", "Python, PyTorch, Metaflow, feature store", "TensorFlow; managed AutoML",
             "Netflix-built Metaflow; flexible research to production"],
            ["Databases", "PostgreSQL (Aurora), Cassandra, EVCache / Redis, OpenSearch, S3 + Iceberg",
             "Single relational DB", "Each data shape gets the store built for it"],
            ["Cloud and CDN", "AWS multi-region + Netflix Open Connect", "GCP; third-party CDN",
             "Where Netflix already runs; no migration"],
            ["GenAI", "OpenAI API behind a model gateway", "Google Gemini", "Part 4: wins on latency, "
             "accuracy and stable cost"]]
    d.table(s, 0.6, 1.62, [1.85, 4.15, 2.45, 3.68], rows, size=11, row_h=0.58, bold_first_col=True)

    # ================================================================== 15 Frontend
    s = d.base("Frontend: React Native with native audio modules",
               "Weighted comparison of three options for the mobile apps (scores 1 to 5)",
               source="Report analysis; weights reflect launch priorities")
    rows = [["Criterion", "Weight", "React Native", "Flutter", "Native (Swift / Kotlin)"],
            ["Code reuse across iOS, Android, web", "25%", "5", "5", "2"],
            ["Performance (audio, animation, start time)", "25%", "4", "4", "5"],
            ["Fit with Netflix skills and React ecosystem", "20%", "5", "3", "4"],
            ["Background audio, CarPlay, Android Auto", "15%", "4", "4", "5"],
            ["Ship fixes and experiments fast (OTA updates)", "15%", "5", "2", "2"],
            [("Weighted score", B), "", ("4.60", R), ("3.75", B), ("3.60", B)]]
    ca = [None, PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.CENTER]
    d.table(s, 0.6, 1.7, [4.1, 1.0, 1.5, 1.3, 2.0], rows, size=12.5, row_h=0.6, col_align=ca,
            highlight={6: PINK})
    d.card(s, 10.75, 1.7, 1.98, 4.2, "Decision", ["React Native for the UI.", "Native modules for "
           "playback, downloads and car integration, where native wins."], size=12)
    d.text(s, 0.6, 6.15, 12.1, 0.7, [[("Why not Flutter? ", B), "Flutter performs as well, and it won the smart-home "
           "exercise in Lesson 1. Here it loses on team fit and fast experimentation: Netflix builds its web UI "
           "in React, and music apps live on rapid A/B tests."]], size=12.5)

    # ================================================================== 16 Backend real-time
    s = d.base("Backend: event-driven services keep recommendations live",
               "What happens in the seconds after a listener skips a song")
    flow = [("Skip", "App sends a skip event"), ("Kafka", "Event lands on listening-events topic"),
            ("Flink", "Updates session features: skip rate, mood, genre"),
            ("Recommender", "Re-ranks Up Next with fresh features"),
            ("Push", "WebSocket sends the new queue to the app")]
    for i, (t, body) in enumerate(flow):
        x = 0.6 + i * 2.47
        d.box(s, x, 1.75, 2.2, 0.62, t, fill=RED if i in (1, 2) else HEAD, size=15, color=WHITE, bold=True)
        d.text(s, x, 2.47, 2.2, 0.9, body, size=12, color=INK2, align=PP_ALIGN.CENTER)
        if i < 4:
            d.arrow(s, x + 2.22, 1.9, 0.23, 0.3)
    d.text(s, 0.6, 3.35, 12.1, 0.4, "Target: under 5 seconds end to end", size=12, bold=True, color=RED,
           align=PP_ALIGN.CENTER)
    d.card(s, 0.6, 3.95, 3.93, 2.75, "Java 21 + Spring Boot", ["Netflix's service stack (DGS GraphQL, "
           "resilience patterns). Virtual threads handle many concurrent streams cheaply."], size=14)
    d.card(s, 4.7, 3.95, 3.93, 2.75, "Kafka + Flink", ["Kafka keeps every event durable and replayable "
           "for retraining. Flink computes features in real time with exactly-once state."], size=14)
    d.card(s, 8.8, 3.95, 3.93, 2.75, "WebSockets / gRPC", ["Server push instead of polling: the app gets "
           "a new queue the moment it changes. Fewer requests, less battery."], size=14)

    # ================================================================== 17 Databases
    s = d.base("Databases: the right store for each kind of data",
               "Polyglot persistence, mapped to the entities in the ER diagram")
    rows = [["Data", "Store", "ER entities", "Why this store"],
            ["Users, plans, catalog, playlists", "PostgreSQL (Amazon Aurora)",
             "USERS, SUBSCRIPTION_PLANS, SONGS, ARTISTS, PLAYLISTS", "Relational integrity, joins, ACID for billing"],
            ["Listening events, recommendation logs", "Apache Cassandra",
             "LISTENING_BEHAVIOR, RECOMMENDATION_LOGS, WATCH_HISTORY", "Write-heavy time series; multi-region"],
            ["Sessions, Up Next, hot features", "EVCache / Redis", "Derived from the tables above",
             "Sub-millisecond reads on every screen"],
            ["Search", "OpenSearch", "SONGS, ARTISTS, NETFLIX_TITLES", "Full-text, typo-tolerant, fast facets"],
            ["Song and user embeddings", "Vector index (OpenSearch k-NN)", "Model outputs for SONGS and USERS",
             "Nearest-neighbour retrieval for candidates"],
            ["Training data and analytics", "Amazon S3 + Apache Iceberg", "TRAINING_DATASETS, AI_MODELS lineage",
             "Cheap storage, time travel for reproducible training"]]
    d.table(s, 0.6, 1.65, [2.85, 2.55, 3.65, 3.08], rows, size=11.5, row_h=0.7, bold_first_col=True)
    d.text(s, 0.6, 6.7, 12.1, 0.3, "The SQLite build in this project implements the relational core of the "
           "model (12 tables) to validate the design.", size=11, color=INK2)

    # ================================================================== 18 APIs
    s = d.base("Third-party API integrations, assessed",
               "Adopt only what Netflix should not build; every API is tested in Postman before integration",
               source="Vendor documentation; Lesson 1 demo (testing APIs with Postman)")
    rows = [["API", "Purpose", "Performance plan", "Main risk", "Decision"],
            ["OpenAI API", "AI DJ narration, playlist copy, conversational search", "Streaming, caching, batch "
             "for nightly copy", "Vendor lock-in", ("Adopt via gateway", R)],
            ["Gracenote music metadata", "Moods, tempo, genre for cold start", "Nightly batch into catalog",
             "Licensing cost", ("Adopt", B)],
            ["MusicBrainz", "Open IDs to match ISRC and artists", "Batch, cached", "Data quality",
             ("Supplement", B)],
            ["Musixmatch lyrics", "Synced lyrics, karaoke mode later", "Cached at edge", "Licensing",
             ("Phase 2", B)],
            ["APNs and Firebase Cloud Messaging", "Push: new soundtrack drops", "Async, batched",
             "Opt-out fatigue", ("Adopt", B)],
            ["CarPlay, Android Auto, Cast, AirPlay", "Listening in car and on speakers", "Native SDKs",
             "Certification time", ("Adopt", B)],
            ["Payments", "Reuse Netflix billing", "Existing", "None new", ("Reuse", B)]]
    d.table(s, 0.6, 1.65, [2.55, 3.15, 2.55, 1.85, 2.03], rows, size=11.5, row_h=0.56, bold_first_col=True)
    d.text(s, 0.6, 6.25, 12.1, 0.7, [[("Postman test plan: ", B), "a collection per API with GET / POST checks, "
           "expected status codes (200, 201), response-time budgets and schema assertions, run in CI on every "
           "build."]], size=12.5)

    # ================================================================== 19 Architecture (native shapes)
    s = d.base("Reference architecture", "Seven layers on AWS, multi-region active-active")
    layers = [("Clients", "React Native (iOS, Android)  |  React + Next.js web  |  TV and car  |  Native audio: "
               "Media3 / ExoPlayer, AVPlayer"),
              ("Edge and delivery", "Netflix Open Connect + CloudFront  |  HLS / DASH (AAC, Opus)  |  Widevine / "
               "FairPlay DRM  |  API gateway"),
              ("API layer", "GraphQL federation (Netflix DGS)  |  REST for partners  |  WebSockets / gRPC "
               "streams"),
              ("Microservices", "Java 21 + Spring Boot: catalog, playback, playlists, profiles, entitlements  |  "
               "Python: recommender, GenAI"),
              ("Streaming and ML", "Kafka events, Flink features, feature store  |  PyTorch + Metaflow training  "
               "|  vector index"),
              ("Data", "PostgreSQL (Aurora)  |  Cassandra  |  EVCache / Redis  |  OpenSearch  |  S3 + Iceberg"),
              ("Third-party APIs", "OpenAI (via model gateway)  |  Gracenote, MusicBrainz  |  Musixmatch  |  "
               "APNs / FCM  |  Netflix SSO")]
    for i, (n, body) in enumerate(layers):
        y = 1.62 + i * 0.75
        hot = i in (3, 4)
        d.box(s, 0.6, y, 2.5, 0.63, n, fill=RED if hot else HEAD, color=WHITE, bold=True, size=13)
        d.box(s, 3.2, y, 9.53, 0.63, body, fill=PINK if hot else PANEL, size=12, align=PP_ALIGN.LEFT)
    d.text(s, 0.6, 6.92, 12.1, 0.3, "Red layers carry the AI recommendation work.", size=10, color=INK2)

    # ================================================================== 20 Together
    s = d.base("How the pieces work together: one “Because you watched” playlist",
               "A member finishes a series and opens Netflix Music")
    steps = [("1", "Sign in", "Netflix SSO; the gateway checks the plan and the watch-to-listen consent flag"),
             ("2", "Read signals", "Watch history (Cassandra) and listening features (Redis) for this member"),
             ("3", "Retrieve and rank", "Two-tower model pulls the series soundtrack and similar songs; ranker "
              "scores them"),
             ("4", "Write the words", "GenAI service asks OpenAI for a title and a one-line “why”; "
              "cached for reuse"),
             ("5", "Stream", "App plays via Open Connect with DRM; first audio under 1 second"),
             ("6", "Learn", "Plays, skips and saves flow to Kafka and the recommendation log")]
    for i, (n, t, body) in enumerate(steps):
        x, y = 0.6 + (i % 3) * 4.1, 1.75 + (i // 3) * 2.55
        d.rect(s, x, y, 3.93, 2.35, PANEL)
        d.text(s, x + 0.2, y + 0.15, 0.6, 0.6, n, size=28, bold=True, color=RED)
        d.text(s, x + 0.9, y + 0.28, 2.9, 0.4, t, size=16, bold=True)
        d.text(s, x + 0.2, y + 0.92, 3.5, 1.35, body, size=13, color=INK2)

    # ================================================================== 21 P/S/I justification
    s = d.base("Justification: performance, scalability and integration",
               "The three criteria from the brief, applied to every layer")
    rows = [["Layer and choice", "Performance", "Scalability", "Integration feasibility"],
            ["React Native + native audio", "Native playback; 60 fps UI", "One codebase across platforms",
             "Reuses Netflix React skills and SSO"],
            ["Java + Spring Boot, DGS", "JIT-compiled; virtual threads", "Stateless, autoscaled pods",
             "Netflix's own GraphQL framework"],
            ["Kafka + Flink + WebSockets", "Sub-5 s feature freshness", "Millions of events per second, "
             "partitioned", "Same events feed ML training"],
            ["PostgreSQL + Cassandra + Redis", "Sub-ms cache; fast writes", "Cassandra scales linearly, "
             "multi-region", "Standard drivers; Netflix runs all three"],
            ["OpenSearch + vector index", "Typo-tolerant search in ms", "Sharded clusters",
             "One engine for text and embeddings"],
            ["AWS + Open Connect CDN", "Audio cached inside ISPs", "Global footprint already built",
             "No migration; shared tooling"],
            ["OpenAI via model gateway", "2.8 s median first token (Terra)", "Batch and caching cut load",
             "Gateway allows a switch to Gemini"]]
    d.table(s, 0.6, 1.65, [3.2, 2.95, 2.95, 3.03], rows, size=11.5, row_h=0.62, bold_first_col=True)

    # ================================================================== PART 3
    d.section("Part 3  |  Task 2", "ER diagram and the data behind it",
              "Mapping users, songs, playlists and AI model data")

    # ================================================================== 23 Sheet 1 profile
    s = d.base("Sheet 1 - Music Data at a glance", "10 listening records: one user, one song, one genre each",
               source="CEP_Dataset.xlsx, Sheet 1 - Music Data")
    kp = [(f"{ms['rows']}", "users and songs"), (f"{ms['plays_total']}", "total plays"),
          (f"{ms['minutes_total']:,}", "listening minutes"), (f"{ms['skip_mean']:.3f}", "average skip rate"),
          (f"{ms['rating_mean']:.2f}", "average rating (of 5)")]
    for i, (v, l) in enumerate(kp):
        d.kpi(s, 0.6 + i * 2.45, 1.65, 2.3, 1.05, v, l)
    m = ctx["music"].sort_values("user_id")
    rows = [["User_ID", "Song_ID", "Genre", "Play_Count", "Skip_Rate", "User_Rating", "Listening min"]] + \
           [[str(r.user_id), r.song_id, r.genre, str(r.play_count), f"{r.skip_rate:.2f}", f"{r.user_rating:.1f}",
             str(r.listening_minutes)] for r in m.itertuples()]
    ca = [PP_ALIGN.CENTER] * 7
    d.table(s, 0.6, 2.9, [1.55, 1.55, 2.0, 1.75, 1.75, 1.75, 1.78], rows, size=11, row_h=0.355, col_align=ca)

    # ================================================================== 24 ER diagram
    s = d.base("Entity-relationship diagram for Netflix Music",
               "12 entities: users and behaviour, songs and playlists, AI model data")
    d.image(s, FIG / "er_diagram.png", 0.45, 1.5, 9.95, 5.45)
    d.card(s, 10.5, 1.6, 2.23, 5.25, "How to read it", [
        [("Pink: ", B), "users and behaviour; Sheet 1 lands in LISTENING_BEHAVIOR"],
        [("Blue: ", B), "songs, playlists, Netflix titles"], [("Green: ", B), "AI model data and logs"],
        [("1 / N: ", B), "one-to-many"], [("Bridges: ", B), "LISTENING_BEHAVIOR and PLAYLIST_SONGS resolve "
                                                       "many-to-many"]], size=11)

    # ================================================================== 25 Mapping to brief
    s = d.base("Every attribute in the brief has a home in the model",
               "Required entities and attributes mapped to tables and columns")
    rows = [["Brief entity", "Attribute", "Table.column in the ER diagram"],
            [("Users", B), "User ID / Name", "USERS.user_id / USERS.name"],
            ["", "Subscription Plan", "USERS.plan_id → SUBSCRIPTION_PLANS"],
            ["", "Watch History", "WATCH_HISTORY (user_id, title_id) → NETFLIX_TITLES"],
            ["", "Listening Behavior", "LISTENING_BEHAVIOR (Sheet 1: plays, skips, rating, minutes)"],
            [("Songs and Playlists", B), "Song ID / Genre", "SONGS.song_id / SONGS.genre"],
            ["", "Artist", "SONGS.artist_id → ARTISTS"],
            ["", "AI Recommendation Score", "RECOMMENDATION_LOGS.ai_recommendation_score"],
            ["", "Playlist ID", "PLAYLISTS.playlist_id, PLAYLIST_SONGS (playlist_id, song_id)"],
            [("AI Model Data", B), "Model Version", "AI_MODELS.model_version"],
            ["", "Training Dataset", "AI_MODELS.training_dataset_id → TRAINING_DATASETS"],
            ["", "Recommendation Logs", "RECOMMENDATION_LOGS (user, song, model, score, rank, action)"]]
    hl = {1: PINK, 2: PINK, 3: PINK, 4: PINK, 5: RGBColor(0xEE, 0xF2, 0xF7), 6: RGBColor(0xEE, 0xF2, 0xF7),
          7: RGBColor(0xEE, 0xF2, 0xF7), 8: RGBColor(0xEE, 0xF2, 0xF7), 9: RGBColor(0xEE, 0xF6, 0xEE),
          10: RGBColor(0xEE, 0xF6, 0xEE), 11: RGBColor(0xEE, 0xF6, 0xEE)}
    d.table(s, 0.6, 1.62, [2.6, 3.2, 6.33], rows, size=12, row_h=0.43, highlight=hl)

    # ================================================================== 26 Design decisions
    s = d.base("Six design decisions behind the model",
               "Why the diagram looks the way it does")
    dec = [("Bridge tables for many-to-many", "LISTENING_BEHAVIOR links users and songs; PLAYLIST_SONGS links "
            "playlists and songs."),
           ("The score belongs to the log", "A score is for one user, one song, one model version, so it lives "
            "in RECOMMENDATION_LOGS, not in SONGS."),
           ("Watch-to-listen bridge", "SONGS.source_title_id ties soundtracks to Netflix titles: the "
            "differentiator, as a foreign key."),
           ("Consent is data", "USERS.personalization_consent gates any query that joins watch history."),
           ("Third normal form", "Plans and artists have their own tables: no repeated groups, no update "
            "anomalies."),
           ("Model lineage", "Every recommendation traces to a model version and its training dataset, for "
            "audits and rollback.")]
    for i, (t, body) in enumerate(dec):
        x, y = 0.6 + (i % 3) * 4.1, 1.7 + (i // 3) * 2.6
        d.card(s, x, y, 3.93, 2.42, t, body, size=13)

    # ================================================================== 27 Mapping + DDL
    s = d.base("From Sheet 1 to SQL", "Sheet 1 columns become LISTENING_BEHAVIOR; scores land in "
               "RECOMMENDATION_LOGS", source="code/src/database.py (SQLite)")
    rows = [["Sheet 1 column", "Column in the database"], ["User_ID", "listening_behavior.user_id (FK users)"],
            ["Song_ID", "listening_behavior.song_id (FK songs)"], ["Genre", "songs.genre"],
            ["Play_Count", "listening_behavior.play_count"], ["Skip_Rate", "listening_behavior.skip_rate"],
            ["User_Rating", "listening_behavior.user_rating"],
            ["Listening_Duration (mins)", "listening_behavior.listening_minutes"],
            [("Derived: AI score", R), "recommendation_logs.ai_recommendation_score"]]
    d.table(s, 0.6, 1.65, [2.2, 3.95], rows, size=11, row_h=0.5)
    ddl = ("CREATE TABLE listening_behavior (\n"
           "  user_id   INTEGER NOT NULL REFERENCES users(user_id),\n"
           "  song_id   TEXT    NOT NULL REFERENCES songs(song_id),\n"
           "  play_count INTEGER NOT NULL CHECK (play_count >= 0),\n"
           "  skip_rate  REAL CHECK (skip_rate BETWEEN 0 AND 1),\n"
           "  user_rating REAL CHECK (user_rating BETWEEN 1 AND 5),\n"
           "  listening_minutes INTEGER,\n"
           "  PRIMARY KEY (user_id, song_id));\n\n"
           "CREATE TABLE recommendation_logs (\n"
           "  rec_id  INTEGER PRIMARY KEY AUTOINCREMENT,\n"
           "  user_id INTEGER NOT NULL REFERENCES users(user_id),\n"
           "  song_id TEXT NOT NULL REFERENCES songs(song_id),\n"
           "  model_version TEXT NOT NULL\n"
           "        REFERENCES ai_models(model_version),\n"
           "  ai_recommendation_score REAL NOT NULL,\n"
           "  rank_position INTEGER, served_at TIMESTAMP,\n"
           "  user_action TEXT);")
    d.code(s, 6.9, 1.65, 5.83, 5.2, ddl, size=11, title="DDL excerpt (12 tables in total)")

    # ================================================================== 28 Correlations
    c = corr
    s = d.base("What the data says: skips predict dislike; popularity does not predict love",
               "Correlation between the four behaviour columns (n = 10)", source="CEP_Dataset.xlsx, Sheet 1")
    d.image(s, FIG / "correlation_heatmap.png", 0.6, 1.6, 5.6, 5.3)
    d.card(s, 6.6, 1.7, 6.13, 1.55, f"Plays and minutes move together (r = {c.loc['play_count', 'listening_minutes']})",
           "They measure nearly the same thing. Weight them together, not as two independent votes.", size=13)
    d.card(s, 6.6, 3.4, 6.13, 1.55, f"Skips are the honest negative (r = {c.loc['skip_rate', 'user_rating']})",
           "Songs skipped more are rated lower. Skip rate is the fastest feedback signal we get.", size=13,
           fill=PINK)
    d.card(s, 6.6, 5.1, 6.13, 1.55, f"Plays barely relate to rating (r = {c.loc['play_count', 'user_rating']})",
           "Most-played is not best-loved. Rank on satisfaction, not raw popularity.", size=13)

    # ================================================================== 29 Skip vs rating
    s = d.base("Three genres cross the skip-risk line", "Skip rate against rating; bubble size is play count",
               source="CEP_Dataset.xlsx, Sheet 1")
    d.image(s, FIG / "skip_vs_rating.png", 0.6, 1.55, 7.6, 5.35)
    risk = scored[scored.skip_rate >= 0.20].sort_values("skip_rate", ascending=False)
    d.card(s, 8.5, 1.7, 4.23, 2.6, "At risk: skip rate of 0.20 or more",
           [f"{r.genre}: skip {r.skip_rate:.2f}, rating {r.user_rating}" for r in risk.itertuples()] +
           ["Action: demote in ranking, re-check genre and mood tags"], size=12.5, bullets=True, fill=PINK)
    d.card(s, 8.5, 4.45, 4.23, 2.25, "Niche delight: Classical",
           ["Lowest skip (0.05) and top rating (5.0), but fewest plays (10).",
            "Action: surface to focus and calm-mood listeners"], size=12.5, bullets=True)

    # ================================================================== 30 AI score
    s = d.base("A baseline AI Recommendation Score from Sheet 1",
               "Model v1.0: a transparent weighted score that the ML model (v2) must beat",
               source="code/src/analysis.py; CEP_Dataset.xlsx, Sheet 1")
    d.rect(s, 0.6, 1.65, 4.6, 5.2, PANEL)
    d.text(s, 0.8, 1.8, 4.2, 0.3, "FORMULA (EACH INPUT MIN-MAX SCALED 0 TO 1)", size=10.5, bold=True, color=RED)
    d.text(s, 0.8, 2.2, 4.2, 2.1, [[("Score = ", B)], "0.30 × play count", "+ 0.25 × listening minutes",
                                    "+ 0.25 × user rating", "+ 0.20 × (1 − skip rate)"],
           size=15, spacing=0.3)
    d.text(s, 0.8, 4.35, 4.2, 2.4, [[("Why these weights: ", B), "repeat plays are the strongest revealed "
           "preference; minutes and rating confirm it; skips subtract."],
           [("Top 3: ", R), ", ".join(f"{r.genre} {r.ai_recommendation_score:.2f}" for r in top3.itertuples())]],
           size=12.5)
    d.image(s, FIG / "ai_score_by_song.png", 5.45, 1.6, 7.3, 5.3)

    # ================================================================== 31 Minutes per play
    s = d.base("Listening depth: Classical and Reggae hold attention longest",
               "Minutes per play shows which genres suit long, background sessions",
               source="CEP_Dataset.xlsx, Sheet 1")
    d.image(s, FIG / "minutes_per_play.png", 0.6, 1.55, 7.6, 5.35)
    d.card(s, 8.5, 1.7, 4.23, 2.4, "Long sessions",
           "Classical (7.5) and Reggae (7.3) minutes per play suit focus, work and relax playlists, the Casual "
           "Listener persona's need.", size=13)
    d.card(s, 8.5, 4.3, 4.23, 2.4, "Short bursts",
           "Pop (4.8) plays are short and frequent: good for discovery mixes and quick “Because you "
           "watched” moments.", size=13)

    # ================================================================== 32 SQL results
    s = d.base("SQL on the model: top picks and segments", "Two of the six analysis queries, run in SQLite",
               source="output/database/netflix_music.sql and netflix_music.db")
    t1, q1, c1, r1 = results["Q1"]
    t3, q3, c3, r3 = results["Q3"]
    d.code(s, 0.6, 1.6, 6.0, 1.95, q1, size=10, title="Q1  " + t1)
    d.table(s, 0.6, 3.65, [1.3, 1.6, 1.6, 1.5], [c1] + [[f'{v:.2f}' if isinstance(v, float) else str(v) for v in row] for row in r1], size=11,
            row_h=0.36, col_align=[PP_ALIGN.CENTER] * 4)
    d.code(s, 6.85, 1.6, 5.88, 2.45, q3, size=9.5, title="Q3  " + t3)
    d.table(s, 6.85, 4.15, [1.2, 2.0, 1.3, 1.38], [c3] + [[str(v) for v in row] for row in r3][:6], size=10.5,
            row_h=0.36, col_align=[PP_ALIGN.CENTER] * 4)
    d.text(s, 6.85, 6.7, 5.9, 0.3, "Showing 6 of 10 rows. Plans are placeholders: Sheet 1 has no plan column.",
           size=9.5, color=INK2)

    # ================================================================== 33 Segments
    s = d.base("Three listening segments, three product responses",
               "Segments from play count (Query 3), used alongside the personas from the earlier project")
    seg = scored.groupby("segment").agg(users=("user_id", lambda x: ", ".join(map(str, sorted(x)))),
                                        genres=("genre", lambda x: ", ".join(x)))
    segs = [("Power", "30+ plays", "AI DJ, early access to Netflix exclusives, deeper cuts"),
            ("Regular", "20 to 29 plays", "“Because you watched” mixes after each series finale"),
            ("Casual", "Under 20 plays", "Mood and background playlists with one-tap start")]
    for i, (n, rule, act) in enumerate(segs):
        x = 0.6 + i * 4.1
        d.rect(s, x, 1.7, 3.93, 4.25, PINK if i == 0 else PANEL)
        d.text(s, x + 0.2, 1.85, 3.5, 0.3, rule.upper(), size=10.5, bold=True, color=RED)
        d.text(s, x + 0.2, 2.2, 3.5, 0.5, n + " listeners", size=20, bold=True)
        d.text(s, x + 0.2, 2.85, 3.5, 0.9, [[("Users: ", B), seg.loc[n, "users"]],
                                            [("Genres: ", B), seg.loc[n, "genres"]]], size=12.5)
        d.text(s, x + 0.2, 4.2, 3.5, 0.3, "PRODUCT RESPONSE", size=10.5, bold=True, color=INK2)
        d.text(s, x + 0.2, 4.5, 3.5, 1.3, act, size=13)
    d.text(s, 0.6, 6.15, 12.1, 0.7, [[("Segments vs personas: ", B), "segments describe how much people listen; "
           "the earlier personas (Binge-Watcher, Casual Listener, Regional Listener) describe why. Targeting "
           "uses both."]], size=12.5)

    # ================================================================== PART 4
    d.section("Part 4  |  Task 3", "GenAI model selection: OpenAI vs Gemini",
              "Cost, latency, token limits, accuracy, ethics and data privacy")

    # ================================================================== 35 Use cases
    s = d.base("Where GenAI fits in Netflix Music", "Five use cases, each with a different demand on the model")
    rows = [["Use case", "Example", "Latency need", "Volume", "Context need"],
            ["AI DJ narration", "“After that finale, here is the score that played under it…”",
             ("High", R), "Medium", "Short"],
            ["Playlist titles and descriptions", "“Midnight Chase: songs from the series you just finished”",
             "Low (batch)", ("Very high", R), "Short"],
            ["Conversational search", "“Music like the rooftop scene in episode 4”", ("High", R), "High",
             "Medium"],
            ["Podcast and behind-the-scenes summaries", "Chapters and summaries for exclusive audio",
             "Low (batch)", "Low", ("Long", R)],
            ["Metadata enrichment", "Mood and theme tags for new exclusive tracks", "Low (batch)", "Medium",
             "Short"]]
    d.table(s, 0.6, 1.65, [3.0, 4.6, 1.55, 1.45, 1.53], rows, size=12, row_h=0.72, bold_first_col=True)
    d.text(s, 0.6, 6.15, 12.1, 0.7, [[("Not a GenAI job: ", R), "ranking songs. The recommender stays classical "
           "ML (Part 1). GenAI is the voice and the words around the music."]], size=13)

    # ================================================================== 36 Constraints
    s = d.base("Requirements and constraints for the model",
               "What the chosen model must satisfy (targets set for this evaluation)")
    req = [("Cost", "At most $0.10 per monthly active user per month for all GenAI features"),
           ("Latency", "First token under 3 s for live features; streamed output for the AI DJ"),
           ("Token limit", "Long transcripts and catalog context in one call; 128K+ context"),
           ("Accuracy", "No invented facts about artists, songs or shows; grounded on Netflix catalog data"),
           ("Data privacy", "No personal data in prompts; watch history only with opt-in; no training on our data"),
           ("Ethics", "Disclose AI voices and text; no artist voice cloning; fair exposure; kids profiles "
            "excluded")]
    for i, (t, body) in enumerate(req):
        x, y = 0.6 + (i % 3) * 4.1, 1.7 + (i // 3) * 2.6
        d.card(s, x, y, 3.93, 2.42, t, body, size=16)

    # ================================================================== 37 Candidates
    s = d.base("The candidates: compare like with like",
               "Workhorse against workhorse, flagship against flagship",
               source="OpenAI API pricing and models pages; Google Gemini API pricing page (read 17 Nov 2026); "
                      "Requesty latency data (11 Nov 2026); Artificial Analysis AA-Omniscience v1.1")
    mdl = A.MODELS
    rows = [["Vendor", "Model", "Tier", "Input $/1M", "Output $/1M", "Context", "First token", "Hallucination"]]
    for r in mdl.itertuples():
        rows.append([r.vendor, r.model, r.tier, f"${r.input_usd:.2f}", f"${r.output_usd:.2f}", r.context,
                     f"{r.ttft_s:.2f} s", f"{r.aa_hallucination:.1f}%" if r.aa_hallucination == r.aa_hallucination
                     and r.aa_hallucination is not None else "n/a"])
    ca = [None, None, None] + [PP_ALIGN.CENTER] * 5
    d.table(s, 0.6, 1.65, [1.1, 3.4, 1.35, 1.25, 1.3, 1.1, 1.25, 1.38], rows, size=11.5, row_h=0.52,
            col_align=ca, highlight={1: PINK, 4: RGBColor(0xEE, 0xEE, 0xEE)})
    d.text(s, 0.6, 5.95, 12.1, 0.9, [[("Short-listed: ", B), "GPT-6.1 Terra vs Gemini 3.8 Flash for volume "
           "work; GPT-6.1 Sol vs Gemini 4 Argon for hard queries. Low-cost tiers (Luna, Flash-Lite) are noted "
           "for very simple tasks."]], size=12.5)

    # ================================================================== 38 Cost
    s = d.base("Cost and computational efficiency",
               "Gemini Flash is cheaper today, but its price doubles on 1 January 2027",
               source="OpenAI and Google pricing pages, read 17 Nov 2026 (standard tier, per 1M tokens)")
    rows = [["", "GPT-6.1 Terra", "Gemini 3.8 Flash", "GPT-6.1 Sol", "Gemini 4 Argon"],
            ["Input / output (now)", "$1.00 / $5.00", "$0.75 / $3.75", "$2.00 / $10.00", "$2.00 / $10.00"],
            ["Input / output (2027)", ("$1.00 / $5.00", B), ("$1.50 / $7.50", R), "$2.00 / $10.00",
             ("$4.00 / $20.00", R)],
            ["Cached input", "$0.05", "$0.075 → $0.15", "$0.10", "$0.10 → $0.20"],
            ["Batch discount", "50%", "50%", "50%", "50%"],
            ["Long-context surcharge", "Input doubles above 272K", "None (flat to 1M)", "Input doubles above "
             "272K", "None"]]
    ca = [None] + [PP_ALIGN.CENTER] * 4
    d.table(s, 0.6, 1.65, [2.8, 2.33, 2.33, 2.33, 2.34], rows, size=12, row_h=0.55, bold_first_col=True,
            col_align=ca)
    d.card(s, 0.6, 5.15, 6.0, 1.65, "Computational efficiency", "Prompt caching cuts repeat context by 90-95% "
           "on both. Nightly playlist copy runs in batch at half price.", size=12.5)
    d.card(s, 6.73, 5.15, 6.0, 1.65, "Verdict on cost", "Gemini wins for the next six weeks. From 2027 "
           "Terra is 33% cheaper than Flash at the same workhorse tier.", size=12.5, fill=PINK)

    # ================================================================== 39 Latency
    s = d.base("Latency: OpenAI's workhorse answers first",
               "Median time to first token and output speed from production traffic",
               source="Requesty, GPT vs Claude vs Gemini API price and latency (11 Nov 2026)")
    lat = [["Model", "Median first token", "Output speed", "Fit for live features"],
           ["GPT-6 Luna", "1.91 s", "113 tokens/s", "Simple tasks only (low accuracy)"],
           [("GPT-6.1 Terra", B), ("2.76 s", R), "128 tokens/s", ("Yes: AI DJ, search", R)],
           ["Gemini 3.8 Flash", "3.58 s", "105 tokens/s", "Borderline against the 3 s target"],
           ["GPT-6.1 Sol", "4.04 s", "71 tokens/s", "Complex queries, async"],
           ["Gemini 4 Argon", "7.67 s", "84 tokens/s", "Too slow for live use"],
           ["Gemini 3.5 Flash-Lite", "0.81 s", "361 tokens/s", "Fastest; for autocomplete-style tasks"]]
    ca = [None, PP_ALIGN.CENTER, PP_ALIGN.CENTER, None]
    d.table(s, 0.6, 1.65, [3.0, 2.3, 2.1, 4.73], lat, size=12.5, row_h=0.56, col_align=ca, highlight={2: PINK})
    d.text(s, 0.6, 5.85, 12.1, 1.0, [[("Reading this fairly: ", B), "Google has the single fastest model "
           "(Flash-Lite). Among workhorse models that are accurate enough for the AI DJ, GPT-6.1 Terra is about "
           "0.8 s faster to first token and 22% faster to stream."]], size=12.5)

    # ================================================================== 40 Tokens
    s = d.base("Token limits: both are ample; pricing at length differs",
               "Context window and output limits for the short-listed models",
               source="OpenAI models page; Google Gemini API pricing and models pages (read 17 Nov 2026)")
    rows = [["", "GPT-6.1 Terra / Sol", "Gemini 3.8 Flash / 4 Argon"],
            ["Context window", "1.05M tokens", "1,048,576 tokens"],
            ["Maximum output", "128K tokens", "Not confirmed in sources reviewed"],
            ["Price beyond 272K / 200K input", "Input price doubles, output 1.5x", ("Flat across the window", R)],
            ["What fits in one call", "A full podcast season of transcripts", "A full podcast season of transcripts"]]
    d.table(s, 0.6, 1.65, [3.4, 4.36, 4.37], rows, size=13, row_h=0.62, bold_first_col=True)
    d.card(s, 0.6, 4.95, 6.0, 1.85, "What Netflix Music needs", "Most calls are under 5K tokens (playlist copy, "
           "DJ lines). Long context matters only for podcast summaries, which run in batch.", size=12.5)
    d.card(s, 6.73, 4.95, 6.0, 1.85, "Verdict on tokens", "A tie on capacity. Gemini is cheaper for very long "
           "prompts, so it scores higher on this criterion (5 vs 4).", size=12.5, fill=PINK)

    # ================================================================== 41 Accuracy
    s = d.base("Accuracy: Gemini Flash knows a little more; Terra invents much less",
               "Two independent benchmarks, and why we will also run our own",
               source="Artificial Analysis AA-Omniscience v1.1 (read 1 Nov 2026); Vectara Hallucination "
                      "Leaderboard (22 Oct 2026)")
    rows = [["Model", "Accuracy (AA)", "Hallucination when wrong (AA)", "Grounded summary hallucination (Vectara)"],
            [("GPT-6.1 Terra", B), "47.6%", ("34.5%", R), "not listed"],
            ["Gemini 3.8 Flash", "50.5%", "55.1%", "not listed"],
            ["GPT-6.1 Sol", "61.8%", "51.9%", "6.5% (GPT-6 Sol)"],
            ["Gemini 4 Argon", "not captured", "4.3%", "12.1%"]]
    ca = [None, PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.CENTER]
    d.table(s, 0.6, 1.65, [2.8, 2.4, 3.3, 3.63], rows, size=12.5, row_h=0.56, col_align=ca, highlight={1: PINK})
    d.card(s, 0.6, 4.65, 3.93, 2.15, "Workhorse tier", "Terra's lower hallucination matters more than Flash's "
           "3-point accuracy edge: a wrong artist fact is worse than “I don't know”.", size=12)
    d.card(s, 4.7, 4.65, 3.93, 2.15, "Flagship tier", "Argon is very cautious on closed-book facts; Sol is "
           "better grounded in summaries. The leaderboards disagree.", size=12)
    d.card(s, 8.8, 4.65, 3.93, 2.15, "Our own test", "Before signing, run 500 real prompts grounded on the "
           "Netflix catalog and score facts, tone and safety.", size=12, fill=PINK)

    # ================================================================== 42 Chart
    s = d.base("Head to head on the workhorse tier",
               "GPT-6.1 Terra vs Gemini 3.8 Flash on the three measurable criteria",
               source="Pricing pages (17 Nov 2026); Requesty (11 Nov 2026); AA-Omniscience v1.1 (1 Nov 2026)")
    d.image(s, FIG / "genai_comparison.png", 0.6, 1.6, 12.13, 4.4)
    d.text(s, 0.6, 6.15, 12.1, 0.7, [[("Read across: ", B), "Gemini is cheaper only until 31 December 2026. "
           "Terra is faster to first token and hallucinates about 20 points less."]], size=13)

    # ================================================================== 43 Ethics & privacy
    s = d.base("Ethics and data privacy", "Vendor terms compared, plus the guardrails Netflix Music adds "
               "whichever model it picks", source="OpenAI API data usage policy; Google Gemini API pricing page "
                                                 "(“used to improve our products” row)")
    rows = [["", "OpenAI API", "Google Gemini API"],
            ["Training on our data", "Not by default for API business data", "Free tier: yes. Paid: varies by "
             "model; some marked “used to improve products”"],
            ["Enterprise route", "OpenAI API or Azure OpenAI", "Vertex AI on Google Cloud"],
            ["Data residency", "Regional endpoints (+10% price)", "Regional processing on Vertex AI"],
            ["Cloud fit (Netflix on AWS)", "Cross-cloud API call", "Cross-cloud API call"]]
    d.table(s, 0.6, 1.62, [2.8, 4.4, 4.93], rows, size=11.5, row_h=0.52, bold_first_col=True)
    gr = ["Opt-in before watch history shapes music", "No personal data in prompts: IDs and genres only",
          "AI DJ voice and AI text are labelled", "No cloning of real artists' voices",
          "Fair exposure for independent artists in re-ranking", "Kids profiles excluded from GenAI features"]
    d.rect(s, 0.6, 4.4, 12.13, 2.45, PINK)
    d.text(s, 0.8, 4.52, 11.7, 0.3, "NETFLIX MUSIC GUARDRAILS (APPLY TO EITHER VENDOR)", size=11, bold=True, color=RED)
    for i, g in enumerate(gr):
        d.text(s, 0.8 + (i % 2) * 5.95, 4.95 + (i // 2) * 0.6, 5.8, 0.5,
               [[("✓  ", R), g]], size=13)

    # ================================================================== 44 Decision matrix
    s = d.base(f"Decision matrix: OpenAI {totals['openai']:.2f} vs Gemini {totals['gemini']:.2f}",
               "Six weighted criteria (scores 1 to 5); OpenAI wins four, Gemini wins one, one tie",
               source="code/src/analysis.py (CRITERIA); evidence from the previous slides")
    rows = [["Criterion", "Weight", "OpenAI", "Gemini"]]
    for r in dm.itertuples():
        rows.append([r.criterion, f"{int(r.weight * 100)}%", f"{r.openai:g}", f"{r.gemini:g}"])
    rows.append([("Weighted total", B), "100%", (f"{totals['openai']:.2f}", R), (f"{totals['gemini']:.2f}", B)])
    ca = [None, PP_ALIGN.CENTER, PP_ALIGN.CENTER, PP_ALIGN.CENTER]
    d.table(s, 0.6, 1.65, [3.75, 1.0, 1.0, 1.0], rows, size=13, row_h=0.6, col_align=ca,
            highlight={len(rows) - 1: PINK})
    d.kpi(s, 7.65, 1.65, 2.45, 1.3, f"{totals['openai']:.2f}", "OpenAI weighted score", fill=PINK)
    d.kpi(s, 10.28, 1.65, 2.45, 1.3, f"{totals['gemini']:.2f}", "Gemini weighted score", vcolor=INK2)
    d.card(s, 7.65, 3.1, 5.08, 1.75, "Where each wins", [
        [("OpenAI: ", B), "cost from 2027, latency, accuracy, privacy"],
        [("Gemini: ", B), "token limit (flat long-context price)"],
        [("Tie: ", B), "scalability and integration"]], size=12.5)
    d.card(s, 7.65, 5.0, 5.08, 1.85, "Sensitivity checks", [
        f"Gemini keeps its 2026 promo price: {totals['gemini_if_promo_price_kept']:.2f}",
        f"Cost weighted 40%: OpenAI {totals['openai_if_cost_40pct']:.2f}, Gemini "
        f"{totals['gemini_if_cost_40pct']:.2f}", "OpenAI leads in every case"], size=12.5, bullets=True)

    # ================================================================== 45 Cost at scale
    s = d.base("Cost at scale: about 8 cents per listener per month",
               "Monthly GenAI API cost under one usage scenario (planning assumption)",
               source="code/src/analysis.py (USAGE, cost_model); list prices read 17 Nov 2026")
    d.image(s, FIG / "genai_cost_model.png", 0.6, 1.55, 7.9, 4.6)
    u = A.USAGE
    d.card(s, 8.75, 1.7, 3.98, 3.0, "Assumptions",
           [f"{u['mau'] / 1e6:.0f}M monthly active users", f"{u['calls_per_user_month']} GenAI calls per user "
            f"per month", f"{u['input_tokens']:,} input tokens per call, {int(u['cached_share'] * 100)}% cached",
            f"{u['output_tokens']} output tokens per call"], size=12, bullets=True)
    d.card(s, 8.75, 4.85, 3.98, 1.95, "Result", f"Recommended mix: ${mix.monthly_usd / 1000:,.0f}K a month, "
           f"${mix.per_mau_usd:.3f} per user: inside the $0.10 target.", size=12.5, fill=PINK)
    d.text(s, 0.6, 6.3, 7.9, 0.6, f"Gemini 3.8 Flash costs ${flash.monthly_usd / 1000:,.0f}K now but "
           f"${flash27.monthly_usd / 1000:,.0f}K from January 2027.", size=11.5, color=INK2)

    # ================================================================== 46 Recommendation
    s = d.base("Recommendation: OpenAI, behind a model gateway",
               "Pick the best model now and keep the option to switch")
    d.rect(s, 0.6, 1.65, 12.13, 1.25, PINK)
    d.text(s, 0.85, 1.75, 11.7, 1.1, [[("Choose OpenAI. ", R), ("GPT-6.1 Terra", B), " for AI DJ lines, "
           "playlist copy and search (about 85% of calls); ", ("GPT-6.1 Sol", B), " for complex conversational "
           "requests (about 15%); the Batch API for nightly playlist copy."]], size=15, anchor=MSO_ANCHOR.MIDDLE)
    why = [("Faster", "2.76 s first token meets the 3 s live-feature target; Flash does not"),
           ("Safer", "34.5% vs 55.1% hallucination: fewer invented artist facts"),
           ("Predictable", "Stable list price; Gemini Flash doubles in January 2027"),
           ("Fits the guardrails", "API data not used for training by default")]
    for i, (t, body) in enumerate(why):
        x = 0.6 + i * 3.07
        d.card(s, x, 3.1, 2.9, 1.9, t, body, size=12.5)
    d.text(s, 0.6, 5.2, 12.1, 0.3, "RISKS AND MITIGATIONS", size=11, bold=True, color=RED)
    d.bullets(s, 0.6, 5.5, 12.1, 1.4, [
        ("Lock-in:", "a model gateway makes the vendor a setting; Gemini Flash-Lite is the tested fallback."),
        ("Benchmarks age fast:", "a 4-week bake-off on 500 catalog-grounded prompts before contract; re-run "
         "every quarter."),
        ("Cost drift:", "per-feature budgets, caching and alerts at $0.10 per user.")], size=12.5, spacing=0.3)

    # ================================================================== PART 5
    d.section("Part 5  |  Task 4", "Agile workflow and the Trello board",
              "Kanban for flow, sprints for rhythm, WSJF for priority, using Sheet 2 - Sprint Tasks")

    # ================================================================== 48 Operating model
    s = d.base("Agile operating model: Scrum-ban", "Two-week sprints for rhythm, a Kanban board for flow")
    d.card(s, 0.6, 1.7, 3.93, 5.1, "Roles", [
        [("Product Manager / PO: ", B), "owns backlog and WSJF scores"],
        [("Scrum Master: ", B), "runs ceremonies, guards WIP"],
        [("Engineers (10): ", B), "app, backend, data, ML, QA"],
        [("Stakeholders: ", B), "Netflix content, legal, privacy"]], size=14.5)
    d.card(s, 4.7, 1.7, 3.93, 5.1, "Ceremonies", [
        [("Sprint planning ", B), "(day 1): pull top WSJF cards"],
        [("Daily stand-up: ", B), "walk the board right to left"],
        [("Backlog refinement ", B), "(weekly): re-score WSJF"],
        [("Review / demo: ", B), "show working software"],
        [("Retrospective: ", B), "one improvement per sprint"]], size=14.5)
    d.card(s, 8.8, 1.7, 3.93, 5.1, "Ready and done", [
        [("Definition of Ready: ", B), "owner, priority label, acceptance criteria, WSJF score"],
        [("Definition of Done: ", B), "code reviewed, tests pass, Postman checks green, metrics dashboard "
                                      "updated, PM accepted"]], size=14.5, fill=PINK)

    # ================================================================== 49 Sheet 2 insights
    sp = tsum["status_priority"]
    s = d.base("Sheet 2 shows a team busy on the right things, with one gap",
               "10 tasks by status and priority", source="CEP_Dataset.xlsx, Sheet 2 - Sprint Tasks")
    d.image(s, FIG / "sprint_status_priority.png", 0.6, 1.55, 6.9, 4.1)
    d.kpi(s, 0.6, 5.8, 2.2, 1.05, f"{tsum['completion_rate']}%", "tasks completed")
    d.kpi(s, 2.95, 5.8, 2.2, 1.05, f"{tsum['high_share_in_progress']}%", "of in-progress work is High")
    d.kpi(s, 5.3, 5.8, 2.2, 1.05, f"{int(sp.loc['Backlog', 'High'])}", "High task still in Backlog")
    d.card(s, 7.8, 1.7, 4.93, 1.6, "Focus is right", "3 of 4 in-progress tasks are High: AI playlist "
           "generation, streaming buffer fix, bug fixes and tuning.", size=12.5)
    d.card(s, 7.8, 3.45, 4.93, 1.6, "The gap", f"{tsum['high_in_backlog'][0]} is High but not started. "
           "Watch-history data cannot launch without it.", size=12.5, fill=PINK)
    d.card(s, 7.8, 5.2, 4.93, 1.6, "Capacity", "One owner per task, nobody double-booked. Ten people, "
           "four in-flight tasks: room to pull two more.", size=12.5)

    # ================================================================== 50 WSJF
    s = d.base("Backlog prioritization with WSJF",
               "Weighted Shortest Job First = cost of delay ÷ job size (relative Fibonacci estimates)",
               source="code/src/analysis.py (WSJF_INPUTS); estimates are team planning assumptions")
    names = dict(zip(ctx["board"].task_id, ctx["board"].task_name))
    rows = [["Rank", "Card", "BV", "TC", "RR", "Size", "WSJF", "Why"]]
    for r in wsjf.itertuples():
        rows.append([f"#{r.backlog_rank}", f"{r.card}  {names[r.card]}", str(r.business_value),
                     str(r.time_criticality), str(r.risk_reduction), str(r.job_size), f"{r.wsjf:.2f}", r.rationale])
    ca = [PP_ALIGN.CENTER, None] + [PP_ALIGN.CENTER] * 5 + [None]
    d.table(s, 0.6, 1.65, [0.7, 3.55, 0.55, 0.55, 0.55, 0.65, 0.8, 4.78], rows, size=11, row_h=0.52,
            col_align=ca, highlight={1: PINK, 2: PINK})
    d.text(s, 0.6, 6.05, 12.1, 0.8, [[("Dependency rule: ", B), "N02 Dataset preparation ranks above N03 User "
           "segmentation (4.20 vs 4.33) because segments are built from the prepared data. BV business value, "
           "TC time criticality, RR risk reduction."]], size=12)

    # ================================================================== 51 Trello board
    s = d.base("The Trello Kanban board", "Backlog, In Progress and Completed, as the brief specifies; "
               "17 cards", source="output/trello_cards.csv; board rendered from Sheet 2 plus brief cards")
    d.image(s, FIG / "trello_kanban_board.png", 0.45, 1.55, 8.95, 5.35)
    d.card(s, 9.55, 1.65, 3.18, 5.2, "Reading the board", [
        [("Lists: ", B), "Backlog, In Progress, Completed, exactly as the brief asks"],
        [("Labels: ", B), "High, Medium, Low from Sheet 2"],
        [("Backlog order: ", B), "WSJF rank, top card is pulled next"],
        [("WIP: ", R), "In Progress holds 6 against a limit of 5. Finish T003 and T010 before pulling new work"],
        [("N cards: ", B), "the 7 tasks named in the brief"]], size=11.5)

    # ================================================================== 52 Trello setup
    s = d.base("Setting up the board in Trello", "Lists, labels, cards and automation (as in the Lesson 5 demo)")
    steps = [("1  Create the board", "“Netflix Music: AI Recommendations” with lists Backlog, "
              "In Progress, Completed"),
             ("2  Add labels", "High (red), Medium (amber), Low (green), from Sheet 2's Priority column"),
             ("3  Add 17 cards", "10 from Sheet 2 and 7 from the brief; members from Assigned_Team_Member"),
             ("4  Card template", "Description, acceptance criteria, DoD checklist, due date, WSJF custom field"),
             ("5  Order the backlog", "Sort Backlog by WSJF rank; top of the list is the next pull"),
             ("6  Automate (Butler)", "Card moved to Completed: mark due date done. In Progress over 5 cards: "
              "post a WIP warning")]
    for i, (t, body) in enumerate(steps):
        x, y = 0.6 + (i % 2) * 6.13, 1.7 + (i // 2) * 1.72
        d.rect(s, x, y, 6.0, 1.55, PANEL)
        d.text(s, x + 0.2, y + 0.15, 5.6, 0.4, t, size=15, bold=True, color=RED)
        d.text(s, x + 0.2, y + 0.6, 5.6, 0.9, body, size=12.5)

    # ================================================================== 53 Sprint plan
    s = d.base("Sprint plan and the feedback loop", "Finish what is in flight, then pull by WSJF")
    d.card(s, 0.6, 1.7, 3.93, 3.0, "Sprint 4 (now): finish", [
        "T001 Implement AI Playlist Gen", "T003 Fix Streaming Buffer Issues", "T010 Bug Fixes & Performance",
        "N04 AI model training (v2)", "N05 Recommendation accuracy testing",
        "T006 Backend API Optimization"], size=13.5, bullets=True)
    d.card(s, 4.7, 1.7, 3.93, 3.0, "Sprint 5 (next): pull", [
        "N01 GenAI model selection (decided in Part 4)", "T005 Data Security Review",
        "N02 Dataset preparation", "N03 User segmentation"], size=13.5, bullets=True, fill=PINK)
    d.card(s, 8.8, 1.7, 3.93, 3.0, "Sprint 6 and later", [
        "T009 Enhance User Personalization", "T008 Improve Song Metadata Analysis", "T004 UI Enhancements",
        "Re-score WSJF each refinement"], size=13.5, bullets=True)
    loop = ["Plan", "Build", "Review and demo", "Retro", "Refine backlog"]
    for i, t in enumerate(loop):
        x = 0.6 + i * 2.47
        d.box(s, x, 5.05, 2.2, 0.65, t, fill=HEAD, color=WHITE, bold=True, size=14)
        if i < 4:
            d.arrow(s, x + 2.22, 5.22, 0.23, 0.3)
    d.text(s, 0.6, 5.9, 12.1, 0.4, "Iterative feedback: review shows working software; the retro changes one "
           "process; refinement re-scores the backlog with what was learned.", size=13, color=INK2)

    # ================================================================== 54 Metrics
    s = d.base("How we know it is working", "Delivery, product and model metrics, reviewed every sprint")
    rows = [["Area", "Metric", "Target"],
            ["Delivery", "Cycle time (In Progress to Completed)", "Under 6 working days"],
            ["", "Work in progress", "5 cards or fewer"],
            ["", "Sprint goal hit rate", "80% or more"],
            ["Product", "Skip rate on recommended songs", "Below 0.15 (Sheet 1 average 0.149)"],
            ["", "Saves per 100 recommendations", "Up 20% vs baseline v1.0"],
            ["", "Listeners who start from “Because you watched”", "25% of new listeners"],
            ["Model", "NDCG@10 offline; A/B lift online", "v2 beats v1.0 before rollout"],
            ["GenAI", "First token; cost per user; flagged outputs", "Under 3 s; under $0.10; under 0.5%"]]
    d.table(s, 0.6, 1.65, [2.0, 5.6, 4.53], rows, size=12.5, row_h=0.55,
            highlight={1: PANEL, 2: PANEL, 3: PANEL, 4: WHITE, 5: WHITE, 6: WHITE, 7: PANEL, 8: WHITE})

    # ================================================================== PART 6
    d.section("Part 6", "Results", "What was delivered, what comes next and what could go wrong")

    # ================================================================== 56 Results
    s = d.base("Results against the brief", "Every expected outcome delivered, with evidence",
               source="Netflix_Music_CEP_Submission folder")
    rows = [["Expected outcome", "Delivered", "Where"],
            ["Technology stack report", "Components, NFR targets, stack table, frontend scoring, real-time "
             "design, databases, API assessment, architecture", "Slides 12-21"],
            ["Entity-relationship diagram", "12-entity model in 3NF, mapping to the brief, design decisions, "
             "working SQLite build with 6 queries", "Slides 23-33; netflix_music.db"],
            ["GenAI model selection report", "OpenAI vs Gemini on cost, latency, tokens, accuracy, ethics; "
             "decision matrix, sensitivity, cost model", "Slides 35-46"],
            ["Kanban-based Agile workflow", "Trello board design, WSJF backlog, sprint plan, setup steps, "
             "metrics; importable card list", "Slides 48-54; trello_cards.csv"],
            ["Reproducible analysis", "Python code that rebuilds every chart, table, database and this deck",
             "code/ folder"]]
    d.table(s, 0.6, 1.65, [3.0, 6.4, 2.73], rows, size=12, row_h=0.8, bold_first_col=True)

    # ================================================================== 57 Roadmap
    s = d.base("Roadmap: from foundations to the MVP launch",
               "Aligned with the earlier project's MVP target of mid-2027 (planning dates)")
    ph = [("Q4 2026", "Foundations", ["Stack and data model signed off", "GenAI bake-off", "Data Security Review"]),
          ("Q1 2027", "Build", ["v2 recommender trained", "AI playlists and watch-history discovery",
                                "Trello flow at WIP 5"]),
          ("Q2 2027", "Beta", ["Binge-Watcher beta cohort", "AI DJ in English", "Hit skip-rate and cost "
                               "targets"]),
          ("Mid-2027", "MVP launch", ["All members, opt-in watch-to-listen", "Exclusive soundtracks",
                                      "Gate: saves +20%"])]
    for i, (when, t, items) in enumerate(ph):
        x = 0.6 + i * 3.07
        d.rect(s, x, 1.75, 2.9, 0.08, RED)
        d.text(s, x, 1.95, 2.9, 0.3, when.upper(), size=11, bold=True, color=RED)
        d.text(s, x, 2.3, 2.9, 0.5, t, size=20, bold=True)
        d.rect(s, x, 2.95, 2.9, 2.45, PINK if i == 3 else PANEL)
        d.text(s, x + 0.2, 3.1, 2.5, 2.8, [[("•  ", R), it] for it in items], size=15, spacing=0.7)
    d.text(s, 0.6, 5.65, 12.1, 0.6, "Each phase ends at a gate: the next phase starts only when its metric is "
           "met.", size=14, color=INK2)

    # ================================================================== 58 Risks
    s = d.base("Key risks and how we reduce them")
    rows = [["Risk", "Likelihood", "Impact", "Mitigation"],
            ["Members object to watch history shaping music", "Medium", "High",
             "Opt-in consent, clear explanation, easy off switch"],
            ["GenAI states wrong facts about artists or shows", "Medium", "High",
             "Ground prompts on catalog data; eval set; human review of DJ scripts"],
            ["GenAI cost grows faster than usage", "Medium", "Medium", "Caching, batch, per-feature budgets, "
             "gateway to cheaper tiers"],
            ["Music licensing limits catalog", "High", "High", "Lead with soundtracks and exclusives Netflix owns"],
            ["Ten records are too few to train on", "Certain", "Medium", "Treat Sheet 1 as a design sample; train "
             "v2 on full event logs"],
            ["In Progress exceeds WIP limit", "High", "Medium", "Butler warning; swarm to finish before "
             "pulling new work"]]
    ca = [None, PP_ALIGN.CENTER, PP_ALIGN.CENTER, None]
    d.table(s, 0.6, 1.4, [4.0, 1.5, 1.3, 5.33], rows, size=12, row_h=0.72, col_align=ca, bold_first_col=True)

    # ================================================================== 59 Conclusion
    s = d.base("Conclusion", "From watching to listening, built on what Netflix already does well")
    d.bullets(s, 0.6, 1.7, 7.3, 5.0, [
        ("Stack:", "React Native, Java microservices, Kafka and a polyglot data layer on AWS: fast, scalable "
                   "and native to Netflix."),
        ("Data:", "a 12-entity model connects watch history, listening behaviour and AI decisions, with "
                  "consent and lineage built in."),
        ("Insight:", "skips are the honest signal; popularity is not satisfaction."),
        ("GenAI:", f"OpenAI ({totals['openai']:.2f} vs {totals['gemini']:.2f}) for speed, accuracy and "
                   f"predictable cost, behind a gateway."),
        ("Delivery:", "a Trello Kanban board, WSJF backlog and two-week sprints.")], size=17, spacing=0.7)
    d.rect(s, 8.3, 1.7, 4.43, 4.6, DARK)
    d.text(s, 8.6, 2.0, 3.9, 3.9, ["“How might we turn what members watch into what they love to listen "
                                   "to?”", "", "This project is the engineering answer."],
           size=22, color=WHITE, bold=True, spacing=0.3, anchor=MSO_ANCHOR.MIDDLE)

    # ================================================================== 60 Sources
    s = d.base("Appendix: sources")
    src = ["CEP_Dataset.xlsx: Sheet 1 - Music Data; Sheet 2 - Sprint Tasks (course materials)",
           "OpenAI API pricing and models pages, developers.openai.com (read 17 Nov 2026)",
           "Google Gemini Developer API pricing page, ai.google.dev (read 17 Nov 2026)",
           "Requesty, “GPT vs Claude vs Gemini: API price and latency compared” (11 Nov 2026)",
           "Artificial Analysis, AA-Omniscience v1.1 benchmark (read 1 Nov 2026, via Lotook summary)",
           "Vectara Hallucination Leaderboard, github.com/vectara/hallucination-leaderboard (22 Oct 2026)",
           "Gomez-Uribe, C. & Hunt, N. (2015). The Netflix Recommender System. ACM TMIS 6(4)",
           "Covington, P., Adams, J. & Sargin, E. (2016). Deep Neural Networks for YouTube Recommendations. RecSys",
           "Netflix Technology Blog: DGS framework, EVCache, Apache Iceberg, Metaflow, Open Connect",
           "Course materials: Lesson 1 (Postman), Lesson 2 (SQLite, CRUD), Lesson 4 (LLM comparison), "
           "Lesson 5 (Trello Kanban)",
           "Earlier project: Netflix_Music_Project_Report_v2.pptx and Netflix_Dataset.xlsx"]
    d.text(s, 0.6, 1.5, 12.1, 5.4, [[(f"{i + 1}.  ", R), t] for i, t in enumerate(src)], size=14, spacing=0.75)

    # ================================================================== 61 Assumptions
    s = d.base("Appendix: assumptions and data notes")
    d.bullets(s, 0.6, 1.5, 12.1, 5.4, [
        ("Sample size:", "Sheet 1 has 10 rows (one per user and song); correlations describe the sample, not "
                         "the market."),
        ("Sheet naming:", "the brief refers to “Sheet 3 - Sprint Tasks” in one place; the workbook's "
                          "sprint data is Sheet 2, which is used here."),
        ("Placeholders:", "names, artists, titles and plans in the SQLite build are labelled placeholders; Sheet 1 "
                          "has IDs only."),
        ("Board reading:", "the brief places deployment in Completed while training is in progress; read as "
                           "baseline v1.0 deployed and v2 in training."),
        ("Estimates:", "WSJF inputs, NFR targets, usage volumes and roadmap dates are planning assumptions."),
        ("Benchmarks:", "prices, latency and accuracy are dated snapshots (Oct-Nov 2026) and change often; "
                        "re-check before contract."),
        ("Scores:", "frontend and GenAI matrices are analyst judgement grounded in the evidence cited.")],
              size=16, spacing=1.0)

    d.save(DECK)
    return DECK, len(d.prs.slides)


if __name__ == "__main__":
    path, n = build()
    print(f"Wrote {path} ({n} slides)")
