==================================================
Rosenmeister skill-test - Walk thougth
==================================================

How to try this out:
-------------------
* In one console tab, run:
`docker-compose up`

* In another console tab, run the migrations:
`./run_migrations_in_compose.sh`

* That's it!

To run tests:

`./run_tests_in_compose.sh`


Excercises
----------
1. 
  a. POST to `/api/v1/user_birthday/`

    By default, since email address is unique, trying to add a User
    object with a existing email, will yield error.
    Since updating a user's info is a normal task, two alternatives are posible:
    1. Add a UPDATE call to the API, to handle this cases.
    2. Upsert all incomming users objects.
    I opted for option 2 for simplicity.

    If there's some incorrect information in a post request, the system rejects
    the whole request, even if some items in the request are correct.
    This is, ofcourse, a design desition.


  b. GET to `/api/v1/user_birthday/?from=%d%m&to=%d%m`
  
    Assumend the payload example from `1a` is having the needed date format for the
    project, so for `1b` I considered the from/to querystrings parameters 
    to maintain that format: `%d.%m` instead of `%d%m`. Also by doing this,
    the app can be more flexible about the number of digits provided in the 
    days/months queryparam, so `from=1.1` can be as valid as `from=01.01`. 
    UPDATE: For the sake of using the examples as rule, decided to also accept dates 
    in the `%d%m` format, and let `datetime.strptime(date_string, "%d%m")` handle
    the parsing. Both formats coexists.
    In a real app, pagination would be necesary.

  c. GET to `/api/v1/user_birthday/averageage`

    There's a nice little hack to use a function's default value as cache, 
    and felt tempted to use it for this purpose.
    The cache is valid until next birthday happening on current month, or
    until the end of current month (if there was no birthdays), or after 
    changes are made to the user's objects. Since is a memory cache, is not 
    persistent in DB.
    To trigger the invalidations against user's model changes, I used Django's signals.
    To calculate the average age of users, I used a ModelManager, so it can be
    accesssed by calling `User.objects.get_avg_age()`
    When there are no users in DB, this method returns `NaN`.
    Turns out this calculation is tricky and imposible to get it exact, considering
    leap years and the fact that we don't have the time of birth, only the date.
    So I simpl calculated the average of the elapsed days until today for every user,
    and divided that by 365. I guess is fair enought.


CONSIDERATIONS
--------------

* For using Docker with Django and postgres SQL, I followed this guide:
https://docs.docker.com/compose/django/

* For using REST endpoints in this small project, I decided to use the included
django methods available by default.
In a real project, I would consider using something like tastypie or
djangorestframework, to also have a nice HTML version of the API, and better validation, error handling, pagination, performance, code readability, etc.

* I avoided using external packages in general, coded the most on my own,
  or used already included Django's and Python's packages.

Since security and authentication was beyond the scope of the test,
I took the following measures:

* Commented out csrf middleware in project's `settings.py` to allow POST requests to pass through:
`# 'django.middleware.csrf.CsrfViewMiddleware'`

* Decided to not use API authentication
  Still, I was pleaced to find this nice source of authentication methods and 
  third party packages available to integrate, for future reference:
  https://www.django-rest-framework.org/api-guide/authentication/
