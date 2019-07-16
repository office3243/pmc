from paywix.payu import PAYU
import hashlib
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from payments.models import Payment
from django.contrib import messages
from recharges import alert_messages
from django.contrib.auth.decorators import login_required

import uuid

payu = PAYU()


payu_details = {
    'first_name': "PrintMyCopy",
    "email": "ewayprint.inc@gmail.com",
    "phone": "9028116344",
}


@login_required
def create_payment(request, recharge):
    # hash_object = hashlib.sha256(b'randint(0,20)')
    # txnid = hash_object.hexdigest()[0:20]
    txnid = uuid.uuid4()
    payment_data = recharge.get_payment_info_dict
    payment = Payment.objects.initiate_payment(txnid=txnid,
                                               amount=payment_data.get('amount'),
                                               product_info=payment_data.get('productinfo'),
                                               recharge=recharge)
    payment_data.update({"txnid": txnid})
    payment_data.update(recharge.get_user_info_dict)
    payu_data = payu.initate_transaction(payment_data)
    return render(request, 'payments/checkout.html', {"posted": payu_data})


@login_required
def recharge_succeed(request, payment):
    messages.success(request, alert_messages.RECHARGE_SUCCEED_MESSAGE)
    return redirect("wallets:view")


@login_required
def recharge_failed(request, payment):
    messages.warning(request, alert_messages.RECHARGE_FAILED_MESSAGE)
    return redirect("wallets:view")


@csrf_protect
@csrf_exempt
def payment_success(request):
    payu_success_data = payu.check_hash(dict(request.POST))
    txnid = payu_success_data.get('data').get('txnid')
    amount = payu_success_data.get('data').get('amount')
    payment = Payment.objects.search_payment(txnid=txnid, amount=amount, wallet_id=request.user.get_wallet.id)
    if payment is None:
        raise Http404("Bad Request")
    else:
        payment.succeed()
        return recharge_succeed(request, payment)


@csrf_protect
@csrf_exempt
def payment_failure(request):
    payu_failure_data = payu.check_hash(dict(request.POST))
    txnid = payu_failure_data.get('data').get('txnid')
    amount = payu_failure_data.get('data').get('amount')
    payment = Payment.objects.search_payment(txnid=txnid, amount=amount, wallet_id=request.user.get_wallet.id)
    if payment is None:
        raise Http404("Bad Request")
    else:
        payment.failed()
        return recharge_failed(request, payment)

