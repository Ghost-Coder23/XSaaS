from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.conversation_list, name='list'),
    path('<int:conversation_id>/', views.chat_view, name='chat'),
    path('start/<int:user_id>/', views.start_conversation, name='start'),
    path('<int:conversation_id>/messages/', views.get_messages_ajax, name='get_messages'),
]
