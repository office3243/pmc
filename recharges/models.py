from django.db import models
from wallets.models import Wallet
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse_lazy
from django.conf import settings
from .managers import OfferPackManager, RechargeManager
from django.http import Http404

USER_MODEL = settings.AUTH_USER_MODEL


class OfferPack(models.Model):
    name = models.CharField(max_length=16)
    headline = models.CharField(max_length=48)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    balance = models.DecimalField(max_digits=6, decimal_places=2)
    details = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    preference = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.name

    @property
    def get_make_recharge_url(self):
        return reverse_lazy('recharges:create_with_offer_pack', kwargs={'offer_pack_id': self.id})

    @property
    def get_absolute_url(self):
        return reverse_lazy("recharges:offer_pack_detail", kwargs={"offer_pack_id": self.id})

    @property
    def get_display_text(self):
        return self.name

    @property
    def get_headline(self):
        return self.headline

    @property
    def get_price(self):
        return self.price

    @property
    def get_balance(self):
        return self.balance

    @property
    def get_extra_balance(self):
        return (self.balance - self.price)

    objects = OfferPackManager()


class CustomPack(models.Model):
    price = models.DecimalField(max_digits=6, decimal_places=2)
    balance = models.DecimalField(decimal_places=2, max_digits=6)

    def __str__(self):
        return str(self.balance)


class Recharge(models.Model):

    STATUS_CHOICES = (('IN', 'Initiated'), ('SC', 'Success'), ('FL', 'Failed'), ('HD', "Hold"))

    # user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)

    pack_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    pack_id = models.PositiveIntegerField()
    pack = GenericForeignKey('pack_type', 'pack_id')

    created_on = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='IN')

    objects = RechargeManager()

    def __str__(self):
        return "{} - {}".format(self.id, self.pack)

    def get_absolute_url(self):
        return reverse_lazy('recharges:detail', kwargs={'recharge_id': self.id})

    def get_display_text(self):
        return self.__str__()

    def get_headline(self):
        return self.__str__() +" On " + str(self.created_on)

    def verify_recharge(self, amount):
        if self.get_amount == amount:
            return True
        else:
            return False

    @property
    def get_user(self):
        return self.get_wallet.get_user


    @property
    def get_wallet(self):
        return self.wallet

    @property
    def get_amount(self):
        return self.pack.price

    @property
    def get_firstname(self):
        return self.get_user.first_name if self.get_user.first_name else self.get_phone

    @property
    def get_email(self):
        return self.get_user.email if self.get_user.email else "blank@blank.com"

    @property
    def get_phone(self):
        return self.get_user.phone

    @property
    def get_user_info_dict(self):
        return {
                'first_name': self.get_firstname,
                "email": self.get_email,
                "phone": self.get_phone,
            }


    @property
    def get_productinfo(self):
        return "Recharge of {} rs by {} on {}".format(self.get_amount, self.get_firstname, self.created_on)

    @property
    def get_payment_info_dict(self):
        payment_data = {
            'amount': self.get_amount,
            'productinfo': self.get_productinfo
        }
        return payment_data

    def payment_succeed(self):
        self.get_wallet.balance += self.pack.balance
        self.get_wallet.save()
        self.status = 'SC'
        self.save()

    def payment_failed(self):
        self.success = 'FL'
        self.save()

# def add_balance_to_wallet(sender, instance, *args, **kwargs):
