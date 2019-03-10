from .views import get_mars_photo, index_mars_photos


def setup_routes(app):
    app.router.add_get('/', get_mars_photo)
    app.router.add_get('/index', index_mars_photos)
