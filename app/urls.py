from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='app-home'),
    path('dashboard', views.dashboard, name='app-dashboard'),
    path('playground/', views.playground, name='blog-playground'),


    #path('dashboard/upload/', views.upload, name='app-upload'),


    path('upload/', views.upload_document, name='app-upload'),
    path('ai-analysis/<int:document_id>/', views.ai_analysis, name='ai-analysis'),
    path('review-results/<int:analysis_id>/', views.review_result, name='review-result'),


    path('delete/<int:document_id>/', views.delete_document, name='app-delete'),
    #path('rename/<int:document_id>/', views.rename_document, name='app-rename'),
    path('rename-document/<int:document_id>/', views.rename_document, name='rename-document'),

    #questions and answers
    path('questions-answers/', views.questions_answers, name='questions-answers'),
    path('upload-question-document/', views.upload_question_document, name='app-upload-question-document'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
