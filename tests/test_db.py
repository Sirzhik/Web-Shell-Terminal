from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db.db import DatabaseOperator

import pytest
from unittest.mock import AsyncMock


primary_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
async_session = async_sessionmaker(primary_engine, expire_on_commit=False)

db_operator = DatabaseOperator(engine=primary_engine, session=async_session)

# @pytest.mark.asyncio
# async def test_db_setup():
#     # Mock the init_db method to avoid actual database operations
#     db_operator.init_db = AsyncMock(return_value=None)

#     # Call the init_db method
#     await db_operator.init_db(create_if_not_exists=False)

#     # Assert that the init_db method was called once
#     db_operator.init_db.assert_called_once()

@pytest.mark.asyncio
async def test_add_user():
    new_user = await db_operator.add_user(username="testuser", password="testpass")
    assert new_user is not None
    assert new_user.username == "testuser"
