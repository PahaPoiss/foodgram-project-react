from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    USER_ROLE = [
        (USER, 'user'),
        (ADMIN, 'admin'),
    ]

    username = models.CharField(
        max_length=20,
        verbose_name='Username',
        unique=True
    )

    first_name = models.CharField(
        max_length=20,
        verbose_name='Имя пользователя'
    )

    last_name = models.CharField(
        max_length=20,
        verbose_name='Фамилия пользователя'
    )

    email = models.EmailField('Почта пользователя', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    role = models.CharField(
        'Роль пользователя', max_length=50,
        choices=USER_ROLE, default=USER
    )

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff or self.is_superuser

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
