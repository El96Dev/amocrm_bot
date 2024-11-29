import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session
from asyncio import current_task


load_dotenv()


class DatabaseHelper:
    def __init__(self, url: str, echo: bool=False):
        self.url = url
        self.engine = create_async_engine(
            url=url,
            echo=echo
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    
    def get_scoped_session(self):
        session = async_scoped_session(
            self.session_factory,
            scopefunc=current_task
        )
        return session
    

db_helper = DatabaseHelper(
    url="postgresql+asyncpg://" + os.getenv('DB_USER') + ":" + os.getenv('DB_PASSWORD') + "@" + \
        os.getenv('DB_HOST') + ":" + os.getenv('DB_PORT') + "/" + os.getenv('DB_NAME'),
    echo=False
)