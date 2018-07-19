"""builders_helper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from main.views import TemplateMain
from news.views import *
from forum.views import *
from contacts.views import *
from calculator.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateMain.as_view(), name='main'),
    path('news/', TemplateNews.as_view(), name='news'),
    path('forum/', TemplateForum.as_view(), name='forum'),
    path('calculator/', TemplateCalculator.as_view(), name='calculator'),
    path('calculator/bolts_number/', BoltsNumber.as_view(), name='bolts_number'),
    path('calculator/welding_fas/', WeldingFas.as_view(), name='welding_fas'),
    path('calculator/welding_table/', WeldingTable.as_view(), name='welding_table'),
    path('calculator/welding_frame/', WeldingFrame.as_view(), name='welding_frame'),
    path('calculator/beam/', WeldingBead.as_view(), name='beam'),
    path('calculator/sweep_pipe/', SweepPipe.as_view(), name='sweep_pipe'),
    path('contacts/', TemplateContacts.as_view(), name='contacts'),
    re_path(r'^calculator/sweep_pipe/list/$', pipe_list),
    re_path(r'^calculator/sweep_pipe/pipe90/$', pipe90),
    re_path(r'^calculator/sweep_pipe/pipe/$', pipe),
    re_path(r'^calculator/welding_table/result/$', table),

]
