from dotenv import load_dotenv
import os

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY","")

#Itrust
ITRUST_BASE_URL = os.getenv("ITRUST_BASE_URL", "")
ITRUST_API_KEY = os.getenv("ITRUST_API_KEY", "")

# Store IDs
STORE_IDS = os.getenv("STORE_IDS", "").split(",")
STORE_NAMES = {
    "2": "Guud Mobile 12 (RAF 1)",
    "3": "Guud Mobile 11 (RAF 3)",
    "4": "Guud Mobile 13 (RAF 2)",
    "5": "Guud Mobile 4 (GM4)",
    "6": "Guud Mobile 5 (GM 5)",
    "7": "Guud Mobile 6 (SIOC 1)",
    "8": "Guud Mobile 7 (SIOC2)",
    "9": "Guud Mobile 8 (SIOC3)",
    "10": "Guud Mobile 1 (GM1)",
    "11": "Guud Mobile 2 (GM2)",
    "12": "Guud Mobile 3 (GM3)",
    "13": "Guud Mobile 10 (GM10)",
    "14": "Guud Vision Clinic",
    "1": "LAB"
}

# Schedule
MORNING_RUN_HOUR = int(os.getenv("MORNING_RUN_HOUR", "7"))
EOD_RUN_HOUR = int(os.getenv("EOD_RUN_HOUR", "17"))

# Email
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

