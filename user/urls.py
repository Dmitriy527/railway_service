from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import CrewViewSet
from user.views import CreateUserView, LoginUserView, ManageUserView

router = DefaultRouter()
router.register("crew", CrewViewSet)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", LoginUserView.as_view(), name="get_token"),
    path("me/", ManageUserView.as_view(), name="manage_user"),
    path("", include(router.urls)),
]

app_name = "user"
