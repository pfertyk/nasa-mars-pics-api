import random
import io

from aiohttp import web, ClientSession

from PIL import Image

NASA_API_KEY = 'DEMO_KEY'
ROVER_URL = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'


async def validate_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return image.width >= 1024 and image.height >= 1024 and image.mode != 'L'


async def get_mars_image_url_from_nasa():
    while True:
        sol = random.randint(0, 1700)
        params = {'sol': sol, 'api_key': NASA_API_KEY}
        async with ClientSession() as session:
            async with session.get(ROVER_URL, params=params) as resp:
                resp_dict = await resp.json()
        if 'photos' not in resp_dict:
            raise Exception
        photos = resp_dict['photos']
        if not photos:
            continue
        return random.choice(photos)['img_src']


async def get_random_cached_mars_photo_url():
    photo_base_url = 'http://mars.jpl.nasa.gov/msl-raw-images/msss/'
    photo_urls = [
        '00582/mcam/0582MR0024340260400318E01_DXXX.jpg',
        '01420/mcam/1420MR0070080000702418E01_DXXX.jpg',
        '00587/mcam/0587ML0024530020300471E01_DXXX.jpg',
    ]
    return photo_base_url + random.choice(photo_urls)


async def get_mars_photo_bytes():
    image_url = await get_random_cached_mars_photo_url()
    print(image_url)
    async with ClientSession() as session:
        async with session.get(image_url) as resp:
            image_bytes = await resp.read()
    # while True:
        # image_url = await get_mars_image_url_from_nasa()
        # print(image_url)
        # async with ClientSession() as session:
            # async with session.get(image_url) as resp:
                # image_bytes = await resp.read()
        # if await validate_image(image_bytes):
            # break
    return image_bytes


async def get_mars_photo(request):
    image = await get_mars_photo_bytes()
    return web.Response(body=image, content_type='image/jpeg')


app = web.Application()
app.router.add_get('/', get_mars_photo, name='mars_photo')


if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=80)
