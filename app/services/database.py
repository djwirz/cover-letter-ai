from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.settings.config import settings
from app.agents.utils.logging import setup_logger
from app.models.base import Base

logger = setup_logger("Database")

class Database:
    """Database service for managing connections and sessions"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize database connection"""
        try:
            self.engine = create_async_engine(
                settings.database.url,
                echo=settings.database.echo
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self._initialized = True
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise

    async def close(self) -> None:
        """Close database connections"""
        if self._initialized and self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("Database connections closed")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an async database session
        
        Yields:
            Async database session
            
        Raises:
            Exception: If session creation fails
        """
        if not self._initialized:
            raise Exception("Database not initialized")
            
        async with self.session_factory() as session:
            try:
                yield session
            except Exception as e:
                logger.error(f"Database session error: {str(e)}")
                await session.rollback()
                raise
            finally:
                await session.close()