import json
from .models import User
from django.http import HttpResponse
from .utils import parse_from_to_querystring, refine_query_for_users_in_birthday_range, \
                   process_users_raw_incomming_data, get_date_from_long_date_str_format

def user_birthdays(request):
  if request.method == 'GET':  # Point B
    try:
      # If we have from&to querystrings, process them
      fdate, tdate = parse_from_to_querystring(
                      request.GET.get('from'), request.GET.get('to'))
    except ValueError as err:
      return HttpResponse(json.dumps({'from&to': str(err)}), status=400)
      
    users = User.objects.all()  # By default, return all users
    if fdate and tdate:  # Either both fdate and tdate are set, or none is
      users = refine_query_for_users_in_birthday_range(users, fdate, tdate)
    data = json.dumps([user.serialize_for_API() for user in users], 
                      ensure_ascii=False)
    return HttpResponse(data, content_type='application/json', status=200)

  elif request.method == 'POST':  # Point A
    try:
      # Validate and process requet
      users_data = process_users_raw_incomming_data(request.body)
    except ValueError as err:
      return HttpResponse(json.dumps(str(err)), status=400)
    # User's data seems valid (if any)
    for user_data in users_data:
      User.objects.update_or_create(email=user_data['email'],
                                    defaults=user_data)
    msg = '{} users upserted in DB\n'.format(len(users_data))
    return HttpResponse(msg, content_type='application/json', status=200)
  return HttpResponse(status=405)  # Method not allowed


def user_birthdays_avg_age(request):
  if request.method == 'GET':  # Point C
    when_str = request.GET.get('when')
    try:
      when = get_date_from_long_date_str_format(when_str) if when_str else None
      avg = User.objects.get_avg_age(when)
    except ValueError as err:
      return HttpResponse(json.dumps({'when': str(err)}), status=400)
    return HttpResponse(json.dumps(avg), content_type='application/json', status=200)
  return HttpResponse(status=405)  # Method not allowed