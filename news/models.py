from django.db import models
from django.utils import timezone


class Article (models.Model):

    article_capture = models.CharField(max_length=100)
    article_text = models.TextField(u'Текст статьи')
    article_short = models.TextField(u'Описание статьи')
    article_image = models.ImageField(upload_to='static/articles/', default='static/articles/')
    article_author = models.CharField(max_length=100)
    article_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-article_date']

