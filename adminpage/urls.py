# -*- coding: utf-8 -*-
#

from adminpage.views import LoginView,LogoutView,ActivityList,ActivityDelete,ActivityCreate,ImageUpload,ActivityDetail,ActivityMenu,ActivityCheckin
from django.conf.urls import url


__author__ = "Epsirom"


urlpatterns = [
    url(r'^login/?$', myView.as_view()),
    url(r'^logout/?$',logoutView.as_view()),
    url(r'^activity/list/?$' ,Activity_list.as_view()),
    url(r'^activity/delete/?$',Activity_delete.as_view()),
    url(r'^activity/detail?create=1/?$',Activity_create.as_view()),
    url(r'^image/upload/?$',ImageUpload.as_view()),
    url(r'^activity/detail/?$',ActivityDetail.as_view()),
    url(r'^activity/menu/?$',ActivityMenu.as_view()),
    url(r'^activity/checkin/?$',ActivityCheckin.as_view()),
    ]
