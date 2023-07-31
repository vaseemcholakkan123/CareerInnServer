from rest_framework.response import Response
from rest_framework import status


class PostsMixin:
    def perform_destroy(self, instance):
        if instance.posted_user.id != self.request.user.id: 
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
        return super().perform_destroy(instance)
    
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context'] = {'request':self.request}
        return serializer_class(*args, **kwargs)