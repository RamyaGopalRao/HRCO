from django.urls import path
from django.contrib import admin
from .views import upload_document, chat, chatbot_interface,admin_login_redirect

urlpatterns = [
    path('upload/', upload_document, name='upload_document'),
    path('chat/', chat, name='chat'),
    path('', upload_document, name='chatbot_interface'),
    path('admin/', admin.site.urls),
]
