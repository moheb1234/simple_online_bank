from django.urls import path
from .views import *


urlpatterns = [
    path('create/', create_account),
    path('deposit/', deposit),
    path('withdraw/', withdraw),
    path('fund-transfer/', fund_transfer),
    path('delete/', delete_account),
    path('get-transaction/<int:tracking_number>/', get_transaction),
]
