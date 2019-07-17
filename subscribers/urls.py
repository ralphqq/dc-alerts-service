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
    path(
        'verify/<str:uid>/<str:token>',
        views.VerifyEmailView.as_view(),
        name='verify_email'
    ),
    path(
        'verification/<str:results>/',
        views.VerificationResultsPageView.as_view(),
        name='verification_results'
    ),
    path(
        'unsubscribe_user/<str:uid>/<str:token>',
        views.UnsubscribeUserView.as_view(),
        name='unsubscribe_user'
    ),
    path(
        'unsubscribe/<str:results>/',
        views.UnsubscribeResultsPageView.as_view(),
        name='unsubscribe_results'
    ),
    path(
        'optout/',
        views.OptOutRequestPageView.as_view(),
        name='optout_request'
    ),
    path(
        'optout/instructions/',
        views.OptOutInstructionsPageView.as_view(),
        name='optout_instructions'
    ),
]