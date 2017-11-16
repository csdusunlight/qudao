from django.shortcuts import render
from docs.models import Document
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def get_user_doc_list(request):
    docs = Document.objects.filter(user=request.user)
    return render(request, 'doclist.html', {'docs':docs})

@login_required
def create_doc(request):
    return render(request, 'create_update_doc.html',)

@login_required
def update_doc(request, id):
    doc = Document.objects.get(user=request.user, id=id)
    return render(request, 'create_update_doc.html', {'doc':doc})