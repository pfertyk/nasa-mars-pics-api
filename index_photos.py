import io
import asyncio
import logging

from aiohttp import ClientSession
from PIL import Image

from nasa_mars_pics.db import MarsImage, get_engine
from nasa_mars_pics.settings import NASA_API_KEY, ROVER_URL

logging.basicConfig(level=logging.INFO)


async def get_image_from_url(image_url):
    async with ClientSession() as session:
        async with session.get(image_url) as resp:
            image_bytes = await resp.read()
            return Image.open(io.BytesIO(image_bytes))


async def is_image_approved(image):
    return (image.width >= 1024 and image.height >= 1024 and image.mode != 'L')


async def get_response_json(url, params):
    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()


async def get_max_sol(rover_url):
    params = {'api_key': NASA_API_KEY}
    rover_response = await get_response_json(rover_url, params)
    max_sol = rover_response['rover']['max_sol']
    logging.info('Max sol: {}'.format(max_sol))

    return max_sol


async def get_rover_photos(rover_url, sol):
    rover_photos_url = rover_url + 'photos'
    params = {'api_key': NASA_API_KEY, 'sol': sol}
    photos_response = await get_response_json(rover_photos_url, params)

    if 'photos' not in photos_response:
        return []

    photos = photos_response['photos']

    if not photos:
        logging.info('No photos taken on sol {}'.format(sol))

    return photos


async def verify_and_insert_image(image_url, sol, engine):
    async with engine.acquire() as conn:
        result = await conn.execute(
            MarsImage.select().where(MarsImage.c.url == image_url)
        )

        existing_image = await result.first()

        if not existing_image:
            image = await get_image_from_url(image_url)
            approved = await is_image_approved(image)
            logging.info('Image status: {}'.format(
                'approved' if approved else 'rejected'
            ))

            await conn.execute(MarsImage.insert().values(
                url=image_url,
                sol=sol,
                width=image.width,
                height=image.height,
                mode=image.mode,
                approved=approved
            ))
        else:
            logging.info('Image {} already in database'.format(image_url))


async def index_mars_photos_from_nasa_api(rover_url):
    max_sol = await get_max_sol(rover_url)
    engine = await get_engine()

    for sol in range(0, max_sol + 1):
        photos = await get_rover_photos(rover_url, sol)

        for photo in photos:
            image_url = photo['img_src']
            logging.info('Image URL found: {}'.format(image_url))
            await verify_and_insert_image(image_url, sol, engine)


if __name__ == '__main__':
    logging.info('Indexing process started')
    asyncio.run(index_mars_photos_from_nasa_api(ROVER_URL))
    logging.info('Indexing process finished')
