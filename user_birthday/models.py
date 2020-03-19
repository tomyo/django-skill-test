from django import forms
from datetime import date
from django.db import models
from django.conf import settings


class UserAverageAgeManager(models.Manager):
  """Manager to calculate average age of all users"""
  
  def get_avg_age(self, when=None):
    from .utils import get_avg_age  # Import at runtime to avoid circular import error
    return get_avg_age(when if when else date.today())


class User(models.Model):
  first_name = models.CharField(max_length=40)
  last_name = models.CharField(max_length=40)
  email = models.EmailField(max_length=150, unique=True, primary_key=True)
  birthday = models.DateField()

  def serialize_for_API(self):
    # Serialize and convert birthday to given string format
    return {
      'first_name': self.first_name,
      'last_name': self.last_name,
      'email': self.email,
      'birthday': self.birthday.strftime(settings.DATE_FORMAT)
    }
  
  objects = UserAverageAgeManager()  # Replacing default mananger


class UserForm(forms.ModelForm):
  email = forms.EmailField(max_length=100)  # Removing unique constrain to allow upsert
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'birthday']


# JSON Schema to validate post requests
# TODO: build this automatically from model.
json_user_birthday_schema = \
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "first_name": {
        "type": "string"
      },
      "last_name": {
        "type": "string"
      },
      "email": {
        "type": "string",
        "format": "email"
      },
      "birthday": {
        "type": "string",
        "pattern": "^(0?[1-9]|[12][0-9]|3[01])\\.(0?[1-9]|1[012])\\.\\d{4}$"
      }
    },
    "required": [
      "first_name", "last_name", "email", "birthday"
    ]
  }
}