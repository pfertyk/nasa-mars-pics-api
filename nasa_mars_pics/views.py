import io
import logging
import random

from aiohttp import ClientSession, web
from PIL import Image

from nasa_mars_pics.db import MarsImage
from nasa_mars_pics.settings import NASA_API_KEY, ROVER_URL

logger = logging.Logger(__name__)


async def get_image_info_from_url(image_url):
    async with ClientSession() as session:
        async with session.get(image_url) as resp:
            image_bytes = await resp.read()
            return Image.open(io.BytesIO(image_bytes))


async def is_image_approved(image_info):
    return (
        image_info.width >= 1024 and image_info.height >= 1024 and
        image_info.mode != 'L'
    )


async def index_mars_photos_from_nasa_api(app):
    params = {'api_key': NASA_API_KEY}
    async with ClientSession() as session:
        async with session.get(ROVER_URL, params=params) as resp:
            resp_dict = await resp.json()

    max_sol = resp_dict['rover']['max_sol']
    rover_photos_url = ROVER_URL + 'photos'
    logger.info('Max sol: {}'.format(max_sol))

    for sol in range(0, max_sol + 1):
        params['sol'] = sol
        async with ClientSession() as session:
            async with session.get(rover_photos_url, params=params) as resp:
                resp_dict = await resp.json()

        if 'photos' not in resp_dict:
            return

        photos = resp_dict['photos']
        if not photos:
            continue

        for photo in photos:
            image_url = photo['img_src']
            logger.info('Image URL found: {}'.format(image_url))
            async with app['db'].acquire() as conn:
                result = await conn.execute(
                    MarsImage.select().where(MarsImage.c.url == image_url)
                )
                existing_image = await result.first()
                if not existing_image:
                    image_info = await get_image_info_from_url(image_url)
                    approved = await is_image_approved(image_info)
                    logger.info('Image status: {}'.format(
                        'approved' if approved else 'rejected'
                    ))

                    await conn.execute(MarsImage.insert().values(
                        url=image_url,
                        width=image_info.width,
                        height=image_info.height,
                        mode=image_info.mode,
                        approved=approved
                    ))
                else:
                    logger.info(
                        'Image {} already in database'.format(image_url)
                    )


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


async def index_mars_photos(request):
    logger.info('Indexing process started')
    app = request.app
    await index_mars_photos_from_nasa_api(app)
    logger.info('Indexing process finished')
    return web.Response(body='OK')
