from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .validators import validate_actual_year
from constants import NAME_MAX_LENGTH, SLUG_MAX_LENGTH, MIN_SCORE, MAX_SCORE


User = get_user_model()


class GenreCategoryBaseClass(models.Model):
    """Базовая модель для хранения жанров и категории."""

    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            verbose_name='Название')
    slug = models.SlugField(max_length=SLUG_MAX_LENGTH,
                            verbose_name='ID', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Category(GenreCategoryBaseClass):
    """Модель для хранения категории."""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(GenreCategoryBaseClass):
    """Модель для хранения жанров."""

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель для хранения произведении."""

    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            verbose_name='Название')
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска',
        validators=[validate_actual_year]
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class BaseFeedback(models.Model):
    """Базовая модель для хранения отзывов и комментариев."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
        help_text='Введите текст отзыва'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return self.text

    class Meta:
        abstract = True


class Review(BaseFeedback):
    """Модель для хранения отзывов."""

    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(MIN_SCORE, 'Оценка должна быть от 1 до 10'),
            MaxValueValidator(MAX_SCORE, 'Оценка должна быть от 1 до 10')
        )
    )

    class Meta(BaseFeedback.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(BaseFeedback):
    """Модель для хранения комментарии."""

    review = models.ForeignKey(
        Review,
        verbose_name='Комментарии',
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True
    )

    class Meta(BaseFeedback.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
