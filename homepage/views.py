from django.shortcuts import redirect, render, reverse
from django.views import View


class HomepageView(View):

    def get(self, request):
        return render(request, 'homepage/index.html')
