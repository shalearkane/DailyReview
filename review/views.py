import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.base import View
from django.views.generic.dates import (
    BaseDateDetailView,
    BaseDayArchiveView,
    _date_from_string,
)
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeletionMixin, UpdateView
from django.views.generic.list import ListView

from friendship.models import Friendship

from .models import Review


# Create your views here.
class PersonalFeed(LoginRequiredMixin, ListView):
    model = Review
    paginate_by: int = 10
    template_name: str = "review/feed_personal.html"
    context_object_name = "review_list"

    def get_queryset(self):
        queryset = Review.objects.filter(user=self.request.user).order_by("-date")
        return queryset


class PublicFeed(ListView):
    model = Review
    paginate_by: int = 10
    template_name: str = "review/feed.html"
    context_object_name = "review_list"

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            queryset = Review.objects.filter(visibility="EV").order_by("-date")
        else:
            friend_ids = (
                Friendship.objects.filter(from_user=self.request.user)
                .order_by("-created")
                .values_list("to_user_id", flat=True)
            )
            queryset = Review.objects.filter(
                Q(user__in=friend_ids) | Q(visibility="EV")
            ).order_by("-date")
        return queryset


class DetailsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Review
    template_name: str = "review/details.html"

    def test_func(self):
        obj: Review = self.get_object()
        print(self.request.user.id)
        if obj.user == self.request.user or obj.visibility == "EV":
            return True
        elif obj.visibility == "FR":
            return Friendship.objects.filter(
                from_user=obj.user, to_user=self.request.user
            ).exists()
        else:
            return False


class ReviewFromDateView(LoginRequiredMixin, BaseDateDetailView):
    model = Review
    date_field = "date"
    allow_future = False
    month_format = "%m"

    def get_queryset(self):
        visibility_level = []
        user_id = self.kwargs["user_id"]
        if self.request.user.id != user_id:
            if Friendship.objects.filter(
                from_user=self.request.user.id, to_user=user_id
            ).exists():
                visibility_level = ["FR", "EV"]
            else:
                visibility_level = ["EV"]
        else:
            visibility_level = ["FR", "EV", "ME"]

        return self.model.objects.filter(user=user_id, visibility__in=visibility_level)

    def get_object(self, queryset=None):
        """Get the object this request displays."""
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = _date_from_string(
            year,
            self.get_year_format(),
            month,
            self.get_month_format(),
            day,
            self.get_day_format(),
        )

        # Use a custom queryset if provided
        qs = self.get_queryset() if queryset is None else queryset

        if not self.get_allow_future() and date > datetime.date.today():
            raise Http404(
                (
                    "Future %(verbose_name_plural)s not available because "
                    "%(class_name)s.allow_future is False."
                )
                % {
                    "verbose_name_plural": qs.model._meta.verbose_name_plural,
                    "class_name": self.__class__.__name__,
                }
            )

        lookup_kwargs = self._make_single_date_lookup(date)
        qs = get_object_or_404(klass=qs, **lookup_kwargs)

        return qs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = json.dumps(model_to_dict(self.object))
        return JsonResponse(response, safe=False)


class FriendsWhoReviewedOnDateView(BaseDayArchiveView):
    model = Review
    date_field = "date"
    month_format = "%m"

    def get_queryset(self):
        friend_ids = Friendship.objects.filter(from_user=self.request.user).values_list(
            "to_user_id", flat=True
        )
        return self.model.objects.filter(user__in=friend_ids)

    def get_dated_items(self):
        """Return (date_list, items, extra_context) for this request."""
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()

        date = _date_from_string(
            year,
            self.get_year_format(),
            month,
            self.get_month_format(),
            day,
            self.get_day_format(),
        )

        return self._get_dated_items(date)

    def _get_dated_items(self, date):
        """
        Do the actual heavy lifting of getting the dated items; this accepts a
        date object so that TodayArchiveView can be trivial.
        """
        lookup_kwargs = self._make_single_date_lookup(date)
        qs = self.get_dated_queryset(**lookup_kwargs)

        return (
            None,
            qs,
            None,
        )

    def get_dated_queryset(self, **lookup):
        """
        Get a queryset properly filtered according to `allow_future` and any
        extra lookup kwargs.
        """
        user_ids = self.get_queryset().filter(**lookup).values_list("user", flat=True)
        qs = User.objects.filter(id__in=user_ids).values(
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "socialaccount__extra_data",
        )
        return qs

    def get(self, request, *args, **kwargs):
        self.date_list, self.object_list, extra_context = self.get_dated_items()
        response = json.dumps(list(self.object_list))
        return JsonResponse(response, safe=False)


class Write(LoginRequiredMixin, CreateView):
    model = Review
    template_name = "review/form.html"
    fields = ["title", "text", "personal_thoughts", "visibility"]
    success_url = reverse_lazy("personal-feed")

    def get(self, request, *args, **kwargs):
        if Review.objects.filter(date=timezone.now(), user=request.user).exists():
            review = Review.objects.get(date=timezone.now(), user=request.user)
            return redirect("edit-review", pk=review.pk)
        return super().get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(Write, self).get_form(form_class)
        form.fields["personal_thoughts"].required = False
        form.fields["visibility"].required = True
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)


class Edit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    template_name = "review/form.html"
    fields = ["title", "text", "personal_thoughts", "visibility"]
    success_url = reverse_lazy("personal-feed")

    def test_func(self):
        return self.model.objects.filter(
            pk=self.kwargs["pk"], user=self.request.user
        ).exists()


class Delete(LoginRequiredMixin, UserPassesTestMixin, DeletionMixin, View):
    model = Review
    success_url = reverse_lazy("personal-feed")

    def test_func(self):
        return Review.objects.filter(
            user=self.request.user, pk=self.kwargs["pk"]
        ).exists()

    def get_object(self):
        return get_object_or_404(Review, pk=self.kwargs["pk"])
