from django.conf.urls import url
from shop import views

urlpatterns = [  
    url(r'^$', views.shop ,name='Shop'),
    url(r'^active/$', views.active, name='Active'), 
    url(r'^product/(?P<product_id>[0-9]+)/$', views.product, name='Product'),
    url(r'^basket/$', views.basket, name='Basket'),      
    url(r'^bought/$', views.bought, name='Bought'), 
    url(r'^bought/(?P<bought_id>[0-9]+)/$', views.boughtdetail, name='BoughtDetail'), 
    url(r'^bought/complet/$', views.boughtComplet, name='BoughtComplet,'), 
    url(r'^completed/$', views.completed, name='Completed'), 
    url(r'^completed/(?P<com_id>[0-9]+)/$', views.completeddetail, name='CompletedDetail'), 
    url(r'^buy/$', views.buy, name='Buy'), 
    url(r'^options/$', views.options, name='Options'), 
    url(r'^getfile/$', views.getfile, name='GetFile'), 
 ]
