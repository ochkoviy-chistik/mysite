from django import forms


class DocCreationForm (forms.Form):
    valid_extensions = [
        '.pdf', '.doc', '.docx',
    ]

    title = forms.CharField(
        widget=forms.TextInput,
        required=True,
        max_length=255,
    )
    description = forms.CharField(
        widget=forms.Textarea,
        max_length=511,
        required=True,
    )
    file = forms.FileField(
        required=True,
        widget=forms.FileInput,
    )
