from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from foodgram.core.config import Constans


class User(AbstractUser):
    """Моделб пользователей"""
    email = models.EmailField(
        _('email address'),
    )
    first_name = models.CharField(
        _('first name'),
        max_length=Constans.LENGTH_CHAR_FIELD_100
    )
    last_name = models.CharField(
        _('last name'),
        max_length=Constans.LENGTH_CHAR_FIELD_100
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique following'
            ),
        )
