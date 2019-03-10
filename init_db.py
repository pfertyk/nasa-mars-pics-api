from sqlalchemy import create_engine

from nasa_mars_pics.db import metadata, MarsImage
from nasa_mars_pics.settings import DATABASE_URL


def create_postgres_engine():
    return create_engine(DATABASE_URL, isolation_level='AUTOCOMMIT')


engine = create_postgres_engine()


def create_tables(engine):
    metadata.create_all(bind=engine, tables=[MarsImage])


def drop_tables(engine):
    metadata.drop_all(bind=engine, tables=[MarsImage])


if __name__ == '__main__':
    create_tables(engine)
