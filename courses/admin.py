from django.contrib import admin
from django.http import Http404, HttpResponseRedirect

from ordered_model.admin import OrderedModelAdmin

from staff.admin import admin_site
from courses.models import Course, Lesson, Section, Task

class _CustomAdmin(admin.ModelAdmin):
    def response_post_save_change(self, request, obj):
        return HttpResponseRedirect(obj.get_absolute_url())
    
    def response_post_save_add(self, request, obj):
        return HttpResponseRedirect(obj.get_absolute_url())
    

class CourseAdmin(_CustomAdmin):
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


class TaskInline(admin.StackedInline):
    model = Task
    extra = 1
    
    fieldsets = (
        (None, {
            "fields":(
                "description",
                ("after_text", "wrong_text", "skip_text", "commentary"),
                ("hidden_pre_code", "visible_pre_code"),
                ("model_answer"),
                ("validate_answer", "post_code"),
                ("language", "uses_random", "uses_image", "automark")
            )
        }),
    )

class SectionAdmin(OrderedModelAdmin, _CustomAdmin):
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
