from django.shortcuts import render
from django.views.generic import TemplateView


class TemplateCalculator (TemplateView):

    template_name = "calc.html"