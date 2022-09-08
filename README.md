# API42:
Logic to interact with the API from 42Network written in python3.

## Setup:
This class requires a file on the root of the directory called ```__secrets__.py``` with the following content:
```python
uid="UID"
secret="secret"
```
Where *UID* and *SECRET* are the credentials from your 42API application.

## Usage:
In order to use this class, you should follow this steps:
- Create an instance of the class `API42`.
	```python
	from API42 import API42

	api = API42()
	```

- Implement in your code the methods `get` and `post` and start using the API.
	```python
	api.get("/v2/ENDPOINT", ["FILTER", "SORT", ...], ...)
	api.post(...)
	```

### GET usage:
- Enter the endpoint directly on the `url` parameter.
- Fill the `filters` array with all the *filters*, *sorting* and *range* parameters. Keep in mind they are only verified against the API.
- For large replies, the output may be bigger than the maximum number of elements allowed per page (the API uses pagination). However, with the attribute `multi_request = True` you can concatenate all the pages. This option can also be disabled by setting the value to `False`.
- The default pagination size is defined by the attribute `page_size`. This value can be change freely but keep in mind the value is only verified against the API.

## Considerations:
- The code handles the token bearer needed to stablish the communication automatically. At the fist call of the instance, it automatically obtains the token if needed (you can give it manually if you prefer).
- The token expiration is handled also automatically if the headers are not given too. This allows to obtain a new token in the middle of a program.
- The logic does not handle the case of multiple executions in parallel with the same credentials, reaching the 1200 calls/hour. However, it does handle the http-error returned by the API.