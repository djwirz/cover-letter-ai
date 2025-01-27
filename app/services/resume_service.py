from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import ResumeResponse
from app.agents.utils.logging import setup_logger

logger = setup_logger("ResumeService")

from sqlalchemy import Table, Column, BigInteger, Text, TIMESTAMP, MetaData
from app.models.base import Base

metadata = MetaData()

active_resume = Table(
    'active_resume',
    metadata,
    Column('id', BigInteger, primary_key=True),
    Column('content', Text, nullable=False),
    Column('metadata', Text),
    Column('created_at', TIMESTAMP(timezone=True)),
    Column('updated_at', TIMESTAMP(timezone=True))
)

class ResumeService:
    def __init__(self):
        self.table = active_resume
        
    async def store_resume(
        self,
        session: AsyncSession,
        content: str,
        metadata: Optional[dict] = None
    ) -> ResumeResponse:
        """Store or update the active resume."""
        try:
            # Check if resume exists
            result = await session.execute(
                select(self.table)
                .order_by(self.table.c.id.desc())
                .limit(1)
            )
            existing = result.first()

            if existing:
                # Update existing resume
                stmt = (
                    update(self.table)
                    .where(self.table.c.id == existing.id)
                    .values(
                        content=content,
                        metadata=metadata,
                        updated_at=datetime.now(UTC)
                    )
                )
            else:
                # Insert new resume
                stmt = insert(self.table).values(
                    content=content,
                    metadata=metadata
                )

            await session.execute(stmt)
            await session.commit()

            return ResumeResponse(
                content=content,
                last_updated=datetime.now(UTC),
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error storing resume: {str(e)}")
            await session.rollback()
            raise

    async def get_active_resume(
        self,
        session: AsyncSession
    ) -> Optional[ResumeResponse]:
        """Get the currently active resume."""
        try:
            result = await session.execute(
                select(self.table)
                .order_by(self.table.c.id.desc())
                .limit(1)
            )
            
            resume = result.first()
            if not resume:
                return None

            return ResumeResponse(
                content=resume.content,
                last_updated=resume.updated_at,
                metadata=resume.metadata
            )

        except Exception as e:
            logger.error(f"Error retrieving resume: {str(e)}")
            raise