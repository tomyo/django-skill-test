# skill-test

## Getting started
###  Set up enviroment:

* In one console tab, run: `docker-compose up`
* In another console tab, run the migrations: `./run_migrations_in_compose.sh`
* That's it!

### Run tests:
`./run_tests_in_compose.sh`

### URLS
* /api/v1/letter_digit/`<word>`  [GET]
* /api/v1/users/ [POST/GET]
* /api/v1/users/?from=`%d%m`&to=`%d%m` [GET]
* api/v1/users/avg_age [GET]

##  Excercises

### 1a

Create an API endpoint which accepts a list of JSON objects as POST-payload

* Store the data in a Postgres Database
* The email address should be unique
* All fields are required

Payload Example:
```
[
  {
	"first_name":"Melamie",  
	"last_name":"Mandrey",  
	"email":"mmandrey0@hubpages.com",  
	"birthday":"28.04.2000"
  }, 
  {
	"first_name":"Rosemonde",  
	"last_name":"Hatchman",  
	"email":"rhatchman1@bbc.co.uk",  
	"birthday":"04.10.1950"  
  },  
  {
	"first_name":"Casie",  
	"last_name":"Giveen",  
	"email":"cgiveen2@psu.edu",  
	"birthday":"22.12.1971"  
  }  
]
```

### 1b. 
Create an API endpoint which returns a list of objects, filtered by the following parameters:
 * (birthday)
	* from (example: from=%d%m) 
	* to (example: to=%d%m)

### 1c.
Create an API endpoint which returns the average age of all records in the database.
Think about caching.


## Resolution

#### 1a	
POST to `/api/v1/users/ `

* Upsert the User's objects with the incomming information, only if all is valid.

By default, since email address is unique, trying to add a User with a existing email 
will yield an error in the request. Since updating a user's info is a normal task, 
two alternatives are posible:

1. Add a PUT/PATH call to the API, to handle this case.

2. Upsert.

I opted for option 2 for simplicity.

If there's some incorrect information in a post request, the system rejects the whole 
request, even if some items in the request are correct.
This is, of course, a design desition.

#### Examples
* Upserting a user:
```
curl  http://localhost:8000/api/v1/users/ -i -d '[{"first_name": "Alan", "last_name": "Brito", "email": "alan@brito.de", "birthday": "19.04.1988"}]'
```

* Bulk upserting 1000 users from test data mock:
```
curl  http://localhost:8000/api/v1/users/ -i -d @user_birthday/tests/MOCK_DATA.json
```


#### 1b. 
GET to `/api/v1/users/?from=%d%m&to=%d%m`

I assumend the payload example from [1a](###1a) is having the expected date format for 
the project, so for this point, I first considered the from/to querystrings parameters
to maintain that format (`%d.%m` instead of `%d%m`). 
After reading the excercise for a second time, and for the sake of using the examples provided
as the rule, I decided to implement both.
Still, the form %d%m may be ambiguos in some cases (i.e `from=111`), so is suboptimal.
For the `%d%m` format, I simply let `datetime.strptime(date_string, "%d%m")` to handle
the parsing. So at the end both formats coexists.  

#### Examples
* Adding/modifying a user:
```
curl  http://localhost:8000/api/v1/users/  -i -d '[{"first_name": "Alan", "last_name": "Brito", "email": "alan@brito.de", "birthday": "19.04.1988"}]'
```

* Buld adding the 1000 users from test mock data:
```
curl  http://localhost:8000/api/v1/users/  -i -d @user_birthday/tests/MOCK_DATA.json
```

#### 1c. 
GET to `/api/v1/users/avg_age`

There's a nice little hack to use a function's default value as cache in Python,
and felt tempted to use it for this purpose. Since is a memory cache, 
is not persistent in DB.
* When there are no users in DB, this method returns `NaN`.
* The cache is valid until the first of the follwing rules apply:
	* Next birthday happening on current month
	* End of current month (if there was no birthdays)
	* Changes are made to the user's objects in DB. 

To trigger the invalidations of the cache against user's model changes, I used 
Django's signals.
To calculate the average age of users, I used a ModelManager, so it can be
accesssed by simply calling `User.objects.get_avg_age()`

#### Example

```
curl  http://localhost:8000/api/v1/users/avg_age
```

++Side note:++

Turns out this calculation is tricky and imposible to get exact, considering
leap years and the fact that we don't have the time of birth, only the date.
So I simply calculated the average of the elapsed days until `date.today()` 
for every user, and divided that by 365. I guess is fair enought.

  
  
FINAL NOTES
------------------------

* For using Docker with Django and postgres SQL, I followed this guide:
https://docs.docker.com/compose/django/

* For using REST endpoints in this small project, I decided to use the included 
   django methods available by default.

* In a real project, I would consider using something like tastypie or djangorestframework, 
   to also have a nice HTML version of the API, and better validation, error handling, pagination, 
   performance, code readability, etc.

* For this project, I tryied to avoid using external packages, and focused on using 
   already included Django's and Python's packages.
   
* Since security and authentication was beyond the scope of the test, I took the following measures:
	* Commented out csrf middleware in project's `settings.py` to allow POST requests to pass through:

* Decided to not use API authentiction
	* Still, I was pleaced to find this nice source of authentication methods and
	   third party packages available to integrate, for future reference:
	   https://www.django-rest-framework.org/api-guide/authentication/


