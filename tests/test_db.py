from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db.db import DatabaseOperator, Groups

import pytest
from unittest.mock import AsyncMock
from uuid import uuid4


primary_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
async_session = async_sessionmaker(primary_engine, expire_on_commit=False)

db_operator = DatabaseOperator(engine=primary_engine, session=async_session)

@pytest.mark.asyncio
async def test_add_user():
    new_user = await db_operator.add_user(username="testuser", password="testpass")
    assert new_user is not None
    assert new_user.username == "testuser"

@pytest.mark.asyncio
async def test_get_user_by_username():
    user = await db_operator.get_user_by_username("testuser")
    assert user is not None
    assert user.username == "testuser"

@pytest.mark.asyncio
async def test_get_user_by_id():
    user = await db_operator.get_user_by_id(1)
    assert user is not None
    assert user.id == 1
    assert user.username == "testuser"



@pytest.mark.asyncio
async def test_add_group():
    new_group = await db_operator.add_group(name="testgroup")
    assert new_group is not None
    assert new_group.name == "testgroup"


@pytest.mark.asyncio
async def test_add_virtual_user():
    suffix = uuid4().hex[:8]
    new_virtual_user = await db_operator.add_virtual_user(
        username=f"virt_{suffix}",
        domain="example.com",
        password="secret_password",
        ssh_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCtest",
        ssh_key_type="rsa",
        passphrase="secret_passphrase",
        port=22,
    )

    assert new_virtual_user is not None
    assert new_virtual_user.username == f"virt_{suffix}"
    assert new_virtual_user.domain == "example.com"
    assert new_virtual_user.port == 22
    assert new_virtual_user.password != "secret_password"
    assert new_virtual_user.ssh_key != "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCtest"
    assert new_virtual_user.passphrase != "secret_passphrase"


@pytest.mark.asyncio
async def test_link_group_to_server():
    suffix = uuid4().hex[:8]
    group = await db_operator.add_group(name=f"group_link_{suffix}")
    server = await db_operator.add_virtual_user(
        username=f"server_link_{suffix}",
        domain="link.example.com",
        ssh_key_type="rsa",
    )

    link = await db_operator.link_group_to_server(group_id=group.id, server_id=server.id)

    assert link is not None
    assert link.group_id == group.id
    assert link.server_id == server.id


@pytest.mark.asyncio
async def test_set_group_for_user():
    suffix = uuid4().hex[:8]
    group = await db_operator.add_group(name=f"group_set_{suffix}")
    user = await db_operator.add_user(username=f"user_set_{suffix}", password="testpass")

    updated_user = await db_operator.set_group_for_user(user_id=user.id, group_id=group.id)
    fetched_user = await db_operator.get_user_by_id(user.id)

    assert updated_user is not None
    assert updated_user.group_id == group.id
    assert fetched_user is not None
    assert fetched_user.group_id == group.id


@pytest.mark.asyncio
async def test_get_server_by_id():
    suffix = uuid4().hex[:8]
    server = await db_operator.add_virtual_user(
        username=f"server_get_{suffix}",
        domain="get.example.com",
        ssh_key_type="rsa",
        port=2222,
    )

    fetched_server = await db_operator.get_server_by_id(server.id)

    assert fetched_server is not None
    assert fetched_server.id == server.id
    assert fetched_server.username == f"server_get_{suffix}"
    assert fetched_server.domain == "get.example.com"
    assert fetched_server.port == 2222


@pytest.mark.asyncio
async def test_get_servers_by_user_id():
    suffix = uuid4().hex[:8]
    group = await db_operator.add_group(name=f"group_servers_{suffix}")
    server = await db_operator.add_virtual_user(
        username=f"server_servers_{suffix}",
        domain="servers.example.com",
        ssh_key_type="rsa",
    )
    await db_operator.link_group_to_server(group_id=group.id, server_id=server.id)

    servers = await db_operator.get_servers_by_user_id(group.id)

    assert servers is not None
    assert any(item.id == server.id for item in servers)


@pytest.mark.asyncio
async def test_get_full_table():
    groups_table = await db_operator.get_full_table(Groups)

    assert groups_table is not None
    assert isinstance(groups_table, list)
    assert len(groups_table) > 0
    assert all("id" in row and "name" in row for row in groups_table)


@pytest.mark.asyncio
async def test_remove_group():
    suffix = uuid4().hex[:8]
    group = await db_operator.add_group(name=f"group_remove_{suffix}")
    user = await db_operator.add_user(
        username=f"user_remove_{suffix}",
        password="testpass",
        group_id=group.id,
    )

    await db_operator.remove_group(group.id)

    removed_group = await db_operator.get_group_by_user_id(user.id)
    removed_user = await db_operator.get_user_by_id(user.id)

    assert removed_group is None
    assert removed_user is None


