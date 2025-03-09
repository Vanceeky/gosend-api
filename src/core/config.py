from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration class for loading application settings from environment variables.
    Inherits from `BaseSettings` to automatically load values from a `.env` file or environment variables.
    """

    secret: str
    algorithm: str

    DATABASE_URL: str

    # ITEXMO API CONFIGURATION
    ITEXMO_API_ENDPOINT: str
    ITEXMO_API_EMAIL: str
    ITEXMO_API_PASSWORD: str
    ITEXMO_API_CODE: str
    ITEXMO_SENDER_ID: str

    TW_API_URL: str
    TW_API_KEY: str
    TW_SECRET_KEY: str
    TW_MOTHERWALLET: str

    ADMIN_STAGING: str

    """
    The database connection URL. This is the connection string for connecting to the database,
    using the `mysql+aiomysql` protocol for asynchronous connections with MySQL.
    """

    class Config:
        """
        Configuration class to specify how settings should be loaded.
        In this case, it tells Pydantic to read the settings from the `.env` file.
        """
        env_file = ".env"

settings = Settings()