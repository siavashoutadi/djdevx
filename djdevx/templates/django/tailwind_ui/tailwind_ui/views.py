from django.shortcuts import render


def home(request):
    return render(request, "tailwind_ui/home.html")
