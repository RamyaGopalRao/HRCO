from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .forms import DocumentForm
from .models import Document
from django.conf import settings
from openai import OpenAI
from django.contrib import admin
from django.contrib.auth import login
import os
import pandas as pd


from django.contrib.auth import authenticate, login
def get_openai_api_key():
    try:
        with open(os.path.join(settings.BASE_DIR, 'openai_key.txt'), 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading API key: {e}")
        return None

def admin_login_redirect(request):
    if request.user.is_authenticated:
        return redirect('upload_page')  # Redirect to the upload page
    else:
        return admin.site.login(request)

@login_required
def upload_document(request):
    try:
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                document = form.save(commit=False)
                document.reference_link = request.build_absolute_uri(document.file.url)
                document.save()
                return redirect('upload_document')
        else:
            form = DocumentForm()
            return redirect('login')

        documents = Document.objects.all()
        return render(request, 'chatbot/upload.html', {'form': form, 'documents': documents})
    except ValidationError as e:
        form.add_error(None, str(e))
        documents = Document.objects.all()
        return render(request, 'chatbot/upload.html', {'form': form, 'documents': documents})
    except Exception as e:
        return render(request, 'chatbot/upload.html', {'form': form, 'documents': [], 'error': str(e)})

@login_required
def preprocess_documents():
    documents = []
    for document in Document.objects.all():
        try:
            with open(document.file.path, 'r') as file:
                documents.append(file.read())
        except Exception as e:
            print(f"Error reading document {document.file.path}: {e}")
    return documents

@login_required
def chat(request):
    try:
        if request.method == 'POST':
            user_input = request.POST.get('message')
            documents = preprocess_documents()
            response = ask_openai(user_input, documents)
            return JsonResponse({"response": response})
    except Exception as e:
        return JsonResponse({"error": str(e)})

def ask_openai(question, documents):
    try:
        context = "\n\n".join(documents)
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        api_key = get_openai_api_key()
        if api_key is None:
            return "API key not found."

        client = OpenAI(
            api_key=api_key
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        bottext = response.choices[0].message.content.strip()
        trimmed_str = bottext.replace('```json\n', '').replace('```', '')
        return trimmed_str
    except Exception as e:
        return str(e)

@login_required
def chatbot_interface(request):
    return render(request, 'chatbot/chat.html')
