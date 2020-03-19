# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from user_birthday.models import User, UserForm
from user_birthday.utils import get_date_from_long_date_str_format, get_avg_age
from datetime import date
import json
import math

class UserTestPOST(TestCase):
  """Testing Point A"""
  def setUp(self):
    self.client = Client()
    self.baseUrl = '/api/v1/users/'
    with open('user_birthday/tests/MOCK_DATA.json', 'r') as f:
      # Assuming this is ran from docker
      self.mock_data = json.load(f)

  def test_no_arguments(self):
    response = self.client.post(self.baseUrl)
    self.assertEqual(response.status_code, 400)

  def test_bad_formated_json(self):
    response = self.client.post(self.baseUrl, json.dumps('asc'),
                                content_type='application/json')
    self.assertEqual(response.status_code, 400)

  def test_empty_list_of_objects(self):
    response = self.client.post(self.baseUrl, json.dumps([]),
                                content_type='application/json')
    self.assertEqual(response.status_code, 200)

  def test_adding_one_well_formed_user(self):
    response = self.client.post(self.baseUrl, json.dumps([self.mock_data[0]]),
                                content_type='application/json')
    self.assertEqual(response.status_code, 200)
    users = User.objects.all()
    self.assertEqual(len(users), 1)
    self.assertEqual(users[0].serialize_for_API(), self.mock_data[0])

  def test_adding_one_malformed_user(self):
    user = {'first_name': 'Melamie', 'last_name': 'Mandrey', 'email': '', 'birthday': '28.04.2000'}
    # user['email'] = ''
    response = self.client.post(self.baseUrl, json.dumps([user]),
                                content_type='application/json')
    self.assertEqual(response.status_code, 400)
    users = User.objects.all()
    self.assertEqual(len(users), 0)

  def test_adding_two_users_one_with_incorrect_info(self):
    """Make sure no partial data is added if all is not valid"""
    users = self.mock_data[0:2]
    users[1]['first_name'] = ''
    response = self.client.post(self.baseUrl, json.dumps(users),
                                content_type='application/json')
    users_in_db = User.objects.all()
    self.assertEqual(len(users_in_db), 0)
    self.assertEqual(response.status_code, 400)
  
  def test_adding_1000_users(self):
    users_data = self.mock_data
    response = self.client.post(self.baseUrl, json.dumps(users_data),
                                content_type='application/json')
    users_in_db = User.objects.all()
    self.assertEqual(len(users_in_db), len(users_data))
    self.assertEqual(response.status_code, 200)


class UserTestGET(TestCase):
  """Testing Point B"""
  def setUp(self):
    self.client = Client()
    self.baseUrl = '/api/v1/users/'
  
  @classmethod
  def setUpTestData(cls):
    # Set up data for the whole TestCase
    with open('user_birthday/tests/MOCK_DATA.json', 'r') as f:
      mock_data = json.load(f)
      for user_data in mock_data:
        user_data['birthday'] = get_date_from_long_date_str_format(user_data['birthday'])
        User.objects.create(**user_data)
      assert (User.objects.count() == len(mock_data))  # Just making sure
    
  def test_no_arguments(self):
    """Should return all users"""
    response = self.client.get(self.baseUrl)
    self.assertEqual(response.status_code, 200)
    users_in_db = User.objects.all()
    response_users = response.json()
    self.assertEqual(len(response_users), len(users_in_db))

  def test_no_complete_arguments(self):
    response = self.client.get(self.baseUrl, {'from':1010})
    self.assertEqual(response.status_code, 400)
    
  def test_from_to_same_day(self):
    """Date range should be inclusive"""
    day = '06'
    month = '10'
    # For this date, I know there are 3 users in mock_data having birthday
    users_in_mock_data_for_this_day = 3
    response = self.client.get(self.baseUrl, {'from': day+month, 'to': day+month})
    self.assertEqual(response.status_code, 200)
    users_in_db = User.objects.filter(
      birthday__month=month,
      birthday__day=day,
    )
    response_users = response.json()
    self.assertEqual(len(response_users), len(users_in_db))
    self.assertEqual(len(response_users), users_in_mock_data_for_this_day)

  def test_overlapping_dates_no_results(self):
    """If from is later that to, no results are expected"""
    # For this date, I know there are 3 users in mock_data having birthday
    response = self.client.get(self.baseUrl, {'from': '1212', 'to': '1112'})
    self.assertEqual(response.status_code, 200)
    response_users = response.json()
    self.assertEqual(len(response_users), 0)

  def test_correct_boundaries(self):
    """Can we obtain all users using from&to args?"""
    response = self.client.get(self.baseUrl, {'from': '0101', 'to': '3112'})
    self.assertEqual(response.status_code, 200)
    response_users = response.json()
    self.assertEqual(len(response_users), User.objects.count())

  def test_one_month(self):
    """All users from January"""
    response = self.client.get(self.baseUrl, {'from': '0101', 'to': '3101'})
    self.assertEqual(response.status_code, 200)
    response_users = response.json()
    users_on_month = User.objects.filter(birthday__month='1')
    self.assertEqual(len(response_users), users_on_month.count())
  

class UserTestAverageAge(TestCase):
  """Testing Point C"""
  def setUp(self):
    self.client = Client()
    self.baseUrl = '/api/v1/users/avg_age'
  
  @classmethod
  def setUpTestData(cls):
    # Set up data for the whole TestCase
    with open('user_birthday/tests/MOCK_DATA.json', 'r') as f:
      mock_data = json.load(f)
      for user_data in mock_data:
        user_data['birthday'] = get_date_from_long_date_str_format(user_data['birthday'])
        User.objects.create(**user_data)
      assert (User.objects.count() == len(mock_data))  # Just making sure
    
  def test_no_users(self):
    """Should return NaN"""
    [user.delete() for user in User.objects.all()]  # Delete all users
    response = self.client.get(self.baseUrl)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(math.isnan(response.json()), True)

  def test_all_users_in_past_date(self):
    """Should return average age of all users in 3.2.1998"""
    when = "3.2.1998"
    expected_result = 17
    response = self.client.get(self.baseUrl, {'when': when})
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json(), expected_result)

  def test_cache_in_past_date(self):
    """Should return average age of all users in 3.2.1998"""
    when = "3.2.1998"
    expected_result = 17
    expected_cache_after = {'result': 17, 'valid_until': date(1998, 2, 5), 
                            'valid_from': date(1998, 2, 3)}
    response = self.client.get(self.baseUrl, {'when': when})
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json(), expected_result)
    self.assertEqual(get_avg_age.__defaults__[0], expected_cache_after)

  def test_from_today(self):
    today = date.today()
    expected_result = 30
    birthday = today.replace(year=today.year - expected_result)
    User.objects.all().update(birthday=birthday)
    # all users should be `expected_result` years old now
    response = self.client.get(self.baseUrl)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json(), expected_result)
    
    
