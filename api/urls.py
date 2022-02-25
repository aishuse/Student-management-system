from django.urls import path, include
from api import views

urlpatterns = [

    # path('userthrottle', views.UsernewThrottle, name='UserThrottle'),
    path('accounts/register/', views.Registration.as_view()),
    path('accounts/signin/', views.Login.as_view()),
    path('accounts/signout/', views.Logout.as_view()),

]
