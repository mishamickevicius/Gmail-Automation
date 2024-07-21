from django import forms

class EmailForm(forms.Form):
    to = forms.EmailField(required=True)
    subject = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'auto-resize'}),required=True)

