from django.urls import path
from . import apis

urlpatterns = [
  path('', apis.user_birthdays, name="user_birthdays"),
  path('avg_age', apis.user_birthdays_avg_age, name="user_birthdays_average")
]