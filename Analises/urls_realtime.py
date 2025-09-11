from django.urls import path
from . import views_realtime

urlpatterns = [
    path('realtime/', views_realtime.realtime_analysis, name='realtime_analysis'),
    path('video-feed/', views_realtime.video_feed, name='video_feed'),
]
