# Token parser
More often than not I find myself creating scripts to generate test data, and those scripts 
always have some kind of token parser. So I decided to create this script in a more re-usable form.

## What's the use-case for this?
Usually I create a json template and then generate a batch of test data. The json will act as the body of my test items.
While this script will provide randomized data for each instance.

## Installation
```shell
pip install token-parser
```
You can check out this project at [PyPi](https://pypi.org/project/token-parser/).


## What can this parse_token function do?
1. Get current time: "$now()"
2. Get current time (UTC): "$utcNow()"
3. Convert a timestamp to datetime: "$now('2021-12-31T23:59:59.000')"
4. Convert a timestamp to datetime (UTC): "$now('2021-12-31T23:59:59.000Z')"
5. Manipulate a datetime string and generate a datetime object: "$dateAdd('2021-12-31T23:59:59.000Z', {'minute': 10})"
6. Convert string to int: "$int(1)"
7. Convert string to float: "$float(1.5)"
8. Generate a random int: "$int(0, 10)" ($int(min, max))
9. Generate a random float: "$float(0.5, 42.7)" ($float(min, max))
10. Chose randomly an int from a list: "$int(1,2,3,4,5,6,7)"
11. Chose randomly a float from a list: "$float(1,2,3,4,5,6,7)"
12. Generate sequential int (positive and negative): "$inc()" / "$dec()"
13. Generate incremental (by N) int (positive and negative): "$inc(5)" / "$dec(5)"
14. Generate uuid4 strings (unique for whole session or individual): "$guid()" / "$guid(true)"
15. Returns next element on list. Each element will be parsed by python. When reaches the end, will start again: "$next(['foo', 'bar'])" / "$next([1,2,3,4])"
    15.1 The argument must be unique, otherwise they will share the same sequence. 

## Example
Here's an example. More in the [examples folder](https://github.com/brenordv/token-parser-py/tree/master/token_parser/examples)

Consider the following JSON template:
```json
{
    "id": "$inc()",
    "testSession": "$guid(true)",
    "name": "Dolly",
    "age": "$int(18, 42)",
    "score": "$float(150, 9999)",
    "status": "$int(1,2,3,4,5)",
    "generationDate": "$utcNow()"    
}
```

```python
from token_parser.parsers import parse_token

# Helper variables with ISO8601 datetime format (utc and local)
ISO8601_DATE_FORMAT_UTC = "%Y-%m-%dT%H:%M:%S.%fZ"
ISO8601_DATE_FORMAT_LOCAL = ISO8601_DATE_FORMAT_UTC[:-1]

# Storing test items here
test_items = []

# Converting the string JSON to a dictionary (You could use json.load and get it from a file)
template = ast.literal_eval(JSON_TEMPLATE)

# Getting a initial datetime
test_data_creation_start = datetime.utcnow()

# Each datetime will be incremented by 15 minutes
created_at_delay = {"minutes": 15}

# I will create 50 test items
for i in range(50):
    # Current test item
    test_item = {}
    for key, item in template.items():
        # Parsing each token and adding it to the current item.
        test_item[key] = parse_token(item)

    # Adding an extra key named 'createdAt', which will be the initial date + 15 minutes
    test_item["createdAt"] = parse_token(
        f"$dateAdd({test_data_creation_start.strftime(ISO8601_DATE_FORMAT_UTC)}, {created_at_delay})")

    # overwriting the initial datetime, so it will be incremented each time
    test_data_creation_start = test_item["createdAt"]
    
    # adding test item to the list
    test_items.append(test_item)

# printing output
pprint(test_items)
```

The output for this would be:
```python
[
  {'age': 33,
  'createdAt': datetime.datetime(2021, 7, 1, 1, 22, 38, 183365, tzinfo=<UTC>),
  'generationDate': datetime.datetime(2021, 7, 1, 4, 7, 38, 183365, tzinfo=<UTC>),
  'id': 1,
  'name': 'Dolly',
  'score': 9631.926551796414,
  'status': 5,
  'testSession': 'f7607f8d-774b-4823-8d47-91c3db056e73'},
 {'age': 35,
  'createdAt': datetime.datetime(2021, 7, 1, 1, 37, 38, 183365, tzinfo=<UTC>),
  'generationDate': datetime.datetime(2021, 7, 1, 4, 7, 38, 186086, tzinfo=<UTC>),
  'id': 2,
  'name': 'Dolly',
  'score': 5486.760170377791,
  'status': 5,
  'testSession': 'f7607f8d-774b-4823-8d47-91c3db056e73'},
 {'age': 36,
  'createdAt': datetime.datetime(2021, 7, 1, 1, 52, 38, 183365, tzinfo=<UTC>),
  'generationDate': datetime.datetime(2021, 7, 1, 4, 7, 38, 186086, tzinfo=<UTC>),
  'id': 3,
  'name': 'Dolly',
  'score': 383.9861640547723,
  'status': 1,
  'testSession': 'f7607f8d-774b-4823-8d47-91c3db056e73'},
 {'age': 28,
  'createdAt': datetime.datetime(2021, 7, 1, 2, 7, 38, 183365, tzinfo=<UTC>),
  'generationDate': datetime.datetime(2021, 7, 1, 4, 7, 38, 186086, tzinfo=<UTC>),
  'id': 4,
  'name': 'Dolly',
  'score': 6644.5243644456095,
  'status': 2,
  'testSession': 'f7607f8d-774b-4823-8d47-91c3db056e73'},

    ...

 {'age': 28,
  'createdAt': datetime.datetime(2021, 7, 1, 13, 22, 38, 183365, tzinfo=<UTC>),
  'generationDate': datetime.datetime(2021, 7, 1, 4, 7, 38, 190470, tzinfo=<UTC>),
  'id': 49,
  'name': 'Dolly',
  'score': 1584.2818807777992,
  'status': 3,
  'testSession': 'f7607f8d-774b-4823-8d47-91c3db056e73'},
 {'age': 18,
  'createdAt': datetime.datetime(2021, 7, 1, 13, 37, 38, 183365, tzinfo=<UTC>),
  'generationDate': datetime.datetime(2021, 7, 1, 4, 7, 38, 190470, tzinfo=<UTC>),
  'id': 50,
  'name': 'Dolly',
  'score': 6704.023925214241,
  'status': 4,
  'testSession': 'f7607f8d-774b-4823-8d47-91c3db056e73'}
]
```

# Notes
this is a very early stage project, just a few functionalities. If you find any bug, please contact me.


# TODO
1. Make a presentable documentation.
2. Review $now and $utcNow.
3. Add strict_mode, to stop all processing when something goes wrong.
4. Support nested tokens
5. Create identifiers for $next, so you can use the same sequence at the same time in different iterations.