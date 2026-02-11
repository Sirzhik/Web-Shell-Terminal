import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    SECRET: str = 'WSTestSecretKey'
    ADMIN_PASSWORD: str = 'WSTestAdminPass'
    PORT: int = 2280
    DB_DIRECTORY: str = 'database/wst.db'
    DB_TYPE: str = 'sqlite'
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_NAME: str = 'wstdb'
    DB_USER: str = 'wstuser'
    DB_PASSWORD: str = 'wstpass'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

config = Config()
