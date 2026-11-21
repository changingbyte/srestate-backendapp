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

## Roz 2 baar (PythonAnywhere → Tasks, UTC)

| Kab (IST) | Cron (UTC) | Command |
|-----------|------------|---------|
| **9:00 AM** | `30 3 * * *` | `cd /home/princewhatsapp/srestate-backendapp && ./venv/bin/python manage.py daily_care_morning` |
| **6:00 PM** | `30 12 * * *` | `cd /home/princewhatsapp/srestate-backendapp && ./venv/bin/python manage.py daily_care_evening` |

Lead record: shared_by → assignee → contact. WhatsApp: `meri leads` | `assign 93…` | `ho gaya 3`

## Adding an area

Add the lowercase canonical area to the alphabetically sorted `area` list in
`inbox/estate_lexicon.json`; no Python or migration change is needed. Add a
common misspelling or run-together broker spelling to `aliases` with that
canonical area as its value, then add a representative parser test.
