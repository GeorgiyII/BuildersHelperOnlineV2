from django.shortcuts import render
from django.views.generic import TemplateView


class TemplateNews (TemplateView):

    template_name = "index.html"