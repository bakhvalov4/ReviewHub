from django.contrib.auth.models import AbstractUser
from django.db import models

from constants import ROLE_USER, ROLE_MODERATOR, ROLE_ADMIN, ROLE_MAX_LENGTH


USER_ROLES = (
    ('user', ROLE_USER),
    ('moderator', ROLE_MODERATOR),
    ('admin', ROLE_ADMIN),
)


class YamdbUserInterface(AbstractUser):
    """Пользовательская модель для пользователей."""

    bio = models.TextField('Биография', blank=True)
    role = models.CharField(max_length=ROLE_MAX_LENGTH,
                            choices=USER_ROLES,
                            default=ROLE_USER)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == ROLE_MODERATOR or self.is_staff

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
