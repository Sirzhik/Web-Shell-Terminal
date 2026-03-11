from sqlalchemy import ForeignKey, exists, select, inspect
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from cryptography.fernet import Fernet
from db.env import config

import base64
import uuid
import hashlib
import os

DB_DIRECTORY = config.DB_DIRECTORY + '/wst.db'

db_url = {
    'sqlite': f'sqlite+aiosqlite:///{DB_DIRECTORY}',
    'postgresql': f'postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}',
}

encryption_key = config.SECRET
primary_engine = create_async_engine(db_url[config.DB_TYPE])
primary_session = async_sessionmaker(primary_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    ...

class WebUsers(Base):
    __tablename__ = 'webusers'

    id: Mapped[int] = mapped_column(primary_key=True)
    legacy_session: Mapped[str]
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

class Groups(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

class Sessions(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('webusers.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    session: Mapped[str] = mapped_column(default=lambda: str(uuid.uuid4()))
    created_at: Mapped[int] = mapped_column()
    expires_at: Mapped[int] = mapped_column(nullable=False)
    ip: Mapped[str] = mapped_column(nullable=True)

class AdminSessions(Base):
    __tablename__ = 'adminsessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    session: Mapped[str] = mapped_column(default=lambda: str(uuid.uuid4()))
    created_at: Mapped[int] = mapped_column()
    expires_at: Mapped[int] = mapped_column(nullable=False)
    ip: Mapped[str] = mapped_column(nullable=True)

class VirtualUsers(Base):
    __tablename__ = 'sshaccounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column()
    ssh_key: Mapped[str] = mapped_column()
    ssh_key_type: Mapped[str] = mapped_column()
    passphrase: Mapped[str] = mapped_column()
    domain: Mapped[str] = mapped_column(nullable=False)
    port: Mapped[int] = mapped_column(nullable=False, default=22)

class GroupToServer(Base):
    __tablename__ = 'grouptoservers'

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    server_id: Mapped[int] = mapped_column(ForeignKey('sshaccounts.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

async def encrypt_string(string: str) -> str:
    key = hashlib.sha256(encryption_key.encode()).digest()
    key_b64 = base64.urlsafe_b64encode(key)
    fernet = Fernet(key_b64)

    return fernet.encrypt(string.encode()).decode()

async def decrypt_string(string: str) -> str:
    key = hashlib.sha256(encryption_key.encode()).digest()
    key_b64 = base64.urlsafe_b64encode(key)
    fernet = Fernet(key_b64)

    return fernet.decrypt(string.encode()).decode()

def hex_pswd(pswd: str) -> str:
    return hashlib.sha256(pswd.encode()).hexdigest()


class DatabaseOperator:
    def __init__(self, engine, session):
        self.engine = engine
        self.session = session

    ###########
    # Setters #
    ###########

    async def setup(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            await self.add_group("default")

    async def init_db(self, create_if_not_exists: bool = True):
        if config.DB_TYPE == 'sqlite':
            db_dir = os.path.dirname(DB_DIRECTORY)
            if db_dir and not os.path.exists(db_dir) and create_if_not_exists:
                os.makedirs(db_dir, exist_ok=True)
        if not await self.table_exists('sessions'):
            await self.setup()

    async def add_user(self, username: str, password: str, legacy_session: str = "", group_id: int = None) -> WebUsers:
        async with self.session() as session:
            if group_id is None:
                result = await session.execute(
                    select(Groups).where(Groups.name == "default")
                )
                group = result.scalars().first()
                group_id = group.id

            user = WebUsers(username=username, password=hex_pswd(password), legacy_session=legacy_session, group_id=group_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user

    async def create_session(self, user_id: int, created_at: int) -> Sessions:
        async with self.session() as session:
            expires_at = created_at + 3600 * 24  * 7  # 7 days
            sess = Sessions(user_id=user_id, created_at=created_at, expires_at=expires_at)
            session.add(sess)
            await session.commit()
            await session.refresh(sess)
            
            return sess

    async def add_group(self, name: str) -> Groups:
        async with self.session() as session:
            group = Groups(name=name)
            session.add(group)
            await session.commit()
            await session.refresh(group)

            return group

    async def add_virtual_user(self, username: str, domain: str, password: str = None, 
                               ssh_key: str = None, ssh_key_type: str = None, passphrase: str = None, port: int = 22) -> VirtualUsers:
        password_encrypted = ''
        ssh_key_encrypted = ''
        passphrase_encrypted = ''
        
        if password:
            password_encrypted = await encrypt_string(password)
        if ssh_key:
            ssh_key_encrypted = await encrypt_string(ssh_key)
        if passphrase:
            passphrase_encrypted = await encrypt_string(passphrase)

        async with self.session() as session:
            user = VirtualUsers(username=username, 
                                password=password_encrypted, 
                                ssh_key=ssh_key_encrypted, 
                                ssh_key_type=ssh_key_type,
                                passphrase=passphrase_encrypted,
                                domain=domain,
                                port=port)
            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user

    async def set_group_for_user(self, user_id: int, group_id: int) -> WebUsers:
        async with self.session() as session:
            result = await session.execute(
                select(WebUsers).where(WebUsers.id == user_id)
            )
            user = result.scalars().first()
            user.group_id = group_id
            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user

    async def link_group_to_server(self, group_id: int, server_id: int) -> GroupToServer:
        async with self.session() as session:
            link = GroupToServer(group_id=group_id, server_id=server_id)
            session.add(link)
            await session.commit()
            await session.refresh(link)

            return link

    async def create_admin_session(self, created_at: int) -> AdminSessions:
        async with self.session() as session:
            expires_at = created_at + 3600 * 24 * 7  # 7 days
            admin_sess = AdminSessions(created_at=created_at, expires_at=expires_at)
            session.add(admin_sess)
            await session.commit()
            await session.refresh(admin_sess)
            
            return admin_sess

    ############
    # removers #
    ############

    async def remove_session(self, session_str: str) -> None:
        async with self.session() as session:
            result = await session.execute(
                select(Sessions).where(Sessions.session == session_str)
            )
            sess = result.scalars().first()
            if sess:
                await session.delete(sess)
                await session.commit()

    async def remove_admin_session(self, session_str: str) -> None:
        async with self.session() as session:
            result = await session.execute(
                select(AdminSessions).where(AdminSessions.session == session_str)
            )
            admin_sess = result.scalars().first()
            if admin_sess:
                await session.delete(admin_sess)
                await session.commit()

    async def remove_user(self, id: int) -> None:
        async with self.session() as session:
            result = await session.execute(
                select(Sessions.session).where(Sessions.user_id == id)
            )
            await self.remove_session(result.scalars().first())
            
            result = await session.execute(
                select(WebUsers).where(WebUsers.id == id)
            )
            user = result.scalars().first()
            if user:
                await session.delete(user)
                await session.commit()

    async def remove_group(self, id: int) -> None:
        async with self.session() as session:
            result = await session.execute(
                select(Groups).where(Groups.id == id)
            )
            group = result.scalars().first()
            if group:
                users_result = await session.execute(
                    select(WebUsers.id).where(WebUsers.group_id == group.id)
                )
                user_ids = users_result.scalars().all()
                for user_id in user_ids:
                    await self.remove_user(user_id)

                await session.delete(group)
                await session.commit()

    async def remove_virtual_user(self, id: int) -> None:
        async with self.session() as session:
            result = await session.execute(
                select(GroupToServer).where(GroupToServer.server_id == id)
            )
            links = result.scalars().all()
            for link in links:
                await session.delete(link)
            
            result = await session.execute(
                select(VirtualUsers).where(VirtualUsers.id == id)
            )
            user = result.scalars().first()
            if user:
                await session.delete(user)
                await session.commit()    

    async def remove_link_group_to_server(self, group_id: int, server_id: int) -> None:
        async with self.session() as session:
            result = await session.execute(
                select(GroupToServer).where(GroupToServer.group_id == group_id, GroupToServer.server_id == server_id)
            )
            link = result.scalars().first()
            if link:
                await session.delete(link)
                await session.commit()

    async def remove_admin_session(self, session_str: str) -> None:
        async with self.session() as session:
            result = await session.execute(
                select(AdminSessions).where(AdminSessions.session == session_str)
            )
            admin_sess = result.scalars().first()
            if admin_sess:
                await session.delete(admin_sess)
                await session.commit()

    ###########
    # Getters #
    ###########

    async def get_full_table(self, table_class) -> list:
        async with self.session() as session:
            result = await session.execute(
                select(table_class)
            )
            objects = result.scalars().all()
            
            return [
                {col.name: getattr(obj, col.name) for col in table_class.__table__.columns}
                for obj in objects
            ]

    async def get_server_by_id(self, server_id: int) -> VirtualUsers | None:
        async with self.session() as session:
            result = await session.execute(
                select(VirtualUsers).where(VirtualUsers.id == server_id)
            )
            return result.scalars().first()

    async def get_session_by_field(self, field: str, value) -> Sessions | None:
        async with self.session() as session:
            stmt = select(Sessions).where(getattr(Sessions, field) == value)
            result = await session.execute(stmt)
            sess = result.scalars().first()
            return sess

    async def get_servers_by_user_id(self, user_id: int) -> list[VirtualUsers]:
        async with self.session() as session:
            result = await session.execute(
                select(VirtualUsers).join(GroupToServer).where(GroupToServer.group_id == user_id)
            )
            return result.scalars().all()

    async def get_session_by_session_str(self, session_str: str) -> Sessions | None:
        return await self.get_session_by_field("session", session_str)

    async def get_session_by_user_id(self, user_id: int) -> Sessions | None:
        return await self.get_session_by_field("user_id", user_id)

    async def get_user_by_username(self, username: str) -> WebUsers | None:
        async with self.session() as session:
            result = await session.execute(
                select(WebUsers).where(WebUsers.username == username)
            )
            
            return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> WebUsers | None:
        async with self.session() as session:
            result = await session.execute(
                select(WebUsers).where(WebUsers.id == user_id)
            )
            
            return result.scalars().first()

    async def get_virtual_user_by_id(self, virtual_user_id: int) -> VirtualUsers | None:
        async with self.session() as session:
            result = await session.execute(
                select(VirtualUsers).where(VirtualUsers.id == virtual_user_id)
            )
            
            return result.scalars().first()
        
    async def get_group_by_user_id(self, user_id: int) -> Groups | None:
        async with self.session() as session:
            result = await session.execute(
                select(WebUsers).where(WebUsers.id == user_id)
            )
            user = result.scalars().first()
            if not user:
                return None

            return user.group_id

    async def get_admin_session_by_field(self, field: str, value) -> AdminSessions | None:
        async with self.session() as session:
            stmt = select(AdminSessions).where(getattr(AdminSessions, field) == value)
            result = await session.execute(stmt)
            admin_sess = result.scalars().first()
            return admin_sess

    async def get_admin_session_by_session_str(self, session_str: str) -> AdminSessions | None:
        return await self.get_admin_session_by_field("session", session_str)

    #############
    # Validator #
    #############

    async def validate_credentials(self, username: str, password: str) -> bool:
        async with self.session() as session:
            result = await session.execute(
                select(WebUsers).where(WebUsers.username == username, WebUsers.password == hex_pswd(password))
            )

            user = result.scalars().first()
            if user:
                return True
            return False

    async def validate_admin_credentials(self, password: str) -> bool:
        """Validates admin password against config.ADMIN_PASSWORD without hashing"""
        return password == config.ADMIN_PASSWORD

    async def is_group_linked(self, group_id: int, virtual_user_id: int) -> bool:
        async with self.session() as session:
            result = await session.execute(
                select(exists().where(GroupToServer.group_id == group_id, GroupToServer.server_id == virtual_user_id))
            )
            
            return result.scalar()

    async def table_exists(self, table_name: str) -> bool:
        async with self.engine.connect() as conn:
            return await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).has_table(table_name)
            )

db_operator = DatabaseOperator(engine=primary_engine, session=primary_session)

