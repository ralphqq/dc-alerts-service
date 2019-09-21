from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.utils import timezone

from email_alerts.misc import message_components
from email_alerts.tasks import process_and_send_email
from subscribers.utils import create_secure_link, get_uid
from subscribers.tokens import account_activation_token


class SubscriberManager(BaseUserManager):

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('No email address provided.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password is not None:
            user.set_password(password)

        user.save()
        return user


    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must be part of the staff.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser status not set to True.')

        return self._create_user(
            email=email,
            password=password,
            **extra_fields
        )


class Subscriber(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    objects = SubscriberManager()

    def __str__(self):
        return self.email

    @staticmethod
    def get_all_active_subscribers():
        """Filters and returns list of all currently-active contacts.

        Returns:
            A query set of Subscriber instances with `is_active `
            attribute equal to True
        """
        return Subscriber.objects.filter(is_active=True)

    def send_transactional_email(self, request=None, message_type=''):
        """Creates transactional message of given type and sends it to user.

        Args:
            request (Request object): the request passed to the view 
                that called this function.
            message_type (str): the type of transactional message to 
                create and send; can be one of:
                * 'confirm'
                * 'welcome'
                * 'optout'
                * 'goodbye'

        Returns:
            TransactionalEmail object
        """
        if message_type not in message_components:
            raise TypeError(f'{message_type} is not a valid message type.')

        # Create and initialize the transactional email object
        components = message_components[message_type]
        email_obj = self.transactionalemail_set.create(
            subject_line=components['subject'],
            message_type=message_type
        )

        # Define the template context
        context = {}
        context['message_title'] = email_obj.subject_line
        if message_type == 'goodbye':
            context['recipient'] = self
        else:
            secure_link = create_secure_link(
                request=request,
                user=self,
                viewname=components['target_view'],
                external=True
            )
            if message_type == 'confirm':
                context['confirmation_link'] = secure_link
            elif message_type == 'welcome':
                context['recipient'] = self
                context['unsubscribe_link'] = secure_link
            elif message_type == 'optout':
                context['recipient'] = self
                context['optout_link'] = secure_link

        # Render the email body and HTML content
        email_obj.render_email_body(
            template=components['template'],
            context=context if context else None
        )

        # Send the email
        process_and_send_email.delay(email_id=email_obj.pk)
        return email_obj

    def verify_secure_link(uid, token):
        """Checks if uid and token point to a valid user.

        Returns:
            Subscriber: the user if both uid and token are valid
            None: otherwise
        """
        user = None
        try:
            uid_from_url = get_uid(uid)
            user = Subscriber.objects.get(pk=uid_from_url)
        except (TypeError, ValueError, OverflowError, Subscriber.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            return user

        return None
