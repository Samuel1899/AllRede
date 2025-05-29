# friends/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('send-friend-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline-friend-request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('cancel-friend-request/<int:request_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('remove-friend/<int:user_id>/', views.remove_friend, name='remove_friend'),
]