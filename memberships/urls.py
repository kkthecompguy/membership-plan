from django.urls import path
from .views import MembershipSelectView, payment_view, update_transaction, profile_view, cancel_subscription

app_name = 'memberships'
urlpatterns = [
  path('', MembershipSelectView.as_view(), name='select-membership'),
  path('payment/', payment_view, name='payment'),
  path('update-transaction/<str:subscription_id>/', update_transaction, name='update-transaction'),
  path('profile/', profile_view, name='profile'),
  path('cancel/', cancel_subscription, name='cancel')
]