from itertools import product
from .settings import max_alpha_letters, max_word_length

def permutate_upper_lower(word):
  assert(word_has_reasonable_length(word))
  return permutate_upper_lower_recursive(word)
  

def permutate_upper_lower_imperative(word):  # Iterative version using itertools
  letters = [(c, c.upper()) if c.isalpha() else (c,) for c in word.lower()]
  return ["".join(words_as_lists) for words_as_lists in product(*letters)]


def permutate_upper_lower_recursive(word, words=['']):  # Recursive version
  if not word:
    return words  # No side effects because we don't modify `words`
  remaining_word, next_letter = word[:-1], word[-1]
  new_words = [next_letter.lower() + w for w in words]
  if str.isalpha(next_letter):
    new_words += [next_letter.upper() + w for w in words]
  return permutate_upper_lower_recursive(remaining_word, new_words)

def word_has_reasonable_length(word):
  count = 0
  if max_word_length < len(word):
    return False
  for l in word:
    if str.isalpha(l):
      count += 1
    if max_alpha_letters < count:
      return False
  return True
    
