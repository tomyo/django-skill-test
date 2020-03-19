from django.urls import path
from . import apis

urlpatterns = [
  path('<str:word>', apis.letter_digit, name="letter_digit")
]

