from rest_framework import serializers
from .models import *


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class LecturerSerializer(serializers.ModelSerializer):
    # courses = CourseSerializer(many=True)
    course_names = serializers.SerializerMethodField()

    def get_course_names(self, obj):
        return [course.name for course in obj.courses.all()]

    class Meta:
        model = Lecturer
        fields = "__all__"


class ClassSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()
    lecturer_name = serializers.SerializerMethodField()

    def get_course_name(self, obj):
        return obj.course.name

    def get_lecturer_name(self, obj):
        return obj.lecturer.name

    class Meta:
        model = Class
        fields = "__all__"


class ScheduleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    start = serializers.DateTimeField(source='start_time')
    end = serializers.DateTimeField(source='end_time')
    classNames = serializers.SerializerMethodField()

    def get_classNames(self, obj):
        return obj.course.name if obj.course else ""

    def get_title(self, obj):
        return str(obj)

    class Meta:
        model = Schedule
        fields = ("id", "start", "end", "title", 'classNames',
                  'lecturer', 'course', 'place', 'notes')


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = ['id', 'title', 'content', 'date', 'lecturer', 'type']


class RecommenderSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Lecturer
        # Include only the fields you want to expose
        fields = ['name', 'workplace', 'email', 'full_name']

    def get_full_name(self, obj):
        # Assuming the full name is a combination of first and last name
        return f"{obj.name} - {obj.workplace}"


class LecturerRecommendationSerializer(serializers.ModelSerializer):
    course_names = serializers.SerializerMethodField()
    recommender_details = RecommenderSerializer(
        source='recommender', read_only=True, required=False)

    def get_course_names(self, obj):
        return [course.name for course in obj.courses.all()]

    class Meta:
        model = LecturerRecommendation
        fields = "__all__"
        read_only_fields = ['id', 'date']


class LecturerStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = ['status']
