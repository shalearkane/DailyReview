import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.list import ListView

from .models import Friendship, FriendshipRequests


# Create your views here.
class MyFriendsView(ListView):
    model = Friendship
    template_name: str = "friendship/friends.html"
    context_object_name = "friends_list"

    def get_queryset(self):
        queryset = Friendship.objects.filter(from_user=self.request.user).order_by(
            "-created"
        )
        return queryset


def DiscoverFriendsView(request):
    if request.method == "GET":
        friend_ids = Friendship.objects.filter(from_user=request.user).values_list(
            "to_user_id", flat=True
        )
        friend_ids_list = list(friend_ids)
        friend_ids_list.append(request.user.id)

        strangers = (
            User.objects.all()
            .exclude(id__in=friend_ids_list)
            .values("id", "username", "email", "first_name", "last_name")
        )
        response = json.dumps(list(strangers))
        return JsonResponse(response, safe=False)


class FriendshipRequestsView(ListView):
    model = FriendshipRequests
    template_name: str = "friendship/requests.html"
    context_object_name = "friendship_requests"

    def get_queryset(self):
        queryset = Friendship.objects.filter(
            to_user=self.request.user, rejected=False
        ).order_by("-created")

        return queryset
