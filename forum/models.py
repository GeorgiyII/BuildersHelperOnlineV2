from django.db import models
from django.utils import timezone
from django.contrib.auth.forms import User


class Message(models.Model):

    message_text = models.TextField(u'Текст сообщения')
    message_date = models.DateTimeField(default=timezone.now)
    message_author = models.CharField(max_length=100)
    message_theme = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-message_date']

    def get_comments(self):
        return Message.objects.filter(parent=self).order_by('-message_date')

    def get_comment_form(self):
        from forum.forms import MessageForm
        return MessageForm(initial={'parent': self.id})
