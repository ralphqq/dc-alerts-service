from django.urls import path

from . import views


urlpatterns = [
    path(
        'register_email',
        views.RegisterEmailView.as_view(),
        name='register_new_email'
    ),
    path(
        'confirm_email/',
        views.ConfirmEmailPageView.as_view(),
        name='confirm_email_page'
    ),
]