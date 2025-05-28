# friends/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('send-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline-request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('cancel-request/<int:request_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('my-friends/', views.friend_list_view, name='friend_list'), # Uma página para ver amigos e solicitações
]