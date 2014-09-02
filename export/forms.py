"""Forms used for POST requests and displaying in pages"""
from django import forms

class ImportForm(forms.Form):
    """Form representing an upload to the import page
    
    Has three fields, text, mode and user_mode.
    
    text is the text that will be imported as a course.
    
    mode is one of:
    - "update" - If the uploaded course exists, change all the values in the upload.
    - "replace" - If the uploaded course exists, delete it and create a new one.
    
    user_mode is one of:
    - "add" - If a user on the course doesn't exist, create that user.
    - "ignore" - If they don't exist, don't add them.
    - "none" - Don't add any users, even if they already exist in the system.
    """
    MODE_UPDATE = "update"
    MODE_REPLACE = "replace"
    
    USER_MODE_ADD = "add"
    USER_MODE_IGNORE = "ignore"
    USER_MODE_NONE = "none"
    
    MODE_CHOICES = (
        (MODE_UPDATE, "Update it, without deleting any lessons, sections or tasks that already exist"),
        (MODE_REPLACE,
            "Replace it, deleting all lessons, sections or tasks that are attached to it (including statistics)"
        )
    )
    
    USER_MODE_CHOICES = (
        (USER_MODE_ADD, "Create a new user"),
        (USER_MODE_IGNORE, "Ignore them"),
        (USER_MODE_NONE, "Do not import users at all"),
    )
    
    text = forms.CharField(widget=forms.Textarea)
    mode = forms.ChoiceField(choices = MODE_CHOICES)
    user_mode = forms.ChoiceField(choices = USER_MODE_CHOICES)
