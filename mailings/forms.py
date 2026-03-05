"""
Формы для приложения mailings.
"""
from django import forms

from mailings.models import Mailing, Message, Recipient


class MessageForm(forms.ModelForm):
    """Форма для создания/редактирования сообщения."""

    class Meta:
        model = Message
        fields = ('subject', 'body')
        widgets = {
            'body': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class RecipientForm(forms.ModelForm):
    """Форма для создания/редактирования получателя."""

    class Meta:
        model = Recipient
        fields = ('email', 'full_name', 'comment')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MailingForm(forms.ModelForm):
    """Форма для создания/редактирования рассылки."""

    class Meta:
        model = Mailing
        fields = ('start_time', 'end_time', 'message', 'recipients')
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'recipients': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # показываем только свои сообщения и получателей
            self.fields['message'].queryset = Message.objects.filter(owner=user)
            self.fields['recipients'].queryset = Recipient.objects.filter(owner=user)
        self.fields['message'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError('Дата окончания должна быть позже даты начала.')
        return cleaned_data
