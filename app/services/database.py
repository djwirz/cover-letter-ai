from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.settings.config import Settings

class Database:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.engine = create_async_engine(
            self.settings.database_url,
            echo=self.settings.debug_mode
        )
        
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async with self.session_factory() as session:
            yield session
