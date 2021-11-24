from django import forms
from .models import *
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator

## Create new class form
class CreateClassForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CreateClassForm, self).__init__()
        self.fields["class_name"].label = ""
        self.fields["class_name"].widget.attrs["placeholder"] = "Class Name"

    class_name = forms.CharField(max_length=100, label="Class name")


## create join class form
class JoinClassForm(forms.Form):
    code = forms.CharField(max_length=10, label="code")
