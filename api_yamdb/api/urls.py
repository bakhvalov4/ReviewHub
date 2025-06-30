from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, GenreViewSet,
                    TitleViewSet, UserSignupTokenDetail,
                    UserViewSet, UserMeDetail, CommentViewSet,
                    ReviewViewSet)


router_v1 = routers.DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('users', UserViewSet, basename='users')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
router_v1.register((r'titles/(?P<title_id>\d+)/reviews'
                   r'/(?P<review_id>\d+)/comments'),
                   CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/users/me/', UserMeDetail.as_view()),
    path('v1/', include(router_v1.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
    path('v1/auth/signup/', UserSignupTokenDetail.as_view()),
    path('v1/auth/token/', UserSignupTokenDetail.as_view())
]
