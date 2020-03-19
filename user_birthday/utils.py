import json
import datetime
from datetime import date
from calendar import monthrange
from django.conf import settings
from django.db.models import Avg
from json.decoder import JSONDecodeError
from jsonschema import validate, ValidationError
from .models import json_user_birthday_schema, UserForm, User


def get_date_from_long_date_str_format(date_string):
  """ Parse %d.%m.%Y format recieved from json in POST """
  return datetime.datetime.strptime(date_string, settings.DATE_FORMAT).date()

def get_date_from_short_date_str_format(date_string):
  """ This is to parse %d.%m / %d%m format recieved in GET """
  # Try format %d.%m
  if date_string.count('.'):
    return datetime.datetime.strptime(date_string, "%d.%m").date()
  return datetime.datetime.strptime(date_string, "%d%m").date()

def parse_from_to_querystring(fromdm, todm):
  """Returns either (fromdm, todm) date tuple, or (None, None)"""
  error_msg = ''
  if not (fromdm or todm):
    return (None, None)
    
  if fromdm and todm:
    try:
      fromdm = get_date_from_short_date_str_format(fromdm)
      todm = get_date_from_short_date_str_format(todm)
    except ValueError:
      error_msg = 'Bad date format, expected %d%m or %d.%m\n'
  else:
    error_msg = 'None or both values must be provided.'
    error_msg += 'Provided: {}, {}\n'.format(fromdm, todm)

  if error_msg:
    raise ValueError(error_msg)

  return (fromdm, todm)

def refine_query_for_users_in_birthday_range(users_query, fdate, tdate):
  """
  Returns a refined query of users, only including the ones having birthday
  in the given range of dates (day and month).
  """
  assert(type(fdate) == datetime.date)
  assert(type(tdate) == datetime.date)
  return users_query.filter(  # Grabing superset of users, between given months
    birthday__month__gte=fdate.month,
    birthday__month__lte=tdate.month,
  ).exclude(  # Refining head: exluding days before the `from` day, in `from` month
    birthday__month=fdate.month,
    birthday__day__lt=fdate.day,
  ).exclude(  # Refining tail, exluding days after the `to` day, in `to` month
    birthday__month=tdate.month,
    birthday__day__gt=tdate.day,
  )

def is_json_format_valid(json_input):
  try:
      data = json.loads(json_input)
      validate(data, json_user_birthday_schema)
  except (JSONDecodeError, ValidationError) as _:
    return False
  return True
  
def process_users_raw_incomming_data(raw_data):
  """Returns validated and cleaned users data, or ValueError with description"""
  result = []
  error_msg = ""
  if is_json_format_valid(raw_data):
    for user_raw_data in json.loads(raw_data):
      try:
        user_raw_data['birthday'] = get_date_from_long_date_str_format(user_raw_data['birthday'])
        u_form = UserForm(user_raw_data)
        if not u_form.is_valid():
          error_msg = u_form.errors.as_json()
        result.append(u_form.data)
      except ValueError:
        error_msg = json.dumps({'birthday': 'Bad date format, expected: %d.%m.%Y'})
  else:
    error_msg ='Invalid json format.\n'
  if error_msg:
    raise ValueError(error_msg)
  return result

def get_avg_age(when, cache={'result': 0, 'valid_until': date(1970,1,1), 'valid_from': date(1970,1,2)}):
  """`when` argument was introduced just for testing porpuses"""
  assert(type(when) == datetime.date)
  if cache['valid_from'] <= when <= cache['valid_until']:
    return cache['result']
  cache['result'] = _calculate_avg_age(when)
  cache['valid_from'] = when
  cache['valid_until'] = _get_avg_age_last_cache_valid_date(when)
  return cache['result']

def _calculate_avg_age(when):
  """
  This is neither efficient enough, or exact enought (is that's even posible).
  Leap years could be considered, but I think a rough stimation is fear enough.
  """
  assert(type(when) == datetime.date)
  users = User.objects.all()
  if not users:
    return float('nan')
  avg_year = sum([(when - user.birthday).days/365 for user in users]) / len(users)
  return round(avg_year)

def _get_avg_age_last_cache_valid_date(when):
  """
  Either returns the date of the next birthday happening this month,
  or a date for the end of this month.
  """
  assert(type(when) == datetime.date)
  users = User.objects.filter(
    birthday__month=when.month,
    birthday__day__gt=when.day,
  ).order_by('birthday__day')[:1]
  if users:  # Returns the next birthday in `when` month
    birthday = users[0].birthday
    return date(when.year, birthday.month, birthday.day)
  # Returns the last day of `when` month
  return date(when.year, when.month, monthrange(when.year, when.month)[1])
