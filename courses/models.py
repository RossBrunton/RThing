from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import defaultfilters
from django.core.cache import cache
from ordered_model.models import OrderedModel

import importlib
import settings
import os
from os import path
import six
from collections import OrderedDict

from rthing.utils import py2_str, rand_str

def _autoslug(c):
    """Given a class, edits its save method to update the slug to the value of the "title" field"""
    save_funct = c.save
    def slug(self, *args, **kwargs):
        slug = defaultfilters.slugify(self.title)
        
        # Check if slug already exists
        if c.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            p = 1
            while c.objects.filter(slug="{}-{}".format(slug, p)).exclude(pk=self.pk).exists():
                p += 1
            slug = "{}-{}".format(slug, p)
        
        self.slug = slug
        save_funct(self, *args, **kwargs)
    
    c.save = slug
    
    return c


class TraversableOrderedModel(OrderedModel):
    class Meta:
        abstract = True
    
    def previous(self):
        """Returns the previous object"""
        try:
            return self.get_ordering_queryset().filter(order__lt=self.order).order_by('-order')[0]
        except IndexError:
            return None
    
    def next(self):
        """Returns the next object"""
        try:
            return self.get_ordering_queryset().filter(order__gt=self.order)[0]
        except IndexError:
            return None


# Types for database choices
_IFACE_CHOICES = map(lambda k : (k, settings.IFACES[k][0]), settings.IFACES.keys())

# Cache for interface modules
_iface_cache = {}

def _complete(states):
    """Returns as per Task.complete depending on whether ALL elements of the given list are at least that state
    
    Priority is "none", "skipped", "revealed", "complete"; this returns the lowest priority complete value
    """
    toReturn = "complete"
    for state in states:
        if state == "none": return "none"
        if state == "skipped": toReturn = "skipped"
        if state == "revealed" and toReturn != "skipped": toReturn = "revealed"
    
    return toReturn


@_autoslug
@py2_str
class Course(TraversableOrderedModel):
    class Meta:
        ordering = ["code"]
    
    title = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(blank=True, max_length=35, unique=True)
    code = models.CharField(max_length=10, blank=True)
    description = models.TextField()
    ending = models.TextField(blank=True)
    published = models.BooleanField(default=False)
    users = models.ManyToManyField(User, blank=True)
    
    def __str__(self):
        return u"{}: {}".format(self.code, self.title)
    
    def get_absolute_url(self):
        return reverse("courses:course", kwargs={"course":self.slug})
    
    def can_see(self, user):
        """Can the given user see this course"""
        if user.is_staff: return True
        return self.users.filter(pk=user.pk).exists() and self.published
    
    @staticmethod
    def get_courses(user):
        """Get a list of all courses that the user can see"""
        if user.is_staff: return Course.objects.all()
        
        return Course.objects.filter(published=True, users__pk=user.pk)
    
    def complete(self, user):
        """Returns as per Task.complete depending on whether ALL lessons are at least that state
        
        Priority is "none", "skipped", "revealed", "complete"; this returns the lowest priority complete value
        """
        return _complete([lesson.complete(user) for lesson in self.lessons.all()])
    
    def to_dict(self):
        output = OrderedDict()
        
        output["title"] = self.title
        output["code"] = self.code
        output["description"] = self.description
        output["ending"] = self.ending
        output["published"] = self.published
        output["lessons"] = [l.to_dict() for l in self.lessons.all()]
        output["users"] = [u.username for u in self.users.all()]
        
        return output


@_autoslug
@py2_str
class Lesson(TraversableOrderedModel):
    class Meta:
        ordering = ["course", "order"]
    
    title = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(blank=True, max_length=35, unique=True)
    introduction = models.TextField()
    closing = models.TextField(blank=True)
    published = models.BooleanField(default=False)
    answers_published = models.BooleanField(default=False)
    
    course = models.ForeignKey(Course, related_name="lessons")
    order_with_respect_to = "course"
    
    
    def __str__(self):
        return u"{}: {}".format(self.course.code, self.title)
    
    def get_absolute_url(self):
        return reverse("courses:lesson", kwargs={"course":self.course.slug, "lesson":self.slug})
    
    def can_see(self, user):
        """Can the given user see this lesson"""
        if user.is_staff: return True
        
        return self.course.can_see(user) and self.published
    
    def complete(self, user):
        """Returns as per Task.complete depending on whether ALL tasks are at least that state
        
        Priority is "none", "skipped", "revealed", "complete"; this returns the lowest priority complete value
        """
        return _complete(self.complete_states(user))
    
    def complete_states(self, user):
        """Returns a list of all the states of each section in this lesson"""
        return [section.complete(user) for section in self.sections.all()]
    
    def to_dict(self):
        output = OrderedDict()
        
        output["title"] = self.title
        output["introduction"] = self.introduction
        output["closing"] = self.closing
        output["published"] = self.published
        output["answers_published"] = self.answers_published
        output["sections"] = [s.to_dict() for s in self.sections.all()]
        
        return output


@_autoslug
@py2_str
class Section(TraversableOrderedModel):
    title = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(blank=True, max_length=35, unique=True)
    introduction = models.TextField()
    closing = models.TextField(blank=True)
    
    lesson = models.ForeignKey(Lesson, related_name="sections")
    order_with_respect_to = "lesson"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return u"{}?t={}".format(
            reverse("courses:lesson", kwargs={"course":self.lesson.course.slug, "lesson":self.lesson.slug}),
            self.order+1
        )
    
    def can_see(self, user):
        """Can the given user see this section"""
        return self.lesson.can_see(user)
    
    def complete(self, user):
        """Returns as per Task.complete depending on whether ALL tasks are at least that state
        
        Priority is "none", "skipped", "revealed", "complete"; this returns the lowest priority complete value
        """
        return _complete([task.complete(user) for task in self.tasks.all()])
    
    def to_dict(self):
        output = OrderedDict()
        
        output["title"] = self.title
        output["introduction"] = self.introduction
        output["closing" ] = self.closing
        output["tasks"] = [t.to_dict() for t in self.tasks.all()]
        
        return output

@py2_str
class Task(TraversableOrderedModel):
    description = models.TextField()
    after_text = models.TextField(blank=True)
    wrong_text = models.TextField(blank=True)
    skip_text = models.TextField(blank=True)
    commentary = models.TextField(blank=True)
    language = models.CharField(max_length=10, choices=_IFACE_CHOICES)
    random_id = models.CharField(blank=True, max_length=10)
    
    hidden_pre_code = models.TextField(blank=True)
    visible_pre_code = models.TextField(blank=True)
    model_answer = models.TextField()
    validate_answer = models.TextField(blank=True)
    post_code = models.TextField(blank=True)
    
    uses_random = models.BooleanField(default=False)
    uses_image = models.BooleanField(default=False)
    automark = models.BooleanField(default=True)
    takes_prior = models.BooleanField(default=False)
    
    section = models.ForeignKey(Section, related_name="tasks")
    order_with_respect_to = "section"
    
    def __str__(self):
        return self.description[:50]
    
    def get_absolute_url(self):
        return u"{}?t={}-{}".format(
            reverse("courses:lesson",
                kwargs={"course":self.section.lesson.course.slug, "lesson":self.section.lesson.slug}
            ),
            self.section.order+1,
            self.order+1
        )
    
    def can_see(self, user):
        """Can the given user see this task"""
        return self.section.can_see(user)
    
    @property
    def iface(self):
        """Returns the iface module that this task uses"""
        return get_iface(self.language)
    
    @iface.setter
    def iface(self, value):
        raise RuntimeError("You cannot set the interface directly.")
    
    def as_prior(self):
        """Returns the full code that the task uses for the model answer, for takes_prior
        
        If the previous task has takes_prior, this will include it as well.
        """
        prior = ""
        if self.takes_prior and self.previous():
            prior = self.previous().as_prior()
        
        out = []
        if prior: out += [prior]
        if self.hidden_pre_code: out += [self.hidden_pre_code]
        if self.visible_pre_code: out += [self.visible_pre_code]
        out += [self.model_answer]
        if self.post_code: out += [self.post_code]
        
        return "".join(out)
    
    def get_uot(self, user):
        """Get the UOT for the given user"""
        # Importing here to avoid circular import
        from stats.models import UserOnTask
        return UserOnTask.objects.get_or_create(task=self, user=user)[0]
    
    def prior_seed(self, user):
        """Goes back on the "prior" chain to find a seed to use for this, returns None if there is no seed"""
        if self.takes_prior and self.previous():
            return self.previous().prior_seed(user)
        
        if self.get_uot(user):
            return self.get_uot(user).seed
        
        return None
    
    def random_poison(self):
        """Returns true if this depends on a random number"""
        if self.uses_random:
            return True
        
        if self.takes_prior and self.previous() and self.previous().uses_random:
            return True
        
        return False
    
    def complete(self, user):
        """Returns "complete", "skipped", "revealed" or "none" depending on what the user has done"""
        from stats.models import UserOnTask
        
        uot = self.get_uot(user)
        
        if uot.skipped and uot.state == UserOnTask.STATE_NONE:
            return "skipped"
        
        if uot.state == UserOnTask.STATE_NONE:
            return "none"
        elif uot.state == UserOnTask.STATE_REVEALED:
            return "revealed"
        else:
            return "complete"
    
    def to_dict(self):
        out = OrderedDict()
        
        out["random_id"] = self.random_id
        out["description"] = self.description
        out["after_text"] = self.after_text
        out["wrong_text"] = self.wrong_text
        out["skip_text"] = self.skip_text
        out["commentary"] = self.commentary
        out["language"] = self.language
        out["hidden_pre_code"] = self.hidden_pre_code
        out["visible_pre_code"] = self.visible_pre_code
        out["model_answer"] = self.model_answer
        out["validate_answer"] = self.validate_answer
        out["post_code"] = self.post_code
        out["uses_random"] = self.uses_random
        out["uses_image"] = self.uses_image
        out["automark"] = self.automark
        out["takes_prior"] = self.takes_prior
        
        return out

def get_iface(name):
    if name in _iface_cache:
        return _iface_cache[name]
    
    _iface_cache[name] = importlib.import_module(settings.IFACES[name][1])
    return _iface_cache[name]

@receiver(post_save, sender=Lesson)
def _lesson_saved(sender, instance, created, **kwargs):
    # Make namespace folder
    if not path.isdir(path.join(settings.NAMESPACE_DIR, str(instance.pk))):
        os.mkdir(path.join(settings.NAMESPACE_DIR, str(instance.pk)), 0o750)

@receiver(post_save, sender=Task)
def _task_saved(sender, instance, created, **kwargs):
    # Remove its cached version from the cache
    cache.delete("task_model_{}".format(instance.pk))
    
    if not instance.random_id:
        # Generate a unique ID
        rid = rand_str(10)
        while Task.objects.filter(random_id=rid):
            rid = rand_str(10)
        instance.random_id = rid
        
        instance.save()
