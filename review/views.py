from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from .models import Review


# Create your views here.
class PersonalFeed(ListView):
    model = Review
    paginate_by: int = 10
    template_name: str = "review/feed.html"
    context_object_name = "review_list"

    def get_queryset(self):
        queryset = Review.objects.filter(user=self.request.user).order_by("-date")
        return queryset


class DetailsView(DetailView):
    model = Review
    template_name: str = "review/details.html"


class Write(CreateView):
    model = Review
    template_name = "review/form.html"
    fields = ["title", "text", "personal_thoughts", "visibility", "published"]
    success_url = reverse_lazy("personal-feed")

    def get(self, request, *args, **kwargs):
        if Review.objects.filter(date=timezone.now(), user=request.user).exists():
            review = Review.objects.get(date=timezone.now(), user=request.user)
            return redirect("edit-review", pk=review.pk)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

class Edit(UpdateView):
    model = Review
    template_name = "review/form.html"
    fields = ["title", "text", "personal_thoughts", "visibility", "published"]
    success_url = reverse_lazy("personal-feed")
