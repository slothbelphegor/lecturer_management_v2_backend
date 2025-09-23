from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("courses", CourseViewSet, basename="courses")
router.register("lecturers", LecturerViewSet, basename="lecturers")
router.register("classes", ClassViewSet, basename="classes")
router.register("schedules", ScheduleViewSet, basename="schedules")
router.register("evaluations", EvaluationViewSet, basename="evaluations")
router.register("recommendations", LecturerRecommendationViewSet, basename="recommendations")
urlpatterns = router.urls