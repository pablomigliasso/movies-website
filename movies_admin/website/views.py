from django.http import HttpResponse


def welcome(request):
    return HttpResponse("Welcome to Movies Website!")


def test_2(request):
    return HttpResponse("Welcome to Movies Website!")
