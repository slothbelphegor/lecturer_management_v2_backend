from django.db import models


class DocumentType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Document(models.Model):
    name = models.CharField(unique=True, max_length=100)
    file_link = models.URLField(unique=True, max_length=200)
    published_at = models.DateField(null=True, blank=True)
    valid_at = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_by = models.CharField(max_length=100, null=True, blank=True)
    signed_by = models.CharField(max_length=100, null=True, blank=True)
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name
