from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Моделб пользователей"""
    email = models.EmailField(
        _('email address'),
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150
    )


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
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique following'
            ),
        )
