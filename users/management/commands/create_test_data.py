from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import User


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей и проекты для проверки TeamFinder."

    def handle(self, *args, **options):
        users_data = [
            {
                "email": "maria@yandex.ru",
                "name": "Мария",
                "surname": "Смирнова",
                "password": "password",
                "phone": "+79000000001",
                "github_url": "https://github.com/maria",
                "about": "Frontend-разработчик, интересуюсь React и UI-дизайном.",
            },
            {
                "email": "ivan@yandex.ru",
                "name": "Иван",
                "surname": "Петров",
                "password": "password",
                "phone": "+79000000002",
                "github_url": "https://github.com/ivan",
                "about": "Backend-разработчик на Python и Django.",
            },
            {
                "email": "anna@yandex.ru",
                "name": "Анна",
                "surname": "Кузнецова",
                "password": "password",
                "phone": "+79000000003",
                "github_url": "https://github.com/anna",
                "about": "Дизайнер интерфейсов и начинающий продуктовый аналитик.",
            },
            {
                "email": "pavel@yandex.ru",
                "name": "Павел",
                "surname": "Орлов",
                "password": "password",
                "phone": "+79000000004",
                "github_url": "https://github.com/pavel",
                "about": "Fullstack-разработчик, люблю pet-проекты и стартапы.",
            },
        ]

        users = []

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults={
                    "name": user_data["name"],
                    "surname": user_data["surname"],
                    "phone": user_data["phone"],
                    "github_url": user_data["github_url"],
                    "about": user_data["about"],
                },
            )

            if created:
                user.set_password(user_data["password"])
                user.save()

            users.append(user)

        projects_data = [
            {
                "name": "StudyBuddy",
                "description": "Веб-приложение для поиска напарников по учёбе и подготовки к экзаменам.",
                "github_url": "https://github.com/example/studybuddy",
                "owner": users[0],
            },
            {
                "name": "PetCare",
                "description": "Сервис для владельцев домашних животных: напоминания о прививках, уходе и визитах к врачу.",
                "github_url": "https://github.com/example/petcare",
                "owner": users[1],
            },
            {
                "name": "TaskFlow",
                "description": "Мини-система управления задачами для небольших команд и учебных проектов.",
                "github_url": "https://github.com/example/taskflow",
                "owner": users[2],
            },
            {
                "name": "FoodShare",
                "description": "Платформа для обмена домашними рецептами и планирования меню на неделю.",
                "github_url": "https://github.com/example/foodshare",
                "owner": users[3],
            },
            {
                "name": "MedNotes",
                "description": "Приложение для структурирования медицинских конспектов и подготовки к зачётам.",
                "github_url": "https://github.com/example/mednotes",
                "owner": users[0],
            },
            {
                "name": "DevPortfolio",
                "description": "Конструктор портфолио для junior-разработчиков с карточками проектов.",
                "github_url": "https://github.com/example/devportfolio",
                "owner": users[1],
            },
            {
                "name": "HabitTracker",
                "description": "Трекер привычек с аналитикой прогресса и системой мотивации.",
                "github_url": "https://github.com/example/habittracker",
                "owner": users[2],
            },
            {
                "name": "LocalEvents",
                "description": "Афиша локальных мероприятий с возможностью поиска команды для участия.",
                "github_url": "https://github.com/example/localevents",
                "owner": users[3],
            },
            {
                "name": "BookClub",
                "description": "Онлайн-клуб для совместного чтения книг, обсуждений и рекомендаций.",
                "github_url": "https://github.com/example/bookclub",
                "owner": users[0],
            },
            {
                "name": "FitnessPlan",
                "description": "Сервис для составления тренировочных планов и поиска спортивного напарника.",
                "github_url": "https://github.com/example/fitnessplan",
                "owner": users[1],
            },
            {
                "name": "EcoMap",
                "description": "Карта экологических инициатив, пунктов переработки и волонтёрских мероприятий.",
                "github_url": "https://github.com/example/ecomap",
                "owner": users[2],
            },
            {
                "name": "TeamFinder Demo",
                "description": "Демонстрационный проект внутри платформы TeamFinder для проверки участия и избранного.",
                "github_url": "https://github.com/example/teamfinder-demo",
                "owner": users[3],
            },
            {
                "name": "AI Notes",
                "description": "Сервис для хранения заметок по машинному обучению, датасетам и экспериментам.",
                "github_url": "https://github.com/example/ai-notes",
                "owner": users[0],
            },
        ]

        projects = []

        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                name=project_data["name"],
                defaults={
                    "description": project_data["description"],
                    "github_url": project_data["github_url"],
                    "owner": project_data["owner"],
                    "status": Project.STATUS_OPEN,
                },
            )

            project.participants.add(project.owner)
            projects.append(project)

        projects[0].participants.add(users[1], users[2])
        projects[1].participants.add(users[0], users[3])
        projects[2].participants.add(users[1])
        projects[3].participants.add(users[0], users[2])

        users[0].favorites.add(projects[1], projects[2], projects[3])
        users[1].favorites.add(projects[0], projects[2])
        users[2].favorites.add(projects[0], projects[1])
        users[3].favorites.add(projects[4], projects[5])

        self.stdout.write(self.style.SUCCESS("Тестовые пользователи и проекты созданы."))
        self.stdout.write("Тестовый пользователь: maria@yandex.ru / password")