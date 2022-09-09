# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    API42.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jre-gonz <jre-gonz@student.42madrid.com    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2022/07/19 13:00:04 by jre-gonz          #+#    #+#              #
#    Updated: 2022/09/09 18:49:49 by jre-gonz         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import json
import requests
from requests import Response
import time

try:
	from .__secrets__ import uid as UID
	from .__secrets__ import secret as SECRET
except Exception as e:
	print("API42 credentials not added. Read documentation for more information.")
	exit(0)

class API42:
	'''
	Class with the logic needed to interact with the API of 42 Network.
	'''

	# Applications are limited to 2 requests/second and 1200 requests / hour
	REQUESTS_DELAY = 0.55

	URL = "https://api.intra.42.fr"

	ERROR_CODES = {
		400: "Something in the request is not right. The server doesn't understand the request.",
		401: "You don't have the right permissions to access this information.",
		403: "Forbidden.",
		404: "Page or resource is not found.",
		422: "Unprocessable entity.",
		429: "Are the credentials valid?",
		500: "We have a problem with our server. Please try again later."
	}

	def __init__(self) -> None:
		self._bearer = None
		self.last_call = 0


	# Bearer

	@classmethod
	def bearer_obsolete(cls, bearer: json):
		'''
		Checks if the given bearer is valid. If nothing given or out of date,
		the result of this method is False. Otherwise, True.
		'''
		if bearer == None:
			return True
		created = int(bearer["created_at"])
		time_remaining = int(bearer["expires_in"])
		now = int(round(time.time()))
		return created + time_remaining <= now

	@property
	def bearer(self) -> json:
		'''
		Obtains and stores the needed bearer form the intranet.
		'''
		if API42.bearer_obsolete(self._bearer):
			DATA=f"grant_type=client_credentials&client_id={UID}&client_secret={SECRET}"
			self._bearer = self.post(f"/oauth/token", data = DATA, headers = {}).json()
		return self._bearer

	@property
	def token(self):
		return self.bearer["access_token"]

	@property
	def basic_header(self):
		return {"Authorization": f"Bearer {self.token}"}


	# Connectivity logic

	def wait_limitation(self):
		'''
		Awaits the minimum time needed between calls. If no time needed to be
		waited, this function ends instantly.
		'''
		now = time.time()
		if now - self.last_call < API42.REQUESTS_DELAY:
			time.sleep(API42.REQUESTS_DELAY - (now - self.last_call))
		self.last_call = time.time()
		print(".", end="", flush=True)


	def post(self, url: str, filters: list = {}, data: str = "", headers = None):
		if headers == None:
			headers = self.basic_header
		full_url = API42._format_url(url, filters)
		self.wait_limitation()
		return API42.post_request(full_url, data, headers)

	def get(self, url: str, filters: list = [], headers = None, multi_request: bool = True, page_size: int = 100):
		if headers == None:
			headers = self.basic_header
		if not any("page[size]=" in f for f in filters):
			filters.append(f"page[size]={page_size}")

		if not multi_request or any("page[number]" in f for f in filters):
			full_url = API42._format_url(url, filters)
			self.wait_limitation()
			return API42.get_request(full_url, headers).json()
		running = True
		i = 1
		response = []
		while running:
			fs = filters + [f"page[number]={i}"]
			full_url = API42._format_url(url, fs)
			self.wait_limitation()
			r = API42.get_request(full_url, headers).json()
			if type(r) != list:
				return r
			if len(r) < page_size:
				running = False
			response = r + response
			i = i + 1
		return response


	@classmethod
	def _format_url(cls, url: str, filters: list):
		f = "" if len(filters) == 0 else f"?{'&'.join(filters)}"
		return f"{cls.URL}{url}{f}"

	@classmethod
	def post_request(cls, url: str, data: str, headers={}) -> Response:
		response = requests.post(url, data=data, headers=headers)
		cls.handle_response(response)
		return response

	@classmethod
	def get_request(cls, url: str, headers = {}) -> Response:
		response = requests.get(url, headers=headers)
		cls.handle_response(response)
		return response

	@classmethod
	def handle_response(cls, response):
		if response.status_code == 200:
			return
		
		if response.status_code in cls.ERROR_CODES:
			raise Exception(cls.ERROR_CODES[response.status_code])
		else:
			raise Exception(f"There was a problem obtaining the response:\n  Status code: {response.status_code}")
