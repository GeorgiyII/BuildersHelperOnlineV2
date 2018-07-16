from django.db import models


class StallMark(models.Model):
    class Meta:
        db_table = 'Марка стали'
        verbose_name_plural = u'Марка стали'
        verbose_name = u'значение в таблицу'

    stall_mark = models.CharField(u'Марка стали', max_length=200)
    stall_run = models.IntegerField(verbose_name=u'Сопротивление Run')


class ResCrushing(models.Model):
    class Meta:
        db_table = 'Сопротивление на срез'
        verbose_name_plural = u'Сопротивление на срез'
        verbose_name = u'значение в таблицу'

    stall_run = models.IntegerField(verbose_name=u'Сопротивление Run')
    cls_a = models.IntegerField(verbose_name=u'Значение для класса А')
    cls_bc = models.IntegerField(verbose_name=u'начение для класса BC')


class ResShear(models.Model):
    class Meta:
        db_table = 'Сопротивление на растяжение и смятие'
        verbose_name_plural = u'Сопротивление на растяжение и смятие'
        verbose_name = u'значение в таблицу'

    bolt_class = models.CharField(u'Класс прочности болта', max_length=10)
    bolt_rbs = models.IntegerField(verbose_name=u'Сопротивление Rbs')
    bolt_rbt = models.IntegerField(verbose_name=u'Сопротивление Rbt')


class BoltArea(models.Model):
    class Meta:
        db_table = 'Площадь болта'
        verbose_name_plural = u'Площадь болта'
        verbose_name = u'значение в таблицу'

    bolt_diam = models.IntegerField(verbose_name=u'Диаметр болта')
    bolt_ab = models.FloatField(verbose_name=u'Площадь болта Ab')
    bolt_bn = models.FloatField(verbose_name=u'Площадь болта Abn')
