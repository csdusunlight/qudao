from django.shortcuts import render

# Create your views here.

def my_homepage(request):
    return render(request, 'my_homepage.html',)
