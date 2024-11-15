from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_HOST: str
    DB_PORT: int

    @property
    def data_source_name(self):
        return f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@" \
               f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"


db_settings = DBSettings()
