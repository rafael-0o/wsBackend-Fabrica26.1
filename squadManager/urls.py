from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewSet import (
    RegisterUserView,
    LoginView,
    LogoutView,
    SquadMemberViewSet,
)
from .views import (
    home_page,
    register_page,
    squad_page,
    login_page,
    logout_page,
    search_characters_page,
    recruit_character,
    edit_squad_member,
    delete_squad_member,
)

router = DefaultRouter()
router.register(r"squad", SquadMemberViewSet, basename="squad")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterUserView.as_view(), name="user_register"),
    path("auth/login/", LoginView.as_view(), name="user_login"),
    path("auth/logout/", LogoutView.as_view(), name="user_logout"),
    path("web/", home_page, name="home_page"),
    path("web/login/", login_page, name="login_page"),
    path("web/logout/", logout_page, name="logout_page"),
    path("web/register/", register_page, name="register_page"),
    path("web/search/", search_characters_page, name="search_characters"),
    path("web/recruit/", recruit_character, name="recruit_character"),
    path("web/squad/", squad_page, name="squad_page"),
    path("web/squad/<int:member_id>/edit/", edit_squad_member, name="edit_squad_member"),
    path("web/squad/<int:member_id>/delete/", delete_squad_member, name="delete_squad_member"),
]