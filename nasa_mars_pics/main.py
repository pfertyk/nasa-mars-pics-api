from aiohttp import web

from nasa_mars_pics.db import close_pg, init_pg
from nasa_mars_pics.routes import setup_routes


def init_app():
    app = web.Application()

    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)

    setup_routes(app)

    return app
