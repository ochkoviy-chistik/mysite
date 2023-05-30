from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'main.html', {})


def profile(request):
    context = {}
    return render(request, 'profile.html', context)
