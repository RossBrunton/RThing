from django import forms

class NamespaceUploadForm(forms.Form):
    """For handling uploads
    
    "Task" files are stored in MEDIA_ROOT and used for lecturer formatting
    "Sandbox" files are stored in NAMESPACE_DIR and used by code
    """
    LOC_TASK = "t"
    LOC_SANDBOX = "s"
    
    LOC_CHOICES = (
        (LOC_TASK, "Descriptions (you can use formatting in task descriptions to display it)"),
        (LOC_SANDBOX, "Code (you can instruct students to load the files from code)")
    )
    
    file = forms.FileField()
    location = forms.ChoiceField(choices = LOC_CHOICES)


class DeleteForm(forms.Form):
    """For deleting those same uploads"""
    basename = forms.CharField()
    location = forms.ChoiceField(choices = NamespaceUploadForm.LOC_CHOICES)
