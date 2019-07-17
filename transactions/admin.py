from django.contrib import admin
from .models import Transaction, File


admin.site.site_header = "Print My Copy | Administration"
admin.site.site_title = "Print My Copy"


class FileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "input_file", "converted_file")
    list_filter = ("file_type", "has_error", "transaction__user")


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("get_otps", "payment_mode", "amount", "file", "is_printed")
    list_filter = ("payment_mode", "user", "printed_station", "station_class", "is_printed", "is_permitted",
                   "file__has_error", "created_on", "printed_on")


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(File, FileAdmin)
