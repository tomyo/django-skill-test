from .models import User
from datetime import date
from django.dispatch import receiver  
from django.db.models.signals import pre_save, pre_delete
from .utils import get_avg_age

@receiver([pre_save, pre_delete], sender=User)
def invalidate_avg_age_cache_on_model_change(sender, instance, *args, **kwargs):
  get_avg_age.__defaults__[0]['valid_until'] = date.fromtimestamp(1)
