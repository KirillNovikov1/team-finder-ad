import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .models import User


RUSSIAN_PHONE_WITH_EIGHT_LENGTH = 11
RUSSIAN_PHONE_DIGITS_AFTER_CODE = 10

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]

    def save(self, commit=True):
        user = User(
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
            email=self.cleaned_data["email"],
        )
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(
                username=email,
                password=password,
            )

            if user is None:
                raise forms.ValidationError("Неверный имейл или пароль.")

            cleaned_data["user"] = user

        return cleaned_data


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not phone:
            return phone

        phone = phone.strip().replace(" ", "").replace("-", "")

        if phone.startswith("8") and len(phone) == RUSSIAN_PHONE_WITH_EIGHT_LENGTH:
            phone = "+7" + phone[1:]

        pattern = rf"^\+7\d{{{RUSSIAN_PHONE_DIGITS_AFTER_CODE}}}$"
        if not re.match(pattern, phone):
            raise forms.ValidationError(
                "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
            )

        queryset = User.objects.filter(phone=phone)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "Пользователь с таким номером телефона уже существует."
            )

        return phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")

        if github_url and "github.com" not in github_url.lower():
            raise forms.ValidationError("Ссылка должна вести на GitHub.")

        return github_url


class UserPasswordChangeForm(PasswordChangeForm):
    pass