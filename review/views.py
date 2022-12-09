import datetime
import json

from django.forms.models import model_to_dict
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.dates import BaseDateDetailView, _date_from_string
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from friendship.models import Friendship

from .models import Review


# Create your views here.
class PersonalFeed(ListView):
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
        queryset = Review.objects.filter().order_by("-date")
        return queryset


class DetailsView(DetailView):
    model = Review
    template_name: str = "review/details.html"


class ReviewFromDateView(BaseDateDetailView):
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


class Write(CreateView):
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


class Edit(UpdateView):
    model = Review
    template_name = "review/form.html"
    fields = ["title", "text", "personal_thoughts", "visibility"]
    success_url = reverse_lazy("personal-feed")
