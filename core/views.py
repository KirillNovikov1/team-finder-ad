from django.shortcuts import redirect


def index_redirect(request):
    return redirect("projects:project_list")