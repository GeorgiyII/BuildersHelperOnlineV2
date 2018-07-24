from django.views.generic import ListView, DetailView, TemplateView
from news.models import Article


class TemplateMain (ListView):

    template_name = "main.html"
    model = Article


class TemplateNews (DetailView):

    template_name = "news.html"
    model = Article

