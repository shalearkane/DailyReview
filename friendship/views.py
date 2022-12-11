import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView

from .models import Friendship, FriendshipRequests


# Create your views here.
class MyFriendsView(LoginRequiredMixin, ListView):
    model = Friendship
    template_name: str = "friendship/friends.html"
    context_object_name = "friends_list"

    def get_queryset(self):
        queryset = Friendship.objects.filter(from_user=self.request.user).order_by(
            "-created"
        )
        return queryset


@login_required
def MyFriendsListView(request):
    if request.method == "GET":
        friend_ids = (
            Friendship.objects.filter(from_user=request.user)
            .order_by("-created")
            .values_list("to_user_id", flat=True)
        )

        friends = User.objects.filter(id__in=friend_ids).values(
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "socialaccount__extra_data",
        )

        response = json.dumps(list(friends))
        return JsonResponse(response, safe=False)


@login_required
def DiscoverFriendsView(request):
    if request.method == "GET":
        friend_ids = Friendship.objects.filter(from_user=request.user).values_list(
            "to_user_id", flat=True
        )
        friend_request_ids = FriendshipRequests.objects.filter(
            from_user=request.user
        ).values_list("to_user_id", flat=True)

        friend_ids_list = list(friend_ids)
        friend_ids_list.extend(friend_request_ids)
        friend_ids_list.append(request.user.id)

        strangers = (
            User.objects.all()
            .exclude(id__in=friend_ids_list)
            .exclude(is_staff=True)
            .values(
                "id",
                "username",
                "email",
                "first_name",
                "last_name",
                "socialaccount__extra_data",
            )
        )
        response = json.dumps(list(strangers))
        return JsonResponse(response, safe=False)


class FriendRequestsView(LoginRequiredMixin, ListView):
    model = FriendshipRequests
    template_name: str = "friendship/requests.html"
    context_object_name = "friend_requests"

    def get_queryset(self):
        queryset = FriendshipRequests.objects.filter(
            to_user=self.request.user, rejected=False, accepted=False
        ).order_by("-created")

        return queryset


@login_required
def SendFriendshipRequestView(request, user_id):
    if request.method == "GET":
        recipient = User.objects.get(id=user_id)
        fr, created = FriendshipRequests.objects.get_or_create(
            from_user=request.user, to_user=recipient
        )
        if not created:
            return HttpResponse(status=HTTPStatus.ALREADY_REPORTED)
        return HttpResponse(status=HTTPStatus.ACCEPTED)


@login_required
def ProcessFriendRequestView(request, pk):
    fr: FriendshipRequests = get_object_or_404(FriendshipRequests, pk=pk)
    if request.method == "POST" and fr.to_user == request.user:
        if request.POST["action"] == "accept":
            Friendship.objects.get_or_create(from_user=fr.from_user, to_user=fr.to_user)
            Friendship.objects.get_or_create(from_user=fr.to_user, to_user=fr.from_user)
            fr.accepted = True
            fr.save()
            return HttpResponse(status=HTTPStatus.ACCEPTED)

        if request.POST["action"] == "reject":
            fr.rejected = True
            fr.save()
            return HttpResponse(status=HTTPStatus.ACCEPTED)
