from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from subscribers.models import Subscriber


EMAIL_INPUT_PLACEHOLDER = 'Enter your email address'
BLANK_ITEM_ERROR_MSG = 'Please enter a valid email address'

class InactiveSubscriberFound(Exception):
    """Custom exception raised when inactive user tries to sign up."""
    pass


class SignupForm(forms.ModelForm):

    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': EMAIL_INPUT_PLACEHOLDER,
                'class': 'form-control input-lg'
            })
        }
        error_messages = {
            'email': {'required': BLANK_ITEM_ERROR_MSG}
        }

    def validate_unique(self):
        """Overrides the validate_unique() method."""
        exclude = self._get_validation_exclusions()
        exclude.append('email')
        try:
            self.instance.validate_unique(exclude=exclude)
        except ValidationError as e:
            self._update_errors(e)

    def save(self):
        """Overrides default save() method.

        If the entered email address belongs to an inactive user, 
        this method raises an InactiveSubscriberFound exception. 
        Only unique emails get saved to db.
        """
        try:
            user = Subscriber.objects.get(email=self.instance.email)
            if not user.is_active:
                raise InactiveSubscriberFound
            else:
                raise IntegrityError
        except Subscriber.DoesNotExist:
            return super().save()


class OptOutRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': EMAIL_INPUT_PLACEHOLDER,
            'class': 'form-control input-lg'
        })
    )
