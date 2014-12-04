from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

import hello.views

urlpatterns = patterns('',

    # main pages
    url(r'^$', hello.views.index, name='index'),
    url(r'^login/', hello.views.login, name='login'),
    url(r'^register/', hello.views.register, name='register'),
    url(r'^add/', hello.views.add, name='add'),
    url(r'^account/', hello.views.account, name='account'),
    url(r'^([0-9]+)/', hello.views.profile, name='profile'),
    url(r'^search/', hello.views.search, name='search'),
    url(r'^recommended/', hello.views.recommended, name='recommended'),
    url(r'^nameChange/', hello.views.nameChange, name='nameChange'),
    url(r'^imageChange/', hello.views.imageChange, name='imageChange'),

    # redirects and xml http requests
    url(r'^delete/', hello.views.delete, name='delete'),
    url(r'^logout/', hello.views.logout, name='logout'),
    url(r'^vote/?', hello.views.vote, name='vote'),
    url(r'^markSearchName/?', hello.views.markSearchName, name='markSearchName'),
    url(r'^markScoreboard/?', hello.views.markScoreboard, name='markScoreboard'),
    url(r'^markVote/?', hello.views.markVote, name='markVote'),
    url(r'^markLogin/?', hello.views.markLogin, name='markLogin'),

    # other
    url(r'^admin/', include(admin.site.urls)),
    url(r'^images/([0-9]+)\.(gif|jpg|jpeg|png)', hello.views.images),

    # TODO: we can remove the name if we dont use them
    # trash
    url(r'^db', hello.views.db, name='db'),
    url(r'^reverse/?', hello.views.reverse, name='reverse'),
    url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, }),

)
