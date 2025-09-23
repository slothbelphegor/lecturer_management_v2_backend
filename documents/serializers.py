from rest_framework import serializers
from .models import Document, DocumentType

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ('id', 'name')


class DocumentSerializer(serializers.ModelSerializer):
    document_type = serializers.PrimaryKeyRelatedField(queryset=DocumentType.objects.all())
    document_type_name = serializers.CharField(source='document_type.name', read_only=True)
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ('id', 'uploaded_at', 'updated_at')