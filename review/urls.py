from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", views.PublicFeed.as_view(), name="public-feed"),
    path("my/", views.PersonalFeed.as_view(), name="personal-feed"),
    path("details/<int:pk>", views.DetailsView.as_view(), name="review-details"),
    path("write/", views.Write.as_view(), name="write-review"),
    path("edit/<int:pk>", views.Edit.as_view(), name="edit-review"),
    path(
        "get/<int:user_id>/<int:year>/<int:month>/<int:day>/",
        views.ReviewFromDateView.as_view(),
        name="get-review-from-date",
    ),
    path(
        "compare/",
        TemplateView.as_view(template_name="review/compare.html"),
        name="compare",
    ),
]
