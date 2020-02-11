import aiopg.sa
from sqlalchemy import Boolean, Column, Integer, MetaData, String, Table

from nasa_mars_pics.settings import DATABASE_URL

metadata = MetaData()


MarsImage = Table(
    'mars_image', metadata,
    Column('url', String, primary_key=True),
    Column('sol', Integer),
    Column('width', Integer),
    Column('height', Integer),
    Column('mode', String),
    Column('approved', Boolean, default=True),
)


async def get_engine():
    return await aiopg.sa.create_engine(dsn=DATABASE_URL)


async def init_pg(app):
    app['db'] = await get_engine()


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()
