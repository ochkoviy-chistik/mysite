from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

from accounts import password_validators

User = get_user_model()


class RegisterForm(forms.ModelForm):
    """
    The default

    """

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'password'
            }
        )
    )
    password_2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'password_2'
            }
        )
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'avatar', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'avatar'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'first_name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'last_name'}),
        }

    def clean_email(self):
        """
        Verify email is available.
        """
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)

        if qs.exists():
            self.fields['email'].widget.attrs['class'] = 'form-control is-invalid'
            raise forms.ValidationError("Эта почта уже используется!")

        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)

        if qs.exists():
            self.fields['username'].widget.attrs['class'] = 'form-control is-invalid'
            raise forms.ValidationError('Этот ник уже занят!')

        return username

    def clean(self):
        """
        Verify both passwords match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")

        if password is not None and password != password_2:
            self.fields['password_2'].widget.attrs['class'] = 'form-control is-invalid'
            self.add_error("password_2", "Пароли должны совпадать!")

        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class UserChangeForm (forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'avatar', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'avatar'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'first_name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'last_name'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')

        qs = User.objects.filter(username=username)

        if qs.exists():
            self.fields['username'].widget.attrs['class'] = 'form-control is-invalid'
            raise forms.ValidationError('Пользователь с этим ником уже существует!')

        return username


class LoginForm (forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
        }),

    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
        }),
    )

    def clean_password(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        try:
            qs = User.objects.get(email=email)

        except ObjectDoesNotExist:
            qs = None

        if qs:
            hashed_password = make_password(password)

            if hashed_password != qs.password:
                self.fields['password'].widget.attrs['class'] = 'form-control is-invalid'

        self.fields['password'].widget.attrs['class'] = 'form-control is-invalid'

        return password


class UserAdminCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'username', 'avatar', 'first_name', 'last_name']

    def clean(self):
        """
        Verify both passwords match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")

        if password is not None and password != password_2:
            self.add_error("password_2", "Your passwords must match")

        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'avatar', 'last_name', 'password', 'is_active', 'admin']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class FloatPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Адресс электронной почты:',
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "class": "form-control",
                "id": "floatingInput",
                "placeholder": "email",
            }
        ),
    )


class SetFloatPasswordForm (SetPasswordForm):
    error_messages = {
        "password_mismatch": _("Пароли должны совпадать!"),
    }
    new_password1 = forms.CharField(
        label=_("Новый пароль"),
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                'class': 'form-control',
                'id': 'floatingPassword',
                'placeholder': 'password'
            }
        ),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("Подтвердите новый пароль"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                'class': 'form-control',
                'id': 'floatingConfirmPassword',
                'placeholder': 'confirm password'
            }
        ),
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            self.fields['new_password1'].widget.attrs['class'] = 'form-control is-invalid'
            self.fields['new_password2'].widget.attrs['class'] = 'form-control is-invalid'

            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )

        errors = password_validators.password_valid(password2, self.user)

        if errors:
            self.fields['new_password1'].widget.attrs['class'] = 'form-control is-invalid'
            self.fields['new_password2'].widget.attrs['class'] = 'form-control is-invalid'

            raise ValidationError(errors)

        return password2
