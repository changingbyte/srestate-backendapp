# Family estate WhatsApp bot

Minimal Django 5 app: five whitelisted family numbers message one Twilio WhatsApp number. Only **real-estate** text is parsed, stored in SQLite, and searched via `query`.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# Fill Twilio + FAMILY_ALLOWED_MOBILES (5 numbers)
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver
```

Twilio Console → WhatsApp sandbox → **When a message comes in**:  
`https://<your-host>/whatsapp/inbound/`

## Commands

| Message | Action |
|---------|--------|
| `help` | Cheat sheet |
| Free text listing | Save if estate fields detected |
| `query 3bhk adajan rent` | Search archive |
| `add` + multiline blocks | Save multiple listings |

Tweak areas and property types in `inbox/estate_lexicon.json`.

## Roz schedule (PythonAnywhere → Tasks)

Server time is **UTC**. India = UTC+5:30.

| Task | Cron (UTC) | Command |
|------|------------|---------|
| Due follow-up reminders | `*/15 * * * *` | `cd /home/YOURUSER/srestate-backendapp && ./venv/bin/python manage.py run_due_followups` |
| Subah family digest | `30 3 * * *` (= **9:00 AM IST**) | `cd /home/YOURUSER/srestate-backendapp && ./venv/bin/python manage.py daily_family_digest` |

WhatsApp: `followup kal 5pm …` | `pending` | `done 3`

## Adding an area

Add the lowercase canonical area to the alphabetically sorted `area` list in
`inbox/estate_lexicon.json`; no Python or migration change is needed. Add a
common misspelling or run-together broker spelling to `aliases` with that
canonical area as its value, then add a representative parser test.
