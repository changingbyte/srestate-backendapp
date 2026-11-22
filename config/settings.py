from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

TESTING = "test" in sys.argv
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
DEBUG = os.environ.get("DEBUG", "True").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "inbox",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

(Path(BASE_DIR / "data")).mkdir(parents=True, exist_ok=True)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "data" / "family_estate.db",
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
TWILIO_VALIDATE_SIGNATURE = os.environ.get("TWILIO_VALIDATE_SIGNATURE", "False").lower() in (
    "1",
    "true",
    "yes",
)
# Exact Twilio console webhook URL (https). Required when TWILIO_VALIDATE_SIGNATURE=True on PA.
TWILIO_WEBHOOK_URL = os.environ.get("TWILIO_WEBHOOK_URL", "").strip()

# Twilio trial: avoid error 63038 (daily cap). TwiML webhook reply does not use REST quota.
WHATSAPP_REPLY_VIA_TWIML = os.environ.get("WHATSAPP_REPLY_VIA_TWIML", "true").lower() in (
    "1",
    "true",
    "yes",
)
WHATSAPP_REST_OPERATOR_NOTIFY = os.environ.get("WHATSAPP_REST_OPERATOR_NOTIFY", "false").lower() in (
    "1",
    "true",
    "yes",
)
WHATSAPP_REST_DAILY_CARE = os.environ.get("WHATSAPP_REST_DAILY_CARE", "false").lower() in (
    "1",
    "true",
    "yes",
)

FAMILY_ALLOWED_MOBILES = [
    m.strip()
    for m in os.environ.get("FAMILY_ALLOWED_MOBILES", "").split(",")
    if m.strip()
]

QUERY_MAX_RESULTS = int(os.environ.get("QUERY_MAX_RESULTS", "10"))
LEXICON_PATH = BASE_DIR / "inbox" / "estate_lexicon.json"
FAMILY_BRAND_NAME = os.environ.get("FAMILY_BRAND_NAME", "Shreeshyam Real Estate")