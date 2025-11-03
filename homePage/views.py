from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'issuance/base.html'


class StaffOnlyView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'issuance/bijak/issuance_form.html'

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']


def index(request):
    return render(request, 'homePage/index.html')


def tariff(request):
    return render(request, 'homePage/tariffs.html')
