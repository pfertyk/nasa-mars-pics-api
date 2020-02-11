import random

from aiohttp import ClientSession, web

from nasa_mars_pics.db import MarsImage


async def get_random_mars_image_url_from_db(conn):
    mars_image_count = await conn.scalar(
        MarsImage.count().where(MarsImage.c.approved)
    )

    offset = random.randint(0, mars_image_count - 1)
    result = await conn.execute(
        MarsImage.select()
        .where(MarsImage.c.approved)
        .offset(offset)
        .limit(1)
    )
    mars_image = await result.first()

    return mars_image.url


async def get_mars_photo_bytes(app):
    async with app['db'].acquire() as conn:
        image_url = await get_random_mars_image_url_from_db(conn)

    async with ClientSession() as session:
        async with session.get(image_url) as resp:
            image_bytes = await resp.read()

    return image_bytes


# Actual views


async def get_mars_photo(request):
    app = request.app
    image = await get_mars_photo_bytes(app)
    return web.Response(body=image, content_type='image/jpeg')
