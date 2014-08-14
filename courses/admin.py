from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from courses.models import Course, Lesson, Section, Task

class CourseAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields":(("title", "code"), "description")
        }),
        
        (None, {
            "fields":("ending", "published")
        })
    )

admin.site.register(Course, CourseAdmin)


class LessonAdmin(OrderedModelAdmin):
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

admin.site.register(Lesson, LessonAdmin)


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

class SectionAdmin(OrderedModelAdmin):
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

admin.site.register(Section, SectionAdmin)
admin.site.register(Task)
