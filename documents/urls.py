from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("documents", DocumentViewSet, basename="documents")
router.register("document_types", DocumentTypeViewSet, basename="document_types")

urlpatterns = router.urls