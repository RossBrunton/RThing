from django import forms

class NamespaceUploadForm(forms.Form):
    """For handling uploads"""
    file = forms.FileField()
