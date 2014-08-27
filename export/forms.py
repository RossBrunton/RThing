from django import forms

class ImportForm(forms.Form):
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
