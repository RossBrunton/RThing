"""Admin models and such for courses, lessons, sections and tasks

These will automatically be added to staff.admin.admin_site
"""
from django.contrib import admin
from django.forms import ModelForm, ValidationError
from django.http import Http404, HttpResponseRedirect

from ordered_model.admin import OrderedModelAdmin

from staff.admin import admin_site
from courses.models import Course, Lesson, Section, Task
from tasks.utils import validate_execute


class _CustomAdmin(admin.ModelAdmin):
    """Extends model admin to redirect to the get_absolute_url when the model is updated or added"""
    def response_post_save_change(self, request, obj):
        """When an object has been saved, redirect to it's absolute url"""
        return HttpResponseRedirect(obj.get_absolute_url())
    
    def response_post_save_add(self, request, obj):
        """When an object has been added, redirect to it's absolute url"""
        return HttpResponseRedirect(obj.get_absolute_url())
    

class CourseAdmin(_CustomAdmin):
    """Custom admin for courses"""
    fieldsets = (
        (None, {
            "fields":(("title", "code"), "description")
        }),
        
        (None, {
            "fields":("ending", "published")
        })
    )

admin_site.register(Course, CourseAdmin)


class LessonAdmin(OrderedModelAdmin, _CustomAdmin):
    """Custom admin for lessons"""
    list_display = ("title", "course", "order", "move_up_down_links")
    list_filter = ["course"]
    
    fieldsets = (
        (None, {
            "fields":("title", "introduction")
        }),
        
        (None, {
            "fields":("closing", "published", "course")
        })
    )

admin_site.register(Lesson, LessonAdmin)


class TaskAdminForm(ModelForm):
    """A ModelForm for tasks to allow them to validate themselves"""
    def clean(self, *args, **kwargs):
        """Check the task runs, and raise a ValidationError if it doesn't"""
        toRet = super(TaskAdminForm, self).clean(*args, **kwargs)
        
        is_error, err = validate_execute(self.cleaned_data, self.instance)
        if is_error:
            raise ValidationError(u"Model answer encountered error: {}".format(err))
        
        return toRet

class TaskInline(admin.StackedInline):
    """Inline for displaying tasks on section pages"""
    model = Task
    extra = 1
    form = TaskAdminForm
    
    fieldsets = (
        (None, {
            "fields":(
                "description",
                ("after_text", "wrong_text", "skip_text", "commentary"),
                ("hidden_pre_code", "visible_pre_code"),
                ("model_answer"),
                ("validate_answer", "post_code"),
                ("language", "uses_random", "uses_image", "automark", "takes_prior")
            )
        }),
    )

class SectionAdmin(OrderedModelAdmin, _CustomAdmin):
    """Custom admin for sections"""
    list_display = ("title", "lesson", "move_up_down_links")
    list_filter = ["lesson"]
    inlines = [TaskInline]
    
    fieldsets = (
        (None, {
            "fields":("title", "introduction")
        }),
        
        (None, {
            "fields":("closing", "lesson")
        })
    )

admin_site.register(Section, SectionAdmin)
admin_site.register(Task)
