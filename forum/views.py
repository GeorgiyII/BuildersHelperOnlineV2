from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic import CreateView
from django.views.generic import ListView
from forum.forms import *
from forum.models import Message


class MessageList(ListView):
    template_name = "forum.html"
    model = Message
    queryset = Message.objects.filter(parent__isnull=True)

    def get_context_data(self, **kwargs):
        context = super(MessageList, self).get_context_data(**kwargs)
        context['form'] = MessageForm(initial={'parent': None})
        return context


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = '/forum/'
