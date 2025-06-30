from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import (generics, permissions, status,
                            viewsets, filters)
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Category, Genre, Title, Review
from .permissions import (IsAdminOrReadOnly, IsRoleAdminOnly,
                          IsOwnerAdminModeratorOrReadOnly)
from .serializers import (UserSerializer,
                          UserMeUpdateSerializer,
                          UserSignupSerializer,
                          UserTokenSerializer,
                          CategorySerializer,
                          GenreSerializer,
                          TitlesEditorSerializer,
                          TitlesReadSerializer,
                          ReviewSerializer,
                          CommentSerializer)
from .utils import send_confirmation_email
from .viewsets import GetPostDeleteViewSet
from .filters import TitleFilter


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Класс представления для модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (permissions.IsAuthenticated, IsRoleAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')


class UserMeDetail(generics.RetrieveAPIView, generics.UpdateAPIView):
    """Класс представления для модели User ресурса /me."""

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserMeUpdateSerializer

    def get_object(self):
        username = self.request.user.username
        return get_object_or_404(User, username=username)


class UserSignupTokenDetail(generics.CreateAPIView):
    """Класс представления для модели User ресурсов /signup и /token."""

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if 'token' in self.request.path:
            return UserTokenSerializer
        return UserSignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if 'token' in self.request.path:
            data = {'token': serializer.data['token']}
        else:
            self.perform_create(serializer)
            data = serializer.data
        return Response(data=data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        send_confirmation_email(serializer.validated_data["username"],
                                serializer.validated_data["email"])


class CategoryViewSet(GetPostDeleteViewSet):
    """Класс представления для модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(GetPostDeleteViewSet):
    """Класс представления для модели Genre."""

    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Класс представления для модели Title."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return TitlesEditorSerializer
        return TitlesReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс представления для модели Review."""

    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerAdminModeratorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Класс представления для модели Comment."""

    serializer_class = CommentSerializer
    permission_classes = (IsOwnerAdminModeratorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        review = get_object_or_404(
            Review, pk=self.kwargs.get("review_id"),
            title__pk=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
