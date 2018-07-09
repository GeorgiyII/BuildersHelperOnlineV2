from django.shortcuts import render
from django.views.generic import TemplateView


class TemplateForum (TemplateView):

    template_name = "forum.html"