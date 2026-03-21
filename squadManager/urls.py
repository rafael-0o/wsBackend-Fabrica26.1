from django.urls import path

from .views import (
    home_page,
    register_page,
    squad_page,
)

urlpatterns = [
    path("", include(router.urls)),
    path("web/", home_page, name="home_page"),
    path("web/register/", register_page, name="register_page"),
    path("web/squad/", squad_page, name="squad_page"),
]
