from django.db import models
from users.models import CustomUser
# Create your models here.


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(max_length=1000, blank=True)
    credits = models.IntegerField()

    def __str__(self):
        return self.name


class Lecturer(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    ethnic = models.CharField(max_length=20, blank=True)
    religion = models.CharField(max_length=30, blank=True)
    hometown = models.CharField(max_length=100)
    degree = models.CharField(max_length=20)
    title = models.CharField(max_length=20, blank=True)
    title_detail = models.CharField(max_length=100)
    title_granted_at = models.DateField()
    address = models.CharField(max_length=100)
    work_position = models.CharField(max_length=100)
    workplace = models.CharField(max_length=100)
    quota_code = models.CharField(max_length=200, blank=True)
    salary_coefficient = models.FloatField(blank=True, null=True)
    salary_coefficient_granted_at = models.DateField(blank=True, null=True)
    recruited_at = models.DateField(blank=True, null=True)
    years_of_experience = models.IntegerField(blank=True, null=True)
    exp_academic = models.JSONField(blank=True, null=True)
    exp_language = models.TextField(blank=True)
    exp_computer = models.TextField(blank=True)
    exp_work = models.JSONField(blank=True, null=True)
    researches = models.JSONField(blank=True, null=True)
    published_works = models.JSONField(blank=True, null=True)
    courses = models.ManyToManyField('Course')
    recommender = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    user = models.OneToOneField(
        CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(db_default="Chưa được duyệt", max_length=100)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.workplace}"


class Class(models.Model):
    name = models.TextField(
        max_length=100
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    lecturer = models.ForeignKey(
        Lecturer,
        on_delete=models.CASCADE
    )
    semester = models.IntegerField()
    year = models.TextField(max_length=10)

    def __str__(self):
        return f'{self.name} ({self.course.code} - {self.lecturer.name})'


class Schedule(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    notes = models.CharField(max_length=500, blank=True, null=True)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    place = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.course.name} - {self.place}'


class LecturerRecommendation(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    workplace = models.CharField(max_length=100, blank=True)
    recommender = models.ForeignKey(
        Lecturer, on_delete=models.CASCADE, related_name='recommended_by')
    courses = models.ManyToManyField(Course, blank=True)
    status = models.CharField(max_length=100, default="Chưa được duyệt")
    content = models.TextField(max_length=1000)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.workplace}"


class Evaluation(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=2000)
    date = models.DateField()
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.lecturer.name} - {self.date}"
