from django.conf.urls import url
from . import views

app_name = 'transactions'


urlpatterns = [
    # url(r"^add$", views.TransactionAddView.as_view(), name='add'),

    url(r"^add/(?P<file_uuid>[0-9a-f-]+)/$", views.TransactionAddView.as_view(), name='add'),

    url(r'^get_otp/(?P<otp_1>[0-9]+)/(?P<otp_2>[0-9]+)/$', views.GetOtpView.as_view(),
        name='get_otp'),
    url(r'^list/$', views.TransactionListView.as_view(), name='list'),
    url(r'^detail/(?P<uuid>[0-9a-f-]+)/$', views.TransactionDetailView.as_view(), name='detail'),
    url(r'^delete/(?P<uuid>[0-9a-f-]+)/$', views.TransactionDeleteView.as_view(), name='delete'),
    url(r'^hide/(?P<uuid>[0-9a-f-]+)/$', views.TransactionHideView.as_view(), name='hide'),

    url(r'^getprint/(?P<otp_1>[0-9]+)/(?P<otp_2>[0-9]+)/(?P<station_code>[0-9a-z-]+)/$', views.get_print, name='get_print'),

    url(r'^file/add/$', views.file_add, name="file_add")

]
