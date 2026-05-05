from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import Comment


class CommentCreateForm(forms.ModelForm):
    parent_id = forms.IntegerField(required=False)
    website = forms.CharField(required=False)

    class Meta:
        model = Comment
        fields = ["author_name", "author_email", "content"]

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise ValidationError("invalid")
        return ""

    def clean_author_email(self):
        value = (self.cleaned_data.get("author_email") or "").strip()
        validate_email(value)
        return value

    def clean_content(self):
        value = (self.cleaned_data.get("content") or "").strip()
        if not value:
            raise ValidationError("required")
        if len(value) > 2000:
            raise ValidationError("too_long")
        return value

