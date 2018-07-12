from django.shortcuts import render
from django.views.generic import TemplateView


class TemplateMain (TemplateView):

    template_name = "main.html"
