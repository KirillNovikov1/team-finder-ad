from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен.")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            surname=surname,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name="Admin", surname="User", password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя is_staff должен быть True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("У суперпользователя is_superuser должен быть True.")

        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        "email",
        unique=True,
    )
    name = models.CharField(
        "имя",
        max_length=124,
    )
    surname = models.CharField(
        "фамилия",
        max_length=124,
    )
    avatar = models.ImageField(
        "аватар",
        upload_to="avatars/",
        blank=True,
        null=True,
    )
    phone = models.CharField(
        "телефон",
        max_length=12,
        unique=True,
        blank=True,
        null=True,
    )
    github_url = models.URLField(
        "GitHub",
        blank=True,
    )
    about = models.TextField(
        "о себе",
        max_length=256,
        blank=True,
    )
    favorites = models.ManyToManyField(
        "projects.Project",
        verbose_name="избранные проекты",
        related_name="interested_users",
        blank=True,
    )
    is_active = models.BooleanField(
        "активен",
        default=True,
    )
    is_staff = models.BooleanField(
        "администратор",
        default=False,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} {self.surname}"