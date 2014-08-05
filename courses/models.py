from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import defaultfilters
from ordered_model.models import OrderedModel

def _autoslug(c):
    """Given a class, edits its save method to update the slug to the value of the "title" field"""
    def slug(self, *args, **kwargs):
        self.slug = defaultfilters.slugify(self.title)
        super(c, self).save()
    
    c.save = slug
    
    return c


@_autoslug
class Course(models.Model):
    class Meta:
        permissions = (
            ("read_all", "Can see all courses"),
        )
    
    title = models.CharField(max_length=30)
    slug = models.SlugField(blank=True)
    code = models.CharField(max_length=10, blank=True)
    description = models.TextField()
    published = models.BooleanField(default=False)
    users = models.ManyToManyField(User, blank=True)
    
    def __str__(self):
        return "{}: {}".format(self.code, self.title)
    
    def can_see(self, user):
        """Can the given user see this course"""
        if user.has_perm("courses.read_all"): return True
        return self.users.filter(pk=user.pk).exists() and self.published
    
    @staticmethod
    def get_courses(user):
        """Get a list of all courses that the user can see"""
        if user.has_perm("courses.read_all"): return Course.objects.all()
        
        return Course.objects.filter(published=True, users__pk=user.pk)


@_autoslug
class Lesson(OrderedModel):
    class Meta:
        permissions = (
            ("read_all_lesson", "Can see all lessons"),
        )
    
    title = models.CharField(max_length=30)
    slug = models.SlugField()
    introduction = models.TextField()
    closing = models.TextField()
    published = models.BooleanField(default=False)
    answers_published = models.BooleanField(default=False)
    
    course = models.ForeignKey(Course)
    order_with_respect_to = "course"
    
    def __str__(self):
        return self.title


@_autoslug
class Section(OrderedModel):
    title = models.CharField(max_length=30)
    slug = models.SlugField()
    introduction = models.TextField()
    closing = models.TextField()
    
    lesson = models.ForeignKey(Lesson)
    order_with_respect_to = "lesson"
    
    def __str__(self):
        return self.title


class Task(OrderedModel):
    description = models.TextField()
    after_text = models.TextField()
    wrong_text = models.TextField()
    commentary = models.TextField(blank=True)
    language = models.CharField(max_length=10)
    
    hidden_pre_code = models.TextField(blank=True)
    visible_pre_code = models.TextField(blank=True)
    model_answer = models.TextField()
    validate_answer = models.TextField(blank=True)
    post_code = models.TextField(blank=True)
    
    uses_random = models.BooleanField(default=False)
    uses_image = models.BooleanField(default=False)
    answer_exists = models.BooleanField(default=False)
    
    section = models.ForeignKey(Section)
    order_with_respect_to = "section"
    
    def __str__(self):
        return self.description[:50]
