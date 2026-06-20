# Deploying Trading AI

Two pieces:

- **Frontend** (React/Vite) → **Vercel**
- **Backend** (FastAPI) → **Render** (free web service)

> Note: Supabase can't host a Python web app — it's a database/auth service. It's
> a great *optional* upgrade later for persistent prediction history (Postgres),
> but the app itself runs on Render. Render's free tier is genuinely free; it just
> "sleeps" after ~15 min idle and takes ~50s to wake on the next request.

---

## 1. Backend on Render (do this first — you need its URL for the frontend)

1. Go to **https://render.com** and sign up (free, GitHub login works).
2. **New ➜ Blueprint** → select the `AI-Trend-Predictor` repo.
3. Render reads `render.yaml` and shows the service. It will **prompt for two secrets**:
   - `OPENAI_API_KEY` — your OpenAI key (from `backend/.env`)
   - `ANTHROPIC_API_KEY` — your Claude key (optional; leave blank to use OpenAI only)
4. Click **Apply**. First build takes ~3–5 min.
5. Copy the live URL, e.g. `https://ai-trend-predictor-api.onrender.com`.
6. Test it: open `<that URL>/assets` — you should see the asset list JSON.

## 2. Frontend on Vercel

1. Go to **https://vercel.com** → **Add New ➜ Project** → import the `AI-Trend-Predictor` repo.
2. Vercel reads `vercel.json` (builds the `frontend/` app automatically).
3. Under **Environment Variables**, add:
   - `VITE_API_URL` = your Render backend URL (e.g. `https://ai-trend-predictor-api.onrender.com`)
   - `VITE_FINNHUB_KEY` = your Finnhub key (from `frontend/.env.local`, optional — enables live forex)
4. **Deploy**. Done — your dashboard is live.

> The live candle chart streams **directly from Binance in the browser**, so crypto
> charts work even before the backend is up. The signal/prediction/report panels
> need the backend (`VITE_API_URL`).

---

## 3. Durable history (Turso / libSQL) — keeps the accuracy report alive

By default the app writes to a local `predictions.db` (SQLite). On serverless
(Vercel) and Render's free tier that file lives in ephemeral storage, so the
**accuracy report and paper-trading track record reset on every cold start /
redeploy** — which guts the self-scoring record that's the whole point.

Point the app at a free **[Turso](https://turso.tech)** (libSQL) database and
that history persists durably. No code change — same schema, same queries:

1. Install the CLI and sign up (free): `curl -sSfL https://get.tur.so/install.sh | bash`, then `turso auth signup`.
2. Create a database and a token:
   ```bash
   turso db create trading-ai
   turso db show trading-ai --url        # → libsql://trading-ai-<org>.turso.io
   turso db tokens create trading-ai     # → the auth token
   ```
3. Add these as environment variables (Vercel project → Settings → Environment
   Variables, or Render → Environment), then redeploy:
   - `TURSO_DATABASE_URL` = the `libsql://…` URL
   - `TURSO_AUTH_TOKEN`   = the token

That's it. On boot the app creates the schema in Turso and every prediction,
forecast and paper trade is written there instead of `/tmp`. If the vars are
absent or the database is unreachable, it transparently falls back to local
SQLite, so nothing breaks. (`LIBSQL_URL` / `LIBSQL_AUTH_TOKEN` work as aliases.)

---

## 4. Keep it collecting (always-on + saved history)

On Vercel the backend is serverless — it only runs when something calls it, so
nothing is saved while nobody has the site open. To keep the backend warm **and**
continuously save the analysis, hit the collector endpoint on a schedule:

    GET /_/backend/snapshot?tf=1h     → logs the current analysis for every asset
    GET /_/backend/health             → confirms it's up + shows what's been saved

`/snapshot` writes a signal snapshot + a technical prediction + the projected
next candle for all 8 assets, so the accuracy report, backtest and saved
analysis grow on their own. Review any time via the in-app **Accuracy Report**,
or the raw `GET /_/backend/signals/{symbol}` and `GET /_/backend/history/{symbol}`.

Two ways to schedule it (use either or both):

1. **Vercel Cron** — already configured in `vercel.json` (`/_/backend/broadcast`,
   daily). `/broadcast` saves the 1h snapshot for every asset **and** posts the
   Telegram signals (see §5). On the **Hobby** plan cron runs at most once/day; on
   **Pro** change the schedule to hourly (`0 * * * *`) for proper intraday work.
2. **External pinger (recommended, free, frequent)** — point
   [cron-job.org](https://cron-job.org) or [UptimeRobot](https://uptimerobot.com)
   at `https://<your-app>/_/backend/broadcast` every 15–30 min. This saves the
   history, posts due Telegram signals, **and** keeps the function warm so the
   live site never cold-starts. (Use `/_/backend/snapshot?tf=1h,4h,1d` instead if
   you only want to save more timeframes without broadcasting.)

> **Lock it down (optional):** set a `CRON_SECRET` env var, then call
> `/_/backend/snapshot?tf=1h&secret=YOUR_SECRET` (Vercel Cron sends it
> automatically). Without `CRON_SECRET` the endpoint is open.

> **Important:** continuous collection only *persists* if a durable database is
> configured (**§3**). Without Turso, every cold start still wipes the saved
> history — so set `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN` first. Check
> `GET /_/backend/health` → `"durable": true` to confirm.

---

## 5. Telegram signal-service (auto-posted to a group/channel)

The `/broadcast` pass (scheduled in §4) posts **high-conviction** directional
setups to a Telegram chat — one message per market per candle, with a rendered
candlestick chart (entry/stop/target + projected next candle). Setup:

1. **Create a bot:** message **@BotFather** → `/newbot` → pick a name + a
   `…bot` username → copy the **token** it gives you.
2. **Create the group/channel** and add your bot (as a **member** for a group, or
   an **admin** for a channel).
3. **Get the chat id:** add **@RawDataBot** to the chat briefly — it prints the
   `Chat ID` (a negative number like `-1001234567890`), then remove it. (Or open
   `https://api.telegram.org/bot<TOKEN>/getUpdates` after sending a message.)
4. **Set env vars** (Vercel → Settings → Environment Variables), then redeploy:
   - `TELEGRAM_BOT_TOKEN` = the bot token
   - `TELEGRAM_CHAT_ID`   = the chat id
5. **Test:** `GET /_/backend/notify/config` should list `telegram`; hit
   `GET /_/backend/broadcast?force=true` to post the current signals immediately
   (`force` ignores the once-per-candle dedupe). Day to day, the cron/pinger
   handles it.

Tuning: the confidence threshold is `MIN_CONFIDENCE = 75` in
`backend/engine/broadcast.py`; the same `CRON_SECRET` from §4 guards `/broadcast`.
The browser 🔔 Alerts toggle also relays signal-flip / price alerts to the same
chat (and to Discord via `DISCORD_WEBHOOK_URL`).

---

## Updating later
Push to `main` → both Render and Vercel auto-redeploy.

## Free-tier notes
- Render free sleeps after 15 min idle; first request after wake is slow (~50s).
- Without a durable database (see **§3**), `predictions.db` (SQLite) resets when
  the host redeploys/sleeps or a serverless function cold-starts. The live
  analysis, forecasts, trend, and accuracy *reconstruction* all compute from
  candles and are unaffected; only the forward-logged prediction history,
  paper-trading book, and the backtest's logged inputs reset. Set
  `TURSO_DATABASE_URL` + `TURSO_AUTH_TOKEN` to keep them permanently.
