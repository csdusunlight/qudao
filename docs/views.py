#coding:utf-8
from django.shortcuts import render, redirect
from docs.models import Document
from django.contrib.auth.decorators import login_required
from public.tools import login_required_ajax
from django.http.response import JsonResponse, Http404

# Create your views here.

@login_required
def get_user_doc_list(request):
    docs = Document.objects.filter(user=request.user)
    return render(request, 'doclist.html', {'docs':docs})

@login_required
def create_doc(request):
    if request.method == "POST":
        doc = Document.objects.create(user=request.user)
        return redirect('update_doc', id=doc.id)
    else:
        raise Http404
@login_required
def update_doc(request, id=None):
    if id:
        doc = Document.objects.get(user=request.user, id=id)
    else:
        doc = Document.objects.create(user=request.user)
    return render(request, 'create_update_doc.html', {'doc':doc})

@login_required_ajax
def duplicate_doc(request, id):
    if request.method == "POST":
        obj = Document.objects.get(user=request.user, id=id)
        doc = Document.objects.create(title=obj.title + u"_副本", content=obj.content, user=request.user)
        ret = {'code':0, 'title':doc.title, 'id':doc.id, 'url':doc.fanshu_url()}
        return JsonResponse(ret)
    else:
        raise Http404
