# posts/views.py (apenas para API)
from rest_framework import viewsets
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]