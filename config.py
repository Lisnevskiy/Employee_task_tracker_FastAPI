import os

from dotenv import load_dotenv

load_dotenv()

POSTRGRESQL_DATABASE_URL = os.getenv("POSTRGRESQL_DATABASE_URL")
