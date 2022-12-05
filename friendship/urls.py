from django.urls import path

from . import views

urlpatterns = [
    path("", views.MyFriendsView.as_view(), name="my-friends"),
    path("discover/", views.DiscoverFriendsView, name="discover-friends"),
    path(
        "requests/", views.FriendshipRequestsView.as_view(), name="friendship-requests"
    ),
]
