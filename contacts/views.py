from django.shortcuts import render
from django.views.generic import TemplateView


class TemplateContacts (TemplateView):

    template_name = "contact.html"
