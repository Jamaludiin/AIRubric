from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #is_deleted = models.BooleanField(default=False)


class Analysis(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
