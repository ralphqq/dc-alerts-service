from django.shortcuts import redirect, render, reverse
from django.utils import timezone
from django.views import View

from notices.models import OutageNotice
from subscribers.forms import SignupForm


class HomepageView(View):

    def get(self, request):
        recent_alerts = OutageNotice.objects.filter(
            scheduled_for__gt=timezone.now()
        ).order_by('scheduled_for')
        form = SignupForm()
        return render(
            request,
            'homepage/index.html',
            {'form': form, 'recent_alerts': recent_alerts}
        )
