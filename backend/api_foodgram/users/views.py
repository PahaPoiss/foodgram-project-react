from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, F
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import LimitOffsetPagination

from .models import User, Follow
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly)

from .serializers import (FollowRetrieveSerializer, CustomUserSerializer,
                          CustomUserCreateSerializer, FollowCreateSerializer)


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     permission_classes = (permissions.AllowAny,)
#     pagination_class = LimitOffsetPagination

#     def get_serializer_class(self):
#         if self.action == 'create':
#             return CustomUserCreateSerializer
#         return CustomUserSerializer


@action(methods=['delete'], detail=False)
class FollowCreateViewSet(viewsets.ModelViewSet):
    serializer_class = FollowCreateSerializer
    queryset = Follow.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request,  *args, **kwargs):
        author_id = self.kwargs['author_id']
        author = User.objects.get(id=author_id)
        user = request.user
        Follow.objects.filter(user=user, author=author).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowRetrieveViewSet(viewsets.ModelViewSet):
    serializer_class = FollowRetrieveSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
