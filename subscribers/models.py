from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.utils import timezone

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


    def create_and_send_confirmation_email(self, request):
        """Creates and sends an email containing confirmation link.

        Returns:
            TransactionalEmail object: the confirmation email object
        """

        # Create the confirmation URL
        confirmation_link = create_secure_link(
            request=request,
            user=self,
            viewname='verify_email',
            external=True
        )

        # Create the account confirmation email object
        confirmation_email = self.transactionalemail_set.create(
            subject_line='Please confirm your email address'
        )

        confirmation_email.render_message_body(
            template='email_alerts/confirmation_email.html',
            context={'confirmation_link': confirmation_link}
        )

        # Send the above email
        process_and_send_email.delay(email_id=confirmation_email.pk)

        return confirmation_email


    @staticmethod
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


    def create_and_send_welcome_email(self, request):
        """Creates and sends out welcome email to user.

        The email is sent once a user successfully verifies her email 
        address.

        Returns:
            TransactionalEmail object: the welcome email object
        """
        unsubscribe_link = create_secure_link(
            request=request,
            user=self,
            viewname='unsubscribe_user',
            external=True
        )

        welcome_email = self.transactionalemail_set.create(
            subject_line='Welcome to DC Alerts!'
        )

        welcome_email.render_message_body(
            template='email_alerts/welcome_email.html',
            context={
                'recipient': self,
                'unsubscribe_link': unsubscribe_link
            }
        )

        process_and_send_email.delay(email_id=welcome_email.pk)

        return welcome_email


    def create_and_send_goodbye_email(self, request):
        """Creates and sends out goodbye email to user.

        This email is sent after a user successfully unsubscribes.

        Returns:
            TransactionalEmail object: the goodbye email object
        """
        goodbye_email = self.transactionalemail_set.create(
            subject_line='You have successfully unsubscribed'
        )
        goodbye_email.render_message_body(
            template='email_alerts/goodbye_email.html',
            context={'recipient': self}
        )

        process_and_send_email.delay(email_id=goodbye_email.pk)

        return goodbye_email


    def create_and_send_optout_email(self, request):
        """Creates and sends out unsubscribe email to user.

        The email is sent after a user requests an unsubscribe email 
        from the optout page.

        Returns:
            TransactionalEmail object: the unsubscribe email object
        """
        unsubscribe_link = create_secure_link(
            request=request,
            user=self,
            viewname='unsubscribe_user',
            external=True
        )

        optout_email = self.transactionalemail_set.create(
            subject_line='Unsubscribe from our mailing list'
        )
        optout_email.render_message_body(
            template='email_alerts/optout_email.html',
            context={
                'recipient': self,
                'optout_link': unsubscribe_link
            }
        )

        process_and_send_email.delay(email_id=optout_email.pk)

        return optout_email
