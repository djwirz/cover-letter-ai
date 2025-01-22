from postgrest import AsyncPostgrestClient
from app.config import settings

class Database:
    def __init__(self):
        self.client = AsyncPostgrestClient(
            base_url=f"{settings.SUPABASE_URL}/rest/v1",
            headers={
                "apikey": settings.SUPABASE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_KEY}"
            }
        )
        print("Successfully connected to Supabase")
        
    async def close(self):
        """Close any open connections."""
        if hasattr(self, 'client'):
            await self.client.aclose()
