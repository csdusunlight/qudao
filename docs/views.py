from django.shortcuts import render, redirect
from docs.models import Document
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def get_user_doc_list(request):
    docs = Document.objects.filter(user=request.user)
    return render(request, 'doclist.html', {'docs':docs})

@login_required
def create_doc(request):
    doc = Document.objects.create(user=request.user)
    return redirect('update_doc', id=doc.id)

@login_required
def update_doc(request, id=None):
    if id:
        doc = Document.objects.get(user=request.user, id=id)
    else:
        doc = Document.objects.create(user=request.user)
    return render(request, 'create_update_doc.html', {'doc':doc})

