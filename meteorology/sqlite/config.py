from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    EXPIRE_IN_ACCESS_TOKEN: int = 3000
    EXPIRE_IN_REFRESH_TOKEN: int = 86400

    model_config = SettingsConfigDict(env_file=".env")


setting = Setting()  