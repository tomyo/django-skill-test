from django.http import HttpResponse
import json

from .utils import permutate_upper_lower, word_has_reasonable_length

def letter_digit(request, word=''):
  if not word_has_reasonable_length(word):
    return HttpResponse(status=412, reason="Word is too expensive to process")
  result = permutate_upper_lower(word)
  return HttpResponse(json.dumps(result, ensure_ascii=False), content_type='application/json')
