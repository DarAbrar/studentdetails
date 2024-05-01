from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_excel, name='upload_excel'),
    path('', views.home, name='home'),
    path('get_assigned_candidates/', views.get_assigned_candidates, name='get_assigned_candidates'),
    path('download_skillgap_excel/', views.download_skillgap_excel, name='download_skillgap_excel'),
    path('save_marked_candidate/', views.save_marked_candidate, name='save_marked_candidate'),
    path('marked_candidates/', views.marked_candidates, name='marked_candidates'),
    path('download_youthaspiration_excel/', views.download_youthaspiration_excel, name='download_youthaspiration_excel'),
    path('download_excel/', views.downloadExcel, name="download_excel")
]