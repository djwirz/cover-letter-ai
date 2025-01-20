from supabase.client import create_client
from app.config import settings

class Database:
    def __init__(self):
        try:
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            # Test the connection
            self.client.table('documents').select("*").limit(1).execute()
            print("Successfully connected to Supabase")
        except Exception as e:
            print(f"Failed to connect to Supabase: {str(e)}")
            raise