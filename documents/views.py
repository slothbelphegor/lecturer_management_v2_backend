from django.shortcuts import render
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from .models import *


class DocumentPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class DocumentFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    document_type_name = filters.CharFilter(lookup_expr='icontains')
    published_by = filters.CharFilter(lookup_expr='icontains')
    signed_by = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Document
        fields = ['name', 'document_type_name', 'published_by', 'signed_by']


class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = DocumentType.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        if not serializer.data:
            return Response({"error": "No document type found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except DocumentType.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        try:
            document_type = self.queryset.get(pk=pk)
            serializer = self.serializer_class(
                document_type, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except DocumentType.DoesNotExist:
            return Response({"error": "Document type not found"}, status=404)

    def destroy(self, request, pk=None):
        try:
            document_type = self.queryset.get(pk=pk)
            document_type.delete()
            return Response(status=204)
        except DocumentType.DoesNotExist:
            return Response({"error": "Document type not found"}, status=404)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    pagination_class = DocumentPagination
    filter_backends = [
        rest_filters.SearchFilter,
        rest_filters.OrderingFilter
    ]
    filterset_class = DocumentFilter
    search_fields = ["name", "published_by",
                     "signed_by", "document_type__name"]
    ordering_fields = ["name", "published_at",
                       "valid_at", "uploaded_at", "updated_at"]
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = Document.objects.all()

        # Apply search filter and ordering
        queryset = self.filter_queryset(queryset)

        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        # If no pagination, return all results
        serializer = self.serializer_class(queryset, many=True)
        if not serializer.data:
            return Response({"error": "No documents found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        try:
            document = self.queryset.get(pk=pk)
            serializer = self.serializer_class(document, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

    def destroy(self, request, pk=None):
        try:
            document = self.queryset.get(pk=pk)
            document.delete()
            return Response(status=204)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)
