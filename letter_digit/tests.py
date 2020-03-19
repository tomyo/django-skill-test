# -*- coding: utf-8 -*-

from django.test import TestCase, Client
from .settings import max_alpha_letters, max_word_length

class LetterDigitTestCase(TestCase):
  def setUp(self):
    self.client = Client()
    self.baseUrl = '/api/v1/letter_digit/'

  def test_no_argument_404(self):
    response = self.client.get(self.baseUrl)
    self.assertEqual(response.status_code, 404)

  def test_correct_status_code_200(self):
    response = self.client.get(self.baseUrl + 'a')
    self.assertEqual(response.status_code, 200)

  def test_correct_charset(self):
    response = self.client.get(self.baseUrl + 'a')
    self.assertEqual(response.charset, 'utf-8')

  def test_space(self):
    response = self.client.get(self.baseUrl + ' ')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json(), [' '])

  def test_spaces(self):
    spaces = '     '
    response = self.client.get(self.baseUrl + spaces)
    self.assertEqual(response.json(), [spaces])
  
  def test_non_alpha(self):
    request = '!@$%^&*(){}][~``""1234567890'
    response = self.client.get(self.baseUrl + request)
    self.assertEqual(response.json(), [request])

  def test_one_letter(self):
    request = 'a'
    response = self.client.get(self.baseUrl + request)
    self.assertEqual(set(response.json()), set(['a', 'A']))

  def test_example_provided(self):
    """a2B => [a2b, a2B, A2b, A2B]"""
    response = self.client.get(self.baseUrl + 'a2B')
    expected = set(['a2b', 'a2B', 'A2b', 'A2B'])
    self.assertEqual(set(response.json()), expected)
  
  def test_too_much_alpha_letters(self):
    request = 'a' * (max_alpha_letters + 1)
    response = self.client.get(self.baseUrl + request)
    self.assertEqual(response.status_code, 412)
  
  def test_word_too_long(self):
    request = '1' * (max_word_length + 1)
    response = self.client.get(self.baseUrl + request)
    self.assertEqual(response.status_code, 412)

  def test_long_non_alpha_word(self):
    request = '1' * 500
    response = self.client.get(self.baseUrl + request)
    self.assertEqual(response.json(), [request])

  
    