from supabase.client import create_client
from app.config import settings

class Database:
    def __init__(self):
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)