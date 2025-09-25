from datetime import date
from django.shortcuts import render
from django.db.models import Q, Count
from django.contrib.auth.models import Group
from rest_framework import viewsets, permissions ,status
from .serializers import *
from .models import *
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication


class CoursePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

# Create your views here.
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePagination
    authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'code', 'credits']
    search_fields = ['name', 'code', 'credits']
    ordering_fields = ['name', 'code', 'credits']
    
    view_permissions = {
        'list,all_courses,lecturer_count': {
            'user': True,
            
        },
        'retrieve,update,create,destroy': {
            'education_department': True,
        },
    }

    def list(self, request):
        queryset = Course.objects.all()
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
            return Response({"error": "No courses found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)

    # Get all courses (not paginated)
    @action(detail=False, methods=['get'], url_path='all_courses')
    def all_courses(self, request):
        queryset = Course.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        if not serializer.data:
            return Response({"error": "No courses found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='lecturer_count')
    def lecturer_count(self, request):
        lecturer_group = Group.objects.filter(name='lecturer').first()
        # Filter lecturers in the 'lecturer' group
        lecturer_queryset = Lecturer.objects.filter(
            Q(user__groups=lecturer_group) |
            Q(status="Đã ký hợp đồng")
        )
        # Annotate each Course with the count of lecturers in the filtered queryset
        courses = Course.objects.annotate(
            lecturer_count=Count(
                'lecturer',
                filter=Q(lecturer__in=lecturer_queryset)
            )
        ).values('name', 'lecturer_count')
        return Response(list(courses))
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=404)
    
    def update(self, request, pk=None):
        try:
            Course = self.queryset.get(pk=pk)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(Course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            Course = self.queryset.get(pk=pk)
            Course.delete()
            return Response(status=204)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=404)

        
class LecturerPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class LecturerViewSet(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    pagination_class = LecturerPagination
    authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'status', 'degree', 'specialization', 'phone_number', 'email', 'address']
    search_fields = ['name', 'status', 'degree', 'specialization', 'phone_number', 'email', 'address']
    ordering_fields = ['name', 'status', 'degree', 'specialization', 'phone_number', 'email', 'address']
    view_permissions = {
        'me': {
            'user': True,
        },
        'list': {
            'lecturer': True,
            'potential_lecturer': True,
            'it_faculty': True,
            'education_department': True,
            'supervision_department': True,
        },
        'retrieve,all_lecturers': {
            'education_department': True,
            'it_faculty': True,
            'supervision_department': True
        },
        'create,update,destroy': {
          'education_department': True  
        },
        'potential_lecturers,partial_update,count_potential_lecturers': {
            'it_faculty': True,
            'education_department': True,
        },
        'sign_contract,count_pending_lecturers': {
            'education_department': True,
        },
        'degree_count,title_count,count_all_lecturers': {
            'user': True,
        },
    }
    
    def list(self, request):
        lecturer_group = Group.objects.filter(name='lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(user__groups=lecturer_group) |
            Q(status="Đã ký hợp đồng")
        ).distinct()
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
            return Response({"error": "No lecturers found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def sign_contract(self, request, pk=None):
        """
        Set lecturer status to 'Đã ký hợp đồng' and add user to 'lecturer' group.
        """
        try:
            lecturer = self.get_queryset().get(pk=pk)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)

        # Set status
        lecturer.status = "Đã ký hợp đồng"
        lecturer.save()

        # Add user to 'lecturer' group if not already
        if lecturer.user:
            lecturer_group, _ = Group.objects.get_or_create(name='lecturer')
            if not lecturer.user.groups.filter(name='lecturer').exists():
                lecturer.user.groups.set([lecturer_group])
                lecturer.user.save()

        serializer = self.get_serializer(lecturer)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='potential_lecturers')
    def potential_lecturers(self, request):
        potential_group = Group.objects.filter(name='potential_lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(user__groups=potential_group) |
            ~Q(status="Đã ký hợp đồng")
        ).distinct()
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
            return Response({"error": "No potential lecturers found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)
    
    def partial_update(self, request, pk=None):
        try:
            Lecturer = self.queryset.get(pk=pk)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LecturerStatusSerializer(Lecturer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def sign_contract(self, request, pk=None):
        """
        Set lecturer status to 'Đã ký hợp đồng' and add user to 'lecturer' group.
        """
        try:
            lecturer = self.get_queryset().get(pk=pk)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)

        # Set status
        lecturer.status = "Đã ký hợp đồng"
        lecturer.save()

        # Add user to 'lecturer' group if not already
        if lecturer.user:
            lecturer_group, _ = Group.objects.get_or_create(name='lecturer')
            if not lecturer.user.groups.filter(name='lecturer').exists():
                lecturer.user.groups.set([lecturer_group])
                lecturer.user.save()

        serializer = self.get_serializer(lecturer)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        try:
            Lecturer = self.queryset.get(pk=pk)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(Lecturer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            Lecturer = self.queryset.get(pk=pk)
            Lecturer.delete()
            return Response(status=204)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)
        
    # Get all lecturers (not paginated)
    @action(detail=False, methods=['get'], url_path='all_lecturers')
    def all_lecturers(self, request):
        queryset = Lecturer.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        if not serializer.data:
            return Response({"error": "No lecturers found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get', 'put', 'patch', 'post'], url_path='me')
    def me(self, request):
        try:
            lecturer = Lecturer.objects.get(user=request.user)
            if request.method in ['PUT', 'PATCH', 'POST']:
                serializer = self.get_serializer(lecturer, data=request.data, partial=(request.method == 'PATCH'))
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=400)
            else:  # GET request
                serializer = self.get_serializer(lecturer)
                return Response(serializer.data)
                
        except Lecturer.DoesNotExist:
            if request.method == 'GET':
                # For GET requests, just return a 404 if no lecturer profile exists
                return Response(
                    {"detail": "No lecturer profile found. Please create one."},
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                # For other methods (PUT, PATCH, POST), create a new lecturer
                data = request.data.copy()
                data['user'] = request.user.id
                serializer = self.serializer_class(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=201)
                return Response(serializer.errors, status=400)
    
    @action(detail=False, methods=['get'])
    def count_all_lecturers(self, request):
        lecturer_group = Group.objects.filter(name='lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(user__groups=lecturer_group) |
            Q(status="Đã ký hợp đồng")
        )
        total = queryset.count()
        return Response(total)
    
    @action(detail=False, methods=["get"])
    def count_potential_lecturers(self, request):
        potential_group = Group.objects.filter(name='potential_lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(status="Chưa duyệt hồ sơ") |
            Q(user__groups=potential_group)
        ).distinct()
        count = queryset.count()
        return Response(count)
    
    @action(detail=False, methods=["get"])
    def count_pending_lecturers(self, request):
        potential_group = Group.objects.filter(name='potential_lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(status="Hồ sơ hợp lệ") |
            Q(user__groups=potential_group)
        ).distinct()
        count = queryset.count()
        return Response(count)
    
    @action(detail=False, methods=['get'])
    def degree_count(self, request):
        # Total number of lecturers
        lecturer_group = Group.objects.filter(name='lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(user__groups=lecturer_group) |
            Q(status="Đã ký hợp đồng") 
        )
        total = queryset.count()
        # Group by degree and count lecturers
        data = (
            queryset.values('degree')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        # Calculate percentage for each degree
        result = [
            {
                "degree": item["degree"],
                "percentage": round(item["count"] / total * 100, 2) if total > 0 else 0
            }
            for item in data
        ]
        # Response format: [{"degree": "PhD", "percentage": 40.0}, ...]
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def title_count(self, request):
        # Total number of lecturers
        lecturer_group = Group.objects.filter(name='lecturer').first()
        queryset = Lecturer.objects.filter(
            Q(user__groups=lecturer_group) |
            Q(status="Đã ký hợp đồng") 
        )
        total = queryset.count()
        # Group by title and count lecturers
        data = (
            queryset.values('title')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        # Calculate percentage for each title
        result = [
            {
                "title": item["title"] if item["title"] != "" else "None",
                "percentage": round(item["count"] / total * 100, 2) if total > 0 else 0,
            }
            for item in data
        ]
        # Response format: [{"title": "Professor", "percentage": 40.0}, ...]
        return Response(result)
    

class ClassPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    pagination_class = ClassPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'course.name', 'lecturer.name', 'semester', 'year']
    search_fields = ['name', 'course.name', 'lecturer.name', 'semester', 'year']
    ordering_fields = ['name', 'course.name', 'lecturer.name', 'semester', 'year']
    
    def list(self, request):
        queryset = Class.objects.all()
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
            return Response({"error": "No classes found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Class.DoesNotExist:
            return Response({"error": "Class not found"}, status=404)
    
    def update(self, request, pk=None):
        try:
            Class = self.queryset.get(pk=pk)
        except Class.DoesNotExist:
            return Response({"error": "Class not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(Class, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            Class = self.queryset.get(pk=pk)
            Class.delete()
            return Response(status=204)
        except Class.DoesNotExist:
            return Response({"error": "Class not found"}, status=404)
        
    # Get all classes (not paginated)
    @action(detail=False, methods=['get'], url_path='all_classes')
    def all_classes(self, request):
        queryset = Class.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        if not serializer.data:
            return Response({"error": "No classes found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)


class ScheduleViewSet(viewsets.ModelViewSet): 
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_assigned__name', 'day_of_week', 'start_period', 'location']
    search_fields = ['class_assigned__name', 'day_of_week', 'start_period', 'location']
    ordering_fields = ['class_assigned__name', 'day_of_week', 'start_period', 'location']
    PERIOD_MAPPING = {
        1 : {"start": "07:00", "end": "07:50"},
        2 : {"start": "07:50", "end": "08:40"},
        3 : {"start": "08:50", "end": "09:40"},
        4 : {"start": "09:40", "end": "10:30"},
        5 : {"start": "10:50", "end": "11:40"},
        6 : {"start": "11:40", "end": "12:30"},
        7 : {"start": "13:30", "end": "14:20"},
        8 : {"start": "14:20", "end": "15:10"},
        9 : {"start": "15:30", "end": "16:20"},
        10: {"start": "16:20", "end": "17:10"},
        11: {"start": "17:30", "end": "18:20"},
        12: {"start": "18:20", "end": "19:10"},
        13: {"start": "19:30", "end": "20:20"},
        14: {"start": "20:20", "end": "21:10"},
    }
    view_permissions = {
        'list': {
            'lecturer': True,
            'potential_lecturer': True,
            'it_faculty': True,
            'education_department': True,
            'supervision_department': True,
            
        },
        'retrieve,update,create,destroy': {
            'education_department': True,
        },
    }
    
    
    def list(self, request):
        queryset = Schedule.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Schedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=404)
    
    def update(self, request, pk=None):
        try:
            Schedule = self.queryset.get(pk=pk)
        except Schedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(Schedule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def partial_update(self, request, pk=None):
        try:
            Schedule = self.queryset.get(pk=pk)
        except Schedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(Schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Partial update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            schedule = self.queryset.get(pk=pk)
            schedule.delete()
            return Response(status=204)
        except Schedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=404)
    
    @action(detail=False, methods=["get"], url_path="by-lecturer/(?P<lecturer_id>[^/.]+)")
    def get_schedules_by_lecturer(self, request, lecturer_id=None):
        try:
            schedules = self.queryset.filter(lecturer_id=lecturer_id)
            serializer = self.serializer_class(schedules, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Lecturer.DoesNotExist:
            return Response(
                {"error": "Lecturer not found"},
                status=status.HTTP_404_NOT_FOUND,
            )    
    
    @action(detail=False, methods=['get'], url_path='today')
    def today(self, request):
        today = date.today()
        schedules = self.queryset.filter(start_time__date=today)
        # Prefetch lecturer to avoid N+1 queries
        schedules = schedules.select_related('lecturer')
        result = []
        for schedule in schedules:
            data = self.serializer_class(schedule).data
            # Attach lecturer name
            data['lecturer_name'] = schedule.lecturer.name if schedule.lecturer else None
            result.append(data)
        return Response(result)
    
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        try:
            lecturer = Lecturer.objects.get(user=request.user)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)
        schedules = self.queryset.filter(lecturer=lecturer)
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
                
class EvaluationPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100
    

class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    # permission_classes = [permissions.AllowAny]
    view_permissions = {
        'get_by_lecturer': {
            'it_faculty': True,
            'supervision_department': True,
        },
        'retrieve,update,create,destroy': {
            'supervision_department': True,
            'it_faculty': True,
        },
        'me': {
            'user': True
        }
    }

    def list(self, request):
        queryset = Evaluation.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except Evaluation.DoesNotExist:
            return Response({"error": "Evaluation not found"}, status=404)
    
    def update(self, request, pk=None):
        try:
            evaluation = self.queryset.get(pk=pk)
        except Evaluation.DoesNotExist:
            return Response({"error": "Evaluation not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(evaluation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        try:
            lecturer = Lecturer.objects.get(user=request.user)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)
        evaluations = self.queryset.all()
        serializer = self.serializer_class(evaluations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="by-lecturer/(?P<lecturer_id>[^/.]+)")
    def get_by_lecturer(self, request, lecturer_id=None):
        """
        Custom action to retrieve all lecturers for a given lecturer ID.
        """
        queryset = self.queryset.filter(lecturer_id=lecturer_id)
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
            return Response({"error": "No evaluations found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)

class LecturerRecommendationPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class LecturerRecommendationViewSet(viewsets.ModelViewSet):
    queryset = LecturerRecommendation.objects.all()
    serializer_class = LecturerRecommendationSerializer
    authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'workplace', 'recommender__name', 'status', 'date', 'course_names']
    search_fields = ['name', 'workplace', 'recommender__name', 'status', 'date', 'course_names']
    ordering_fields = ['name', 'workplace', 'recommender__name', 'status', 'date', 'course_names']
    
    view_permissions = {
        'list': {
            'it_faculty': True
        },
        'retrieve,update': {
            'lecturer': True,
            'it_faculty': True
        },
        'create,destroy,me': {
            'lecturer': True
        },
        'count_unchecked': {
            'it_faculty': True
        }
    }
    def list(self, request):
        queryset = LecturerRecommendation.objects.all()
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
            return Response({"error": "No recommendations found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)
    
    
    @action(detail=False, methods=['get'])
    def count_unchecked(self, request):
        queryset = self.queryset.filter(
            status="Chưa được duyệt"
        )
        count = queryset.count()
        return Response(count)
    
    def retrieve(self, request, pk=None):
        print("Retrieve called with pk:", pk)
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data)
        except LecturerRecommendation.DoesNotExist:
            return Response({"error": "Recommendation not found"}, status=404)
    
    
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def update(self, request, pk=None):
        try:
            recommendation = self.queryset.get(pk=pk)
        except LecturerRecommendation.DoesNotExist:
            return Response({"error": "Recommendation not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(recommendation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            recommendation = self.queryset.get(pk=pk)
            recommendation.delete()
            return Response(status=204)
        except LecturerRecommendation.DoesNotExist:
            return Response({"error": "Recommendation not found"}, status=404)
    
    @action(detail=False, methods=['get', 'post', 'put', 'patch', 'delete'])
    def me(self, request):
        try:
            lecturer = Lecturer.objects.get(user=request.user)
        except Lecturer.DoesNotExist:
            return Response({"error": "Lecturer not found"}, status=404)

        # GET: List all recommendations by this lecturer
        if request.method == 'GET':
            queryset = LecturerRecommendation.objects.filter(recommender=lecturer)
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
                return Response({"error": "No recommendations found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.data)

        # POST: Create a new recommendation for this lecturer
        if request.method == 'POST':
            data = request.data.copy()
            data['recommender'] = lecturer.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

        # PUT/PATCH: Update a recommendation by id (must belong to this lecturer)
        if request.method in ['PUT', 'PATCH']:
            rec_id = request.data.get('id')
            if not rec_id:
                return Response({"error": "Recommendation id required"}, status=400)
            try:
                recommendation = LecturerRecommendation.objects.get(id=rec_id, recommender=lecturer)
            except LecturerRecommendation.DoesNotExist:
                return Response({"error": "Recommendation not found"}, status=404)
            serializer = self.get_serializer(recommendation, data=request.data, partial=(request.method == 'PATCH'))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

        # DELETE: Delete a recommendation by id (must belong to this lecturer)
        if request.method == 'DELETE':
            rec_id = request.data.get('id')
            if not rec_id:
                return Response({"error": "Recommendation id required"}, status=400)
            try:
                recommendation = LecturerRecommendation.objects.get(id=rec_id, recommender=lecturer)
            except LecturerRecommendation.DoesNotExist:
                return Response({"error": "Recommendation not found"}, status=404)
            recommendation.delete()
            return Response(status=204)
    

        
    
    