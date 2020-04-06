from django.shortcuts import render, reverse, redirect
from django.views.generic import ListView
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
from .models import Membership, UserMembership, Subscription
import stripe

stripe.api_key = settings.STRIPE_API_KEY


def profile_view(request):
  user_membership = get_user_membership(request)
  user_subscription = get_user_subscription(request)
  context = {
    'user_membership': user_membership,
    'user_subscription': user_subscription
  }
  return render(request, 'memberships/profile.html', context)


def get_user_membership(request):
  user_membership_qs = UserMembership.objects.filter(user=request.user)
  if user_membership_qs.exists():
    return user_membership_qs.first()
  return None


def get_user_subscription(request):
  user_subscription_qs = Subscription.objects.filter(user_membership=get_user_membership(request))
  if user_subscription_qs.exists():
    user_subscription = user_subscription_qs.first()
    return user_subscription
  return None


def get_selected_membership(request):
  membership_type = request.session['selected_membership_type']
  selected_membership_qs = Membership.objects.filter(membership_type=membership_type)
  if selected_membership_qs.exists():
    return selected_membership_qs.first()
  return None


class MembershipSelectView(ListView):
  model = Membership
  template_name = 'memberships/membership-list.html'

  def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(**kwargs)
    current_membership = get_user_membership(self.request)
    context['current_membership'] = str(current_membership.membership)
    return context

  def post(self,*args, **kwargs):
    selected_membership_type = self.request.POST.get('membership_type')

    user_membership = get_user_membership(self.request)
    user_subscription = get_user_subscription(self.request)

    selected_membership_qs = Membership.objects.filter(membership_type=selected_membership_type)

    if selected_membership_qs.exists():
      selected_membership = selected_membership_qs.first()

    # Validation
    if  user_membership.membership == selected_membership:
      if user_subscription != None:
        messages.info(self.request, 'You already have this membership. Your next payment is due {}'.format('get from stripe'))
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    # assign to the session
    self.request.session['selected_membership_type'] = selected_membership.membership_type

    return HttpResponseRedirect(reverse('memberships:payment'))


def payment_view(request):
  user_membership = get_user_membership(request)
  selected_membership = get_selected_membership(request)

  if request.method == 'POST':
    try:
      token = request.POST['stripeToken']
      subscription = stripe.Subscription.create(
        customer=user_membership.stripe_customer_id,
        items = [
          {
            'plan': selected_membership.stripe_plan_id
          }
        ],
        default_source = token
      )
      messages.info(request, 'Your payment was successfully')
      return redirect(reverse('memberships:update-transaction', kwargs={'subscription_id': subscription.id}))

    except stripe.error.CardError as e:
      messages.info(request, 'Sorry your card has been declined')

  context = {
    'selected_membership': selected_membership
  }
  return render(request, 'memberships/membership-payment.html', context)


def update_transaction(request, subscription_id):
  user_membership = get_user_membership(request)
  selected_membership = get_selected_membership(request)

  user_membership.membership = selected_membership
  user_membership.save()

  sub, created = Subscription.objects.get_or_create(user_membership=user_membership)
  sub.stripe_subscription_id = subscription_id
  sub.active = True
  sub.save()

  try:
    del request.session['selected_membership_type']
  except:
    pass

  messages.info(request, 'You have successfully creaated {} membership'.format(selected_membership))

  return redirect('/')


def cancel_subscription(request):
  user_subscription = get_user_subscription(request)

  if user_subcription.active == False:
    messages.info(request, 'You dont have active membership plan')
    return redirect('memberships:select-membership')

  stripe.Subscription.delete(user_subscription.stripe_subscription_id)

  user_subscription.active = False
  user_subscription.save()

  free_membership = Membership.objects.filter(membership_type='Free').first()
  user_membership = get_user_membership(request)
  user_membership.membership = free_membership
  user_membership.save()

  messages.info(request, 'Successfully cancelled Membership. We have sent an email')
  # send am email

  return redirect('memberships:select-membership')