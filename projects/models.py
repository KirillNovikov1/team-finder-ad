from django.conf import settings
from django.db import models


PROJECT_NAME_MAX_LENGTH = 200
PROJECT_STATUS_MAX_LENGTH = 6

PROJECT_STATUS_OPEN = "open"
PROJECT_STATUS_CLOSED = "closed"


class Project(models.Model):
    STATUS_CHOICES = [
        (PROJECT_STATUS_OPEN, "Open"),
        (PROJECT_STATUS_CLOSED, "Closed"),
    ]

    name = models.CharField(
        "название проекта",
        max_length=PROJECT_NAME_MAX_LENGTH,
    )
    description = models.TextField(
        "описание проекта",
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="автор проекта",
        related_name="owned_projects",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        "дата создания",
        auto_now_add=True,
    )
    github_url = models.URLField(
        "ссылка на GitHub",
        blank=True,
    )
    status = models.CharField(
        "статус",
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="участники проекта",
        related_name="participated_projects",
        blank=True,
    )

    class Meta:
        verbose_name = "проект"
        verbose_name_plural = "проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name