from pymongo import ASCENDING
from pymongo.asynchronous.database import AsyncDatabase


async def setup_database(db: AsyncDatabase) -> None:
    await db.command("ping")
    await db["campaigns"].create_index("campaign_id", unique=True)
    await db["calls"].create_index("call_id", unique=True)
    await db["calls"].create_index(
        [("campaign_id", ASCENDING), ("created_at", ASCENDING)]
    )
