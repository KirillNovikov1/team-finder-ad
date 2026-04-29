from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    ]

    name = models.CharField(
        "название проекта",
        max_length=200,
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
        max_length=6,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
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