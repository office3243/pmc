from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import TransactionAddForm, FileAddForm
from django.urls import reverse_lazy
import random
from .models import Transaction, File
from django.views.generic import TemplateView, ListView
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from . import alert_messages
from stations.models import Station
from django.utils import timezone
from stations.models import Station, StationClass
import json
from django.contrib.auth.decorators import login_required


def generate_four_digit_otp():
    return ''.join(random.sample("0123456789", 4)), ''.join(random.sample("0123456789", 4))


def check_unique_otps():
    otp_1, otp_2 = generate_four_digit_otp()

    if Transaction.objects.filter(otp_1=otp_1, otp_2=otp_2).exists():
        return check_unique_otps()
    else:
        return otp_1, otp_2


class TransactionAddView(LoginRequiredMixin, CreateView):

    form_class = TransactionAddForm
    template_name = 'transactions/add.html'
    success_url = reverse_lazy('portal:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rates_dict = StationClass.objects.first().rate.get_rates_dict
        context['rates_dict'] = json.dumps(rates_dict)
        return context

    def form_valid(self, form):

        try:
            file = get_object_or_404(File, uuid=self.kwargs.get("file_uuid"))
            rate = StationClass.objects.first().rate.get_rate(form.cleaned_data.get('color_model'))
            pages = file.pages
            copies = form.cleaned_data.get('copies')
            amount = rate*pages*copies
            file = get_object_or_404(File, uuid=self.kwargs.get("file_uuid"))

            if form.instance.payment_mode == "AC":
                if amount > self.request.user.wallet.balance:
                    messages.warning(self.request, alert_messages.INSUFFICIENT_BALANCE_MESSAGE)
                    return redirect("wallets:view")
                else:
                    self.request.user.wallet.deduct_amount(amount)
            otp_1, otp_2 = check_unique_otps()
            form.instance.otp_1 = otp_1
            form.instance.otp_2 = otp_2
            form.instance.user = self.request.user
            form.instance.amount = amount
            form.instance.file = file
            form.instance.uuid = file.uuid
            form.save()
            messages.success(self.request, alert_messages.TRANSACTION_ADDED_MESSGAE)
            return redirect('transactions:get_otp', otp_1=otp_1, otp_2=otp_2)
        except:
            messages.warning(self.request, alert_messages.GETTING_ISSUES)
            return redirect("transactions:file_add")


class GetOtpView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/get_otp.html'


class TransactionListView(LoginRequiredMixin, ListView):

    model = Transaction
    template_name = 'transactions/list.html'
    context_object_name = 'transactions'

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset().filter(user=self.request.user, is_hidden=False)
        return qs


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = "transactions/detail.html"
    context_object_name = "transaction"
    slug_url_kwarg = "uuid"
    slug_field = "uuid"

    def get_object(self, queryset=None):
        transaction = super().get_object()
        if transaction.user == self.request.user:
            return transaction
        else:
            raise Http404("No Transaction Found")


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "transactions/delete.html"
    model = Transaction
    success_url = reverse_lazy('transactions:list')
    context_object_name = "transaction"
    slug_url_kwarg = "uuid"
    slug_field = "uuid"

    def get_object(self, queryset=None):
        transaction = super().get_object()
        if transaction.user == self.request.user and not transaction.is_printed:
            return transaction
        else:
            raise Http404("No Transaction Found")

    def delete(self, request, *args, **kwargs):
        transaction = self.get_object()
        if transaction.payment_mode == "AC":
            message = alert_messages.TRANSACTION_DELETED_WITH_REFUND_MESSGAE.format(transaction.amount)
            transaction.user.wallet.balance += transaction.amount
            transaction.user.wallet.save()
            messages.success(self.request, message)
        else:
            messages.success(self.request, alert_messages.TRANSACTION_DELETED_MESSGAE)
        return super().delete(request, *args, **kwargs)


class TransactionHideView(LoginRequiredMixin, DeleteView):
    template_name = "transactions/hide.html"
    model = Transaction
    success_url = reverse_lazy('transactions:list')
    context_object_name = "transaction"
    slug_url_kwarg = "uuid"
    slug_field = "uuid"

    def get_object(self, queryset=None):
        transaction = super().get_object()
        if transaction.user == self.request.user and transaction.is_printed and not transaction.is_hidden:
            return transaction
        else:
            raise Http404("No Transaction Found")

    def delete(self, request, *args, **kwargs):
        transaction = self.get_object()
        transaction.is_hidden = True
        transaction.save()
        messages.success(self.request, alert_messages.TRANSACTION_HIDEED_MESSGAE)
        return redirect(self.success_url)


def get_print(request, otp_1, otp_2, station_code):
    station = get_object_or_404(Station, code=station_code)
    try:
        transaction = Transaction.objects.get(otp_1=otp_1, otp_2=otp_2)
        file_printed = transaction.is_printed
        python_dict = {'otp_found': True, 'file_permitted': transaction.is_permitted, 'file_printed': file_printed,
                       'copies': transaction.copies, 'pages': transaction.file.pages,
                       'color_model': transaction.color_model,
                       'amount': transaction.amount, 'payment_mode': transaction.payment_mode,
                       'file_path': transaction.get_file_url}
        transaction.is_printed = True
        transaction.printed_station = station
        transaction.printed_on = timezone.now()
        transaction.save()
        return JsonResponse(python_dict, safe=False)
    except Transaction.DoesNotExist:
        return JsonResponse({'otp_found': False})


@login_required
def file_add(request):

    transaction_form = TransactionAddForm()
    if request.method == 'POST':
        form = FileAddForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            print(file, file.has_error)
            if file.has_error:
                return JsonResponse({'error': True, 'message': alert_messages.FILE_HAS_ERROR_MESSAGE})
            else:
                bw_rate, color_rate = StationClass.objects.first().rate.get_rates_tuple
                return JsonResponse({'error': False, 'message': 'Uploaded Successfully', "file_uuid": file.uuid,
                                     "file_url": file.get_file_url, 'pages': file.pages,
                                     "bw_rate": bw_rate, "color_rate": color_rate})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    else:
        form = FileAddForm()
        return render(request, 'transactions/file_add.html', {'form': form, "transaction_form": transaction_form})
