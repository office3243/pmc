from __future__ import unicode_literals
from django.db import models
from django.conf import settings
import datetime
from django.db.models.signals import post_save, pre_delete, post_delete
import uuid
from django.urls import reverse_lazy
from .managers import TransactionManager
from django.contrib import messages
from . import alert_messages
from django.core.validators import FileExtensionValidator
from . import converters
import os
from PyPDF2 import PdfFileReader


# SITE_DOMAIN = "http://www.printmycopy.com/"
# SITE_DOMAIN_NAKED = "http://www.printmycopy.com"

# SITE_DOMAIN = "http://127.0.0.1:8000/"
# SITE_DOMAIN_NAKED = "http://127.0.0.1:8000"

SITE_DOMAIN = settings.SITE_DOMAIN
SITE_DOMAIN_NAKED = settings.SITE_DOMAIN_NAKED


MEDIA_PATH = settings.MEDIA_ROOT


USER_MODEL = settings.AUTH_USER_MODEL


class Transaction(models.Model):

    PAYMENT_MODE_CHOICES = (('AC', "Account"), ('CO', "Coin"))
    COLOR_MODEL_CHOICES = (('BW', 'Black&White'), ('CL', 'Colorful'))
    ALLOWED_FILE_TYPES = ("png", "jpg", "jpeg", "pdf")

    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    uuid = models.UUIDField(unique=True)

    otp_1 = models.CharField(max_length=4)
    otp_2 = models.CharField(max_length=4)

    file = models.ForeignKey("File", on_delete=models.CASCADE)

    payment_mode = models.CharField(max_length=2, choices=PAYMENT_MODE_CHOICES)
    color_model = models.CharField(max_length=2, default='BW', choices=COLOR_MODEL_CHOICES)
    copies = models.PositiveSmallIntegerField(default=1)
    station_class = models.ForeignKey('stations.StationClass', on_delete=models.CASCADE, default=1)

    amount = models.DecimalField(decimal_places=2, max_digits=5)

    created_on = models.DateTimeField(auto_now_add=True)

    is_printed = models.BooleanField(default=False)
    printed_on = models.DateTimeField(blank=True, null=True)
    is_hidden = models.BooleanField(default=False)

    printed_station = models.ForeignKey('stations.Station', on_delete=models.PROTECT, blank=True, null=True)

    is_permitted = models.BooleanField(default=True)

    reference = models.CharField(max_length=64, blank=True)

    objects = TransactionManager

    def __str__(self):
        return str(self.user)

    @property
    def get_otps(self):
        return "{} - {}".format(self.otp_1, self.otp_2)

    @property
    def get_absolute_url(self):
        return reverse_lazy("transactions:detail", kwargs={"uuid": self.uuid})

    @property
    def get_delete_url(self):
        return reverse_lazy("transactions:delete", kwargs={"uuid": self.uuid})

    @property
    def get_hide_url(self):
        return reverse_lazy("transactions:hide", kwargs={"uuid": self.uuid})

    @property
    def get_display_text(self):
        if self.reference:
            return self.reference
        else:
            return self.file.name[-30:]

    @property
    def get_file_url(self):
        return SITE_DOMAIN_NAKED + self.file.converted_file.url

    @property
    def calculate_amount(self):
        amount = self.file.pages * self.copies * self.station_class.rate.get_rate(self.color_model)
        return amount


def assign_amount(sender, instance, *args, **kwargs):
    amount = instance.calculate_amount
    if instance.amount != amount:
        instance.amount = amount
        instance.save()

# def refund_amount(sender, instance, *args, **kwargs):
#     if instance.is_permitted and not instance.is_printed and instance.payment_mode == "AC":
#         instance.user.wallet.balance += instance.amount
#         instance.user.wallet.save()
#         instance.is_permitted = False
#         instance.save()
#         instance.delete()
#
#
# pre_delete.connect(refund_amount, sender=Transaction)


post_save.connect(assign_amount, sender=Transaction)


def delete_file(sender, instance, *args, **kwargs):
    if instance.file:
        instance.file.delete()


post_delete.connect(delete_file, sender=Transaction)


class File(models.Model):

    ALLOWED_FILE_TYPES = ("png", "jpg", "jpeg", "pdf")
    FILE_TYPE_CHOICES = (('jpg', 'JPG'), ('png', 'PNG'), ('pdf', 'PDF'), ('txt', 'TXT'), ("jpeg", "JPEG"))
    input_files_path = "transactions/files/input_files/"
    converted_files_path = "transactions/files/converted_files/"

    input_file = models.FileField(upload_to=input_files_path,
                                  validators=[FileExtensionValidator(allowed_extensions=ALLOWED_FILE_TYPES), ])
    converted_file = models.FileField(upload_to=converted_files_path,
                                      validators=[FileExtensionValidator(allowed_extensions=ALLOWED_FILE_TYPES), ],
                                      blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    pages = models.PositiveSmallIntegerField(blank=True, null=True)
    has_error = models.BooleanField(default=False)
    file_type = models.CharField(max_length=3, choices=FILE_TYPE_CHOICES, blank=True)

    @property
    def get_file_ext(self):
        if self.converted_file:
            return self.converted_file.name[(self.converted_file.name.rfind(".")+1):].lower()
        else:
            return self.input_file.name[(self.input_file.name.rfind(".")+1):].lower()

    @property
    def get_pure_name(self):
        return self.input_file.name[(self.input_file.name.rfind("/") + 1): self.input_file.name.rfind(".")]

    @property
    def get_pdf_path(self):
        return self.converted_files_path + self.get_pure_name + ".pdf"

    @property
    def get_jpg_path_temp(self):
        return MEDIA_PATH + self.input_files_path + self.get_pure_name+'.jpg'

    @property
    def get_pdf_path_raw(self):
        return MEDIA_PATH + self.get_pdf_path

    @property
    def convert_input_file(self):
        if self.file_type == "pdf":
            return converters.pdf_converter(self)
        elif self.file_type == "png":
            return converters.png_converter(self)
        elif self.file_type == "jpg":
            return converters.jpg_converter(self)
        elif self.file_type == "jpeg":
            return converters.jpeg_converter(self)
        else:
            pass

    @property
    def get_file_url(self):
        return SITE_DOMAIN_NAKED + self.converted_file.url

    @property
    def count_pdf_pages(self):
        pdf = PdfFileReader(open(self.converted_file.path, 'rb'))
        return pdf.getNumPages()

    def assign_pages(self):
        pages = self.count_pdf_pages
        if self.pages != pages:
            self.pages = pages
            self.save()

    @property
    def temp_method(self):
        return self.get_pure_name

    def save(self, *args, **kwargs):

        if self.file_type != self.get_file_ext:
            self.file_type = self.get_file_ext
            super().save()

        if not self.converted_file:
            converted = self.convert_input_file
            if not converted:
                self.has_error = True
                super().save()
            else:
                super().save()

        if self.converted_file and not self.pages:
            self.assign_pages()
            super().save()


def delete_file_path(sender, instance, *args, **kwargs):
    try:
        if instance.input_file:
            os.remove(instance.input_file.path)
        if instance.converted_file:
            os.remove(instance.converted_file.path)
    except:
        pass


post_delete.connect(delete_file_path, sender=File)
