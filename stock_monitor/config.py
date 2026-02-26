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

# Schedule
MORNING_RUN_HOUR = int(os.getenv("MORNING_RUN_HOUR", "7"))
EOD_RUN_HOUR = int(os.getenv("EOD_RUN_HOUR", "17"))

# Email
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
