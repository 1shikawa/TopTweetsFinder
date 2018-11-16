from django.urls import path
from . import views
from django.contrib.auth import views as auth_views #ログアウトに必要

app_name = 'TopTweetsFinder'

urlpatterns = [
    path(
        'index/', views.TwitterFinderIndex.as_view(), name='TwitterFinderIndex'
    ),
    ]