from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EditProfileForm, LoginForm, RegisterForm, UserPasswordChangeForm
from .models import User


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect("projects:project_list")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:project_list")


def user_list_view(request):
    participants_queryset = User.objects.all().order_by("-id")
    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter:
        current_user = request.user

        if active_filter == "owners-of-favorite-projects":
            favorite_projects = current_user.favorites.all()
            participants_queryset = User.objects.filter(
                owned_projects__in=favorite_projects,
            ).distinct()

        elif active_filter == "owners-of-participating-projects":
            participated_projects = current_user.participated_projects.all()
            participants_queryset = User.objects.filter(
                owned_projects__in=participated_projects,
            ).distinct()

        elif active_filter == "interested-in-my-projects":
            my_projects = current_user.owned_projects.all()
            participants_queryset = User.objects.filter(
                favorites__in=my_projects,
            ).distinct()

        elif active_filter == "participants-of-my-projects":
            my_projects = current_user.owned_projects.all()
            participants_queryset = User.objects.filter(
                participated_projects__in=my_projects,
            ).distinct()

    participants_queryset = participants_queryset.order_by("-id")

    paginator = Paginator(participants_queryset, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "page_obj": page_obj,
            "active_filter": active_filter,
        },
    )


def user_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = EditProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect("users:user_detail", pk=request.user.pk)
    else:
        form = EditProfileForm(instance=request.user)

    return render(
        request,
        "users/edit_profile.html",
        {
            "form": form,
            "user": request.user,
        },
    )


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = UserPasswordChangeForm(
            user=request.user,
            data=request.POST,
        )

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:user_detail", pk=request.user.pk)
    else:
        form = UserPasswordChangeForm(user=request.user)

    return render(request, "users/change_password.html", {"form": form})