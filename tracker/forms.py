from django import forms

from .models import Request


class RequestForm(forms.ModelForm):
    urgency = forms.TypedChoiceField(
        choices=[(1, 'Very urgent'), (2, 'Mildly urgent'), (3, 'Not urgent')],
        coerce=int, # turns the submitted value into a number before saving
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    class Meta:
        model = Request
        fields = ['title', 'description', 'urgency']
        # Bootstrap's form-control class styles the inputs.
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
