from django.conf.urls import url
<<<<<<< HEAD
from . import views


urlpatterns = [
    url(r'^register$', views.RegisterView.as_view()),
    url(r'^active/(.+)$', views.active),
    url(r'^exists$', views.exists),
    url(r'^login$', views.LoginView.as_view()),
    url(r'^logout$', views.logout_user),
    url(r'^info$', views.info),
    url(r'^order$', views.order),
    url(r'^site$', views.SiteView.as_view()),
=======

urlpatterns = [

>>>>>>> 665b20e7f457edc4d588b7fe3b5281f4e73363e5
]