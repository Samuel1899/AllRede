# C:\Users\Meu computador\Desktop\AllRede\friends\urls.py

from django.urls import path
# Importe as views de amizade do seu aplicativo 'friends'
# (assumindo que elas estão em friends/views.py)
from .views import send_friend_request, accept_friend_request, decline_friend_request, remove_friend

urlpatterns = [
    path('send-request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('accept-request/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('decline-request/<int:request_id>/', decline_friend_request, name='decline_friend_request'),
    path('remove/<int:user_id>/', remove_friend, name='remove_friend'),
    # Adicione outras URLs relacionadas a amizade aqui, se houver
]