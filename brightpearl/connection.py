import requests
import logging
import json

from brightpearl.exceptions import TokenExpiredException


class OauthConnection(object):
    def __init__(self, client_id, client_secret):
        self.resource_base_path = "https://{region}.brightpearl.com/public-api/{account_id}/{resource}"
        self._session = requests.Session()
        self.client_id = client_id
        self.client_secret = client_secret
        self._session.headers = {
            "Accept": "application/json",
            "Content - Type": "application/x-www-form-urlencoded"
        }

    def make_request(self, url, method, data=None):
        if not data:
            data = dict()
        response = self._session.request(method, url, data=data)
        return self.process_response(response)

    @staticmethod
    def process_response(response):
        result = dict()
        if response.status_code in [200, 201, 202]:
            result = response.json()
        else:
            raise ValueError("Error while making api request: {}".format(response.text))
        return result


class Connection(object):
    def __init__(self, region, account_id, access_token, developer_ref, app_ref):
        self.resource_base_path = "https://{region}.brightpearl.com/public-api/{account_id}/{resource}"
        self.region = region
        self.account_id = account_id
        self._session = requests.Session()
        self._session.headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(access_token),
            "brightpearl-dev-ref": developer_ref,
            "brightpearl-app-ref": app_ref
        }

    def get_full_path(self, endpoint):
        return self.resource_base_path.format(
            **{"region": self.region, "account_id": self.account_id, "resource": endpoint}
        )

    def make_request(self, url, method, data=None, raw_response=False):
        if not data:
            data = dict()
        response = self._session.request(
            method=method, url=self.get_full_path(url), data=json.dumps(data)
        )
        return self.process_response(response, raw_response)

    @staticmethod
    def process_response(response, raw_response):
        result = dict()
        if response.status_code in [200, 201, 202]:
            if not raw_response:
                result = response.json()
            else:
                return response.raw
        elif response.status_code == 401:
            raise TokenExpiredException("Token expired")
        else:
            raise ValueError("Error while fetching : {}".format(response.text))
        return result
