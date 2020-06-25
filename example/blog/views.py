from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def detail(request, question_id):
    return HttpResponse("You're looking at article %s." % article_id)

def index(request):
    return HttpResponse("List of articles")

