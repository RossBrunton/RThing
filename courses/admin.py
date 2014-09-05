"""Admin models and such for courses, lessons, sections and tasks

These will automatically be added to staff.admin.admin_site
"""
from django.contrib import admin
from django.forms import ModelForm, ValidationError, widgets
from django import forms
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
    list_display = ("course", "title", "move_up_down_links")
    list_filter = ["course"]
    
    fieldsets = (
        (None, {
            "fields":("title", "introduction")
        }),
        
        (None, {
            "fields":("closing", "published", "answers_published", "course")
        })
    )

admin_site.register(Lesson, LessonAdmin)

def _task_field(attrs, field, required=False):
    """Returns a CharField form with the specified attrs, required and with the help text of the field on Task"""
    
    # This uses the private meta attribute of the model, but there seems to be no other way
    try:
        return forms.CharField(
            widget=widgets.Textarea(attrs=attrs), required=False,
            help_text=Task._meta.get_field_by_name(field)[0].help_text
        )
    except:
        return forms.CharField(widget=widgets.Textarea(attrs=attrs), required=False)

class TaskAdminForm(ModelForm):
    """A ModelForm for tasks to allow them to validate themselves"""
    def clean(self, *args, **kwargs):
        """Check the task runs, and raise a ValidationError if it doesn't"""
        toRet = super(TaskAdminForm, self).clean(*args, **kwargs)
        
        # If there is no model answer, don't bother evaluating it
        if "model_answer" in self.cleaned_data:
            is_error, err = validate_execute(self.cleaned_data, self.instance)
            if is_error:
                raise ValidationError(u"Model answer encountered error: {}".format(err))
        
        return toRet
    
    _TEXTAREA_SMALL = {
        "style":"",
        "rows":1
    }
    
    _TEXTAREA_MED = {
        "style":"",
        "rows":3
    }
    
    hidden_pre_code = _task_field(_TEXTAREA_SMALL, "hidden_pre_code")
    visible_pre_code = _task_field(_TEXTAREA_SMALL, "visible_pre_code")
    model_answer = _task_field(_TEXTAREA_SMALL, "model_answer", True)
    validate_answer = _task_field(_TEXTAREA_SMALL, "validate_answer")
    post_code = _task_field(_TEXTAREA_SMALL, "post_code")
    
    after_text = _task_field(_TEXTAREA_MED, "after_text")
    wrong_text = _task_field(_TEXTAREA_MED, "wrong_text")
    skip_text = _task_field(_TEXTAREA_MED, "skip_text")
    commentary = _task_field(_TEXTAREA_MED, "commentary")
    

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
            ),
        }),
    )

class SectionAdmin(OrderedModelAdmin, _CustomAdmin):
    """Custom admin for sections"""
    list_display = ("course", "lesson", "title", "move_up_down_links")
    list_filter = ["lesson__course", "lesson"]
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


class TaskAdmin(OrderedModelAdmin, _CustomAdmin):
    """Custom admin for sections"""
    list_display = ("course", "lesson", "section", "preview", "move_up_down_links")
    list_filter = ["section__lesson__course", "section"]
    
    fieldsets = (
        (None, {
            "fields":(
                "description",
                ("after_text", "wrong_text", "skip_text", "commentary"),
                ("hidden_pre_code", "visible_pre_code"),
                ("model_answer"),
                ("validate_answer", "post_code"),
                ("language", "section", "uses_random", "uses_image", "automark", "takes_prior")
            ),
        }),
    )
    
    form = TaskAdminForm

admin_site.register(Task, TaskAdmin)
