"""up URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from gpm import views
from django.conf.urls import include

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', views.index),
    url(r'^index', views.index),
    url(r'^login', views.login),
    url(r'^register', views.register),
    url(r'^logout', views.logout),
    url(r'^publish', views.publish),
    url(r'^passage', views.passage),
    url(r'^question', views.question),
    url(r'^student', views.student),
    url(r'^teacher', views.teacher),
    url(r'^project', views.project),
    url(r'^userinfo', views.userinfo),
    url(r'^uploads', views.uploads),

    url(r'^schedule', views.schedule),

    url(r'^evaluate', views.evaluate),
    url(r'^data', views.data),
    url(r'^file', views.file),
    url(r'^message', views.message),

    # 测试用
    url(r'^just_test', views.just_test),

]
