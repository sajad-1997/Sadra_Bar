from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def tariff(request):
    return render(request, 'tariffs.html')
