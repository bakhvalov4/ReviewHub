from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Comment, Genre, Review, Title
from .utils import get_confirmation_code
from constants import USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH


User = get_user_model()


class UserValideteMeMixin():

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Использовать имя \'me\' запрещено.')
        return username


class UserSerializerMixin(serializers.ModelSerializer, UserValideteMeMixin):
    """Миксин для работы с User."""

    class Meta:
        abstract = True

    def create(self, validated_data):
        user = User(**validated_data)
        if not User.objects.filter(username=user.username).exists():
            password = get_confirmation_code(user.username)
            user.set_password(password)
            user.save()
        return user

    def validate(self, data):
        same_username, same_email = False, False
        username, email = data.get('username'), data.get('email')

        is_username = User.objects.filter(username=username).exists()
        is_email = User.objects.filter(email=email).exists()
        is_username_and_email = User.objects.filter(username=username,
                                                    email=email).exists()

        request = self.context.get('request')
        if request.method == 'PATCH':
            username = request.path.split('/')[-2]
            if username == 'me':
                username = request.user.username
            email = get_object_or_404(User, username=username).email
            if data.get('username') and username == data.get('username'):
                same_username = True
            if data.get('email') and email == data.get('email'):
                same_email = True

        fields = dict()
        if is_username and not is_username_and_email and not same_username:
            fields['username'] = f'Username \'{data["username"]}\' занят.'
        if is_email and not is_username_and_email and not same_email:
            fields['email'] = f'Email \'{data["email"]}\' занят.'
        if fields:
            raise serializers.ValidationError(fields)
        return data


class UserSerializer(UserSerializerMixin):
    """Сериализатор модели User."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)

    def validate_email(self, email):
        if self.context['request'].method == 'POST' and email is None:
            raise serializers.ValidationError(
                'Поле \'email\' является обязательным.')
        if (self.context['request'].method in ('POST', 'PUT', 'PATCH')
                and email == ''):
            raise serializers.ValidationError(
                'Поле \'email\' не может быть пустым.')
        return email

    def validate(self, data):
        self.validate_email(data.get('email'))
        return super().validate(data)


class UserMeUpdateSerializer(UserSerializer):
    """Сериализатор модели User для ресурса /me"""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class UserSignupSerializer(UserSerializerMixin):
    """Сериализатор модели User для ресурса /signup"""

    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z',
                                      max_length=USERNAME_MAX_LENGTH)
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)

    class Meta:
        model = User
        fields = ('email', 'username',)


class UserTokenSerializer(serializers.ModelSerializer):
    """Сериализатор модели User для ресурса /token"""

    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z',
                                      max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField()
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code', 'token')

    def get_token(self, obj):
        username = self.validated_data['username']
        user = get_object_or_404(User, username=username)
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def validate_username(self, username):
        if not User.objects.filter(username=username).exists():
            raise Http404
        return username

    def validate_confirmation_code(self, code):
        username = self.initial_data.get('username')
        if username and code != get_confirmation_code(username):
            raise serializers.ValidationError('Неверный код подтверждения.')
        return code


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitlesReadSerializer(serializers.ModelSerializer):
    """Сериализатор модели Titles для чтения данных."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitlesEditorSerializer(serializers.ModelSerializer):
    """Сериализатор модели Titles."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    description = serializers.CharField(default='')
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, data):
        representation = super().to_representation(data)
        for key, value in representation.items():
            if key == 'genre':
                genre = [Genre.objects.filter(
                    slug=slug).values('name', 'slug').first()
                    for slug in value]
                representation['genre'] = genre
            if key == 'category':
                category = Category.objects.filter(
                    slug=value).values('name', 'slug').first()
                representation['category'] = category
        return representation

    def validate_genre(self, genre):
        if not genre:
            raise serializers.ValidationError(
                'Поле genre не может быть пустым.')
        return genre


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели Review."""

    author = serializers.CharField(default=serializers.CurrentUserDefault())

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(
                    title=title, author=request.user).exists():
                raise ValidationError('Можно оставлять только один '
                                      'отзыв на произведение.')
        return data

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
