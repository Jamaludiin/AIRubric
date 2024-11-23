from django.contrib import admin

# Register your models here.
from .models import Document, Analysis, Question

admin.site.register(Document)

admin.site.register(Analysis)

admin.site.register(Question)

