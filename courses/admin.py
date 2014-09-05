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


class TaskAdminForm(ModelForm):
    """A ModelForm for tasks to allow them to validate themselves"""
    def clean(self, *args, **kwargs):
        """Check the task runs, and raise a ValidationError if it doesn't"""
        toRet = super(TaskAdminForm, self).clean(*args, **kwargs)
        
        # First append semicolons if they don't already have semicolons at the end
        for field in ["hidden_pre_code", "visible_pre_code", "model_answer", "validate_answer", "post_code"]:
            if field in self.cleaned_data and self.cleaned_data[field]:
                if not self.cleaned_data[field].endswith(";"):
                    self.cleaned_data[field] += ";"
        
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
    
    hidden_pre_code = forms.CharField(widget=widgets.Textarea(attrs=_TEXTAREA_SMALL), required=False)
    visible_pre_code = forms.CharField(widget=widgets.Textarea(attrs=_TEXTAREA_SMALL), required=False)
    model_answer = forms.CharField(widget=widgets.Textarea(attrs=_TEXTAREA_SMALL))
    validate_answer = forms.CharField(widget=widgets.Textarea(attrs=_TEXTAREA_SMALL), required=False)
    post_code = forms.CharField(widget=widgets.Textarea(attrs=_TEXTAREA_SMALL), required=False)
    
    after_text = forms.CharField(widget=widgets.Textarea(attrs=_TEXTAREA_MED), required=False)
    wrong_text = forms.CharField(widget=widgets.Textarea(attrs=_TEXTAREA_MED), required=False)
    skip_text = forms.CharField(widget=widgets.Textarea(attrs=_TEXTAREA_MED), required=False)
    commentary = forms.CharField(widget=widgets.Textarea(attrs=_TEXTAREA_MED), required=False)
    

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
    
    fieldsets = TaskInline.fieldsets
    form = TaskAdminForm

admin_site.register(Task, TaskAdmin)
