from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import PROJECT_STATUS_CLOSED, PROJECT_STATUS_OPEN, Project


PROJECTS_PER_PAGE = 12


def paginate_queryset(request, queryset):
    paginator = Paginator(queryset, PROJECTS_PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def get_project_by_pk(pk):
    return Project.objects.filter(pk=pk).first()


def get_project_with_related_by_pk(pk):
    return (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants")
        .filter(pk=pk)
        .first()
    )


def project_not_found_response():
    return JsonResponse(
        {
            "status": "error",
            "message": "Проект не найден.",
        },
        status=HTTPStatus.NOT_FOUND,
    )


def project_list_view(request):
    projects_queryset = (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )

    page_obj = paginate_queryset(request, projects_queryset)

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
        },
    )


@login_required
def favorite_projects_view(request):
    projects_queryset = (
        request.user.favorites
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )

    page_obj = paginate_queryset(request, projects_queryset)

    return render(
        request,
        "projects/favorite_projects.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
        },
    )


def project_detail_view(request, pk):
    project = get_project_with_related_by_pk(pk)

    if project is None:
        return project_not_found_response()

    return render(
        request,
        "projects/project-details.html",
        {
            "project": project,
        },
    )


@login_required
def project_create_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def project_edit_view(request, pk):
    project = get_project_by_pk(pk)

    if project is None:
        return project_not_found_response()

    if project.owner != request.user and not request.user.is_staff:
        return redirect("projects:project_detail", pk=project.pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            project = form.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": True,
        },
    )


@login_required
@require_POST
def project_complete_view(request, pk):
    project = get_project_by_pk(pk)

    if project is None:
        return project_not_found_response()

    if project.owner == request.user and project.status == PROJECT_STATUS_OPEN:
        project.status = PROJECT_STATUS_CLOSED
        project.save(update_fields=["status"])
        return JsonResponse(
            {
                "status": "ok",
                "project_status": PROJECT_STATUS_CLOSED,
            },
        )

    return JsonResponse(
        {
            "status": "error",
        },
        status=HTTPStatus.FORBIDDEN,
    )


@login_required
@require_POST
def toggle_favorite_view(request, pk):
    project = get_project_by_pk(pk)

    if project is None:
        return project_not_found_response()

    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True

    return JsonResponse(
        {
            "status": "ok",
            "favorited": favorited,
        },
    )


@login_required
@require_POST
def toggle_participate_view(request, pk):
    project = get_project_by_pk(pk)

    if project is None:
        return project_not_found_response()

    if request.user == project.owner:
        return JsonResponse(
            {
                "status": "error",
                "message": "Автор проекта уже является участником.",
            },
            status=HTTPStatus.FORBIDDEN,
        )

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True

    return JsonResponse(
        {
            "status": "ok",
            "participant": participant,
        },
    )