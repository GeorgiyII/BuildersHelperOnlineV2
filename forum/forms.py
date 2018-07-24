from django import forms
from forum.models import *


class MessageForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Message.objects.all(), widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Message
        fields = ('message_text', 'message_theme', 'parent', 'message_author')
        widgets = {
            'message_text': forms.Textarea(attrs={'rows': 3, 'cols': 60}),
            'message_theme': forms.TextInput(),
            'message_author': forms.TextInput(),
        }

