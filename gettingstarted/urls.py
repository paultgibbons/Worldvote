from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import hello.views

urlpatterns = patterns('',

    url(r'^$', hello.views.index, name='index'),
    url(r'^login/?', hello.views.login, name='login'),
    url(r'^register/?', hello.views.register, name='register'),
    url(r'^add/?', hello.views.add, name='add'),
    url(r'^account/?', hello.views.account, name='account'),
    url(r'^[0-9]+/?', hello.views.profile, name='profile'),
    url(r'^logout/?', hello.views.logout, name='logout'),

    url(r'^db', hello.views.db, name='db'),
    url(r'^admin/', include(admin.site.urls)),

)
