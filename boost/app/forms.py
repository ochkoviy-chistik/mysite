from django import forms
from .tags import Subject, Study


class DocCreationForm (forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }
        ),
        required=True,
        max_length=255,
    )
    preview = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
            }
        ),
        required=False,
    )
    subjects = forms.ModelMultipleChoiceField(
        required=True,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'form-check-input'
            }
        ),
        queryset=Subject.objects.all(),
    )
    studies = forms.ModelMultipleChoiceField(
        required=True,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'form-check-input'
            }
        ),
        queryset=Study.objects.all(),
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Description',
            }
        ),
        max_length=511,
        required=True,
    )
    file = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        ),
    )

    def clean_file(self):
        validators = ['pdf', 'docx', 'doc', 'ppt', 'pptx']
        file = self.cleaned_data.get('file')

        if str(file.name).lower().split('.')[-1] not in validators:
            raise forms.ValidationError('Недопустимый тип файла!')

        return file

    def clean_preview(self):
        validators = ['png', 'jpg', 'jpeg', 'webp', 'heic']
        image = self.cleaned_data.get('preview')

        if image is not None and str(image.name).lower().split('.')[-1] not in validators:
            raise forms.ValidationError('Недопустимый формат картинки!')

        return image


class DocEditForm (forms.Form):
    title = forms.CharField(
        widget=forms.TextInput,
        required=True,
        max_length=255,
    )
    preview = forms.ImageField(
        required=False,
    )
    subjects = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Subject.objects.all(),
    )
    studies = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Study.objects.all(),
    )
    description = forms.CharField(
        widget=forms.Textarea,
        max_length=511,
        required=True,
    )
    file = forms.FileField(
        widget=forms.FileInput,
        required=False
    )

    def clean_file(self):
        if self.cleaned_data.get('file'):
            validators = ['pdf', 'docx', 'doc', 'ppt', 'pptx']
            file = self.cleaned_data.get('file')

            if str(file.name).split('.')[-1] not in validators:
                raise forms.ValidationError('недопустимый тип файла')

            return file


class CommentForm (forms.Form):
    comment = forms.CharField(
        widget=forms.TextInput,
        max_length=511
    )


class TagsSortForm (forms.Form):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    studies = forms.ModelMultipleChoiceField(
        queryset=Study.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    sort_type = forms.ChoiceField(
        required=False,
        choices=[
            ('1', 'С высокой оценкой'),
            ('2', 'С низкой оценкой'),
            ('3', 'Новые'),
            ('4', 'Старые'),
        ],
        widget=forms.RadioSelect,
    )


class SearchForm (forms.Form):
    q = forms.CharField(
        label='Поиск по названию',
        widget=forms.TextInput,
        required=False
    )
