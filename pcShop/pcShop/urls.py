"""
Definition of urls for pcShop.
"""

from django.conf.urls import include, url
from django.contrib import admin   
from pcShop import views;
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
   url(r'^admin/', include(admin.site.urls)),
   url(r'^$', views.index,name='Index'),
   url(r'^login/$', views._login , name = 'Login'),
   url(r'^logout/$', views._logout , name = 'Logout'),
   url(r'^register/$', views._register , name = 'Register'),

   url(r'^shop/', include('shop.urls')),   
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += [
        url(r'^(?P<path>.*)/$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        })]