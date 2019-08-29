from django.shortcuts import redirect, render, reverse
from django.views import View

from subscribers.forms import SignupForm


class HomepageView(View):

    def get(self, request):
        form = SignupForm()
        return render(request, 'homepage/index.html', {'form': form})
