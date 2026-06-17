from django import forms
from django.core.validators import EmailValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    Форма обратной связи с валидацией.
    """

    # Валидатор для телефона (поддерживает казахстанские и международные номера)
    phone_validator = RegexValidator(
        regex=r'^\+?[0-9\s\-\(\)]{7,20}$',
        message=_('Введите корректный номер телефона.')
    )

    # Переопределяем поля для кастомизации виджетов и валидации
    name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Ваше имя *'),
            'class': 'form-control',
            'minlength': 2,
            'maxlength': 150,
            # Разрешаем буквы, пробелы, дефисы и апострофы, исключая цифры
            'pattern': r"[A-Za-zА-Яа-яЁё\s\-'’]{2,150}",
            'title': _('Имя от 2 до 150 символов, без цифр')
        }),
        error_messages={
            'required': _('Пожалуйста, укажите ваше имя.'),
            'max_length': _('Имя не должно превышать 150 символов.'),
        }
    )

    email = forms.EmailField(
        required=True,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'placeholder': _('Email адрес *'),
            'class': 'form-control',
            'maxlength': 254
        }),
        error_messages={
            'required': _('Пожалуйста, укажите ваш email.'),
            'invalid': _('Введите корректный email адрес.'),
        }
    )

    phone = forms.CharField(
        max_length=20,
        required=True,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'placeholder': _('Номер телефона *'),
            'class': 'form-control',
            'type': 'tel',
            'inputmode': 'tel',
            'pattern': r"^\+?[0-9\s\-\(\)]{7,20}$",
            'minlength': 7,
            'maxlength': 20,
            'title': _('Телефон от 7 до 20 символов, можно использовать +, пробелы, дефисы и скобки')
        }),
        error_messages={
            'required': _('Пожалуйста, укажите ваш номер телефона.'),
        }
    )

    subject = forms.ChoiceField(
        required=False,
        choices=ContactMessage.MessageSubject.choices,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        initial=ContactMessage.MessageSubject.OTHER
    )

    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': _('Ваше сообщение *'),
            'class': 'form-control',
            'rows': 5,
            'minlength': 10,
            'maxlength': 2000,
            'title': _('Сообщение от 10 до 2000 символов')
        }),
        error_messages={
            'required': _('Пожалуйста, введите ваше сообщение.'),
        }
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']

    def clean_name(self):
        """Дополнительная валидация имени."""
        name = self.cleaned_data.get('name', '').strip()

        if len(name) < 2:
            raise forms.ValidationError(_('Имя должно содержать минимум 2 символа.'))

        # Проверка на недопустимые символы
        if any(char.isdigit() for char in name):
            raise forms.ValidationError(_('Имя не должно содержать цифры.'))

        return name

    def clean_message(self):
        """Дополнительная валидация сообщения."""
        message = self.cleaned_data.get('message', '').strip()

        if len(message) < 10:
            raise forms.ValidationError(_('Сообщение должно содержать минимум 10 символов.'))

        if len(message) > 2000:
            raise forms.ValidationError(_('Сообщение не должно превышать 2000 символов.'))

        # Базовая проверка на спам (слишком много повторяющихся символов)
        if len(set(message)) < 5:
            raise forms.ValidationError(_('Сообщение выглядит подозрительно. Пожалуйста, напишите нормальный текст.'))

        return message

    def clean_email(self):
        """Дополнительная валидация email."""
        from disposable_email_domains import blocklist

        email = self.cleaned_data.get('email', '').lower().strip()

        domain = email.split('@')[-1] if '@' in email else ''
        if domain in blocklist:
            raise forms.ValidationError(_('Пожалуйста, используйте постоянный email адрес.'))

        return email

    def save(self, commit=True, ip_address=None, user_agent=None, user=None):
        """Сохранение с дополнительными метаданными."""
        instance = super().save(commit=False)

        if ip_address:
            instance.ip_address = ip_address

        if user_agent:
            instance.user_agent = user_agent[:500]  # Обрезаем до максимальной длины

        if user and user.is_authenticated:
            instance.user = user

        if commit:
            instance.save()

        return instance
