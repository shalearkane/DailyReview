from django.urls import path

from . import views

urlpatterns = [
    path("", views.MyFriendsView.as_view(), name="my-friends"),
    path("my-friends", views.MyFriendsListView, name="my-friends-list"),
    path("discover/", views.DiscoverFriendsView, name="discover-friends"),
    path(
        "requests/", views.FriendRequestsView.as_view(), name="friendship-requests"
    ),
    path(
        "requests/<int:pk>",
        views.ProcessFriendRequestView,
        name="process-friendship-request",
    ),
    path(
        "requests/send/<int:user_id>",
        views.SendFriendshipRequestView,
        name="send-friendship-request",
    ),
]
