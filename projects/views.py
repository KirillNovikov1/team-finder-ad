from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project


def project_list_view(request):
    projects_queryset = (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )

    paginator = Paginator(projects_queryset, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

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

    paginator = Paginator(projects_queryset, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "projects/favorite_projects.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
        },
    )


def project_detail_view(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=pk,
    )

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
    project = get_object_or_404(Project, pk=pk)

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
    project = get_object_or_404(Project, pk=pk)

    if project.owner == request.user and project.status == Project.STATUS_OPEN:
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=["status"])
        return JsonResponse(
            {
                "status": "ok",
                "project_status": "closed",
            },
        )

    return JsonResponse(
        {
            "status": "error",
        },
        status=403,
    )


@login_required
@require_POST
def toggle_favorite_view(request, pk):
    project = get_object_or_404(Project, pk=pk)

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
    project = get_object_or_404(Project, pk=pk)

    if request.user == project.owner:
        return JsonResponse(
            {
                "status": "error",
                "message": "Автор проекта уже является участником.",
            },
            status=403,
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