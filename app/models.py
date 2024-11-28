from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='document/')
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #is_deleted = models.BooleanField(default=False)


class Analysis(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# questions and answers details must saved in database, such as questions and answers, date and time, and user, document, chapter, or topic, level[medium, hard, easy], subject, and topic, bloom taxonomylevel[1,2,3,4,5,6,7,8,9,10]
class Question(models.Model):
    question = models.TextField()
    answer = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    chapter = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    level = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    bloom_taxon = models.CharField(max_length=255)
    file = models.FileField(upload_to='question_document/')
    name = models.CharField(max_length=255)