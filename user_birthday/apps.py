from django.apps import AppConfig


class UserConfig(AppConfig):
  name = 'user_birthday'
  def ready(self):
      from .signals import invalidate_avg_age_cache_on_model_change