from .views import get_mars_photo


def setup_routes(app):
    app.router.add_get('/', get_mars_photo)
