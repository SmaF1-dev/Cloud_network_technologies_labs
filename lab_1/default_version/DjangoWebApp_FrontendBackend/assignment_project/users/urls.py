from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('user/', TemplateView.as_view(template_name="users/user_list.html"),name='drag-drop'),
    ]