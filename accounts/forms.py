from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('Students', 'Студент'),
        ('Teachers', 'Преподаватель'),
        ('Guests', 'Гость'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Роль')

    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=150, required=True, label='Фамилия')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'middlename', 'phone')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Добавляем пользователя в выбранную группу (если группа существует)
            role_name = self.cleaned_data.get('role')
            try:
                group = Group.objects.get(name=role_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass  # если вдруг группа не создана – ничего страшного
        return user

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middlename', 'phone']