from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
import stripe
from datetime import datetime



stripe.api_key = settings.STRIPE_API_KEY

MEMBERSHIP_CHOICES =  (
  ('Enterprize', 'Enterprize'),
  ('Professional', 'Professional'),
  ('Free', 'Free'),
)

class Membership(models.Model):
  slug = models.SlugField(max_length=50)
  membership_type = models.CharField(max_length=30, choices=MEMBERSHIP_CHOICES, default='Free')
  price = models.DecimalField(max_digits=9, decimal_places=2, default=15.0)
  stripe_plan_id = models.CharField(max_length=40)

  def __str__(self):
    return self.membership_type


class UserMembership(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  stripe_customer_id = models.CharField(max_length=40)
  membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True)

  def __str__(self):
    return self.user.username


def post_save_usermembership_create(sender, instance, created, *args, **kwargs):
  if created:
    UserMembership.objects.get_or_create(user=instance)
  
  user_membership, created = UserMembership.objects.get_or_create(user=instance)

  if user_membership.stripe_customer_id is None or user_membership.stripe_customer_id == '':
    new_customer_id = stripe.Customer.create(email=instance.email)
    user_membership.stripe_customer_id = new_customer_id['id']
    user_membership.save()


post_save.connect(post_save_usermembership_create, sender=settings.AUTH_USER_MODEL)



class Subscription(models.Model):
  user_membership =  models.ForeignKey(UserMembership, on_delete=models.CASCADE)
  stripe_subscription_id = models.CharField(max_length=40)
  active = models.BooleanField(default=True)

  def __str__(self):
    return self.user_membership.user.username

  @property
  def  get_created_date(self):
    subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
    return datetime.fromtimestamp(subscription.created)
  
  @property
  def get_next_billing_date(self):
    subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
    return datetime.fromtimestamp(subscription.current_period_end)


