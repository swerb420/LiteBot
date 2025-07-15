import os
import sys
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geminiBOT_LiteModev2', 'src'))

from database import db_manager as db_manager_module
from database.db_manager import DBManager
from config.settings import DATABASE_URL, DB_POOL_MIN_SIZE, DB_POOL_MAX_SIZE


@pytest.mark.asyncio
async def test_connect_and_disconnect(monkeypatch):
    pool_mock = AsyncMock()
    create_pool = AsyncMock(return_value=pool_mock)
    monkeypatch.setattr(db_manager_module.asyncpg, 'create_pool', create_pool)

    dbm = DBManager()
    await dbm.connect()

    create_pool.assert_awaited_once_with(
        dsn=DATABASE_URL,
        min_size=DB_POOL_MIN_SIZE,
        max_size=DB_POOL_MAX_SIZE,
    )
    assert dbm.pool is pool_mock

    await dbm.connect()  # second call should not recreate
    create_pool.assert_awaited_once()

    await dbm.disconnect()
    pool_mock.close.assert_awaited_once()


class DummyConn:
    def __init__(self):
        self.fetch = AsyncMock(return_value=['rows'])
        self.fetchrow = AsyncMock(return_value={'id': 1})
        self.execute = AsyncMock(return_value='OK')


class DummyPool:
    def __init__(self, conn):
        self.conn = conn

    @asynccontextmanager
    async def acquire(self):
        yield self.conn

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_query_methods(monkeypatch):
    conn = DummyConn()
    pool = DummyPool(conn)
    dbm = DBManager()
    dbm.pool = pool

    connect_mock = AsyncMock()
    dbm.connect = connect_mock

    result = await dbm.fetch('SELECT 1')
    connect_mock.assert_awaited()
    conn.fetch.assert_awaited_once_with('SELECT 1')
    assert result == ['rows']

    result = await dbm.fetchrow('SELECT 2')
    conn.fetchrow.assert_awaited_once_with('SELECT 2')
    assert result == {'id': 1}

    result = await dbm.execute('DELETE 1')
    conn.execute.assert_awaited_once_with('DELETE 1')
    assert result == 'OK'
