import os

from dotenv import load_dotenv

load_dotenv()

POSTGRESQL_DATABASE_URL = os.getenv("POSTGRESQL_DATABASE_URL")
