import requests
from requests_oauthlib import OAuth1
from urllib.parse import parse_qsl, urlencode
import json

class MeoCloud(object):
    REQUEST_TOKEN = 'https://meocloud.pt/oauth/request_token'
    AUTHORIZE = 'https://meocloud.pt/oauth/authorize?oauth_token='
    ACCESS_TOKEN = 'https://meocloud.pt/oauth/access_token'

    def __init__(self, consumer_key=None, consumer_secret=None, oauth_token=None, oauth_token_secret=None, pin=None, callback_uri='oob'):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.callback_uri = callback_uri
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.pin = pin
    
    def get_list(self, path='/'):
        if path == '':
            path = '/'
        oauth = OAuth1(self.consumer_key,
                   client_secret=self.consumer_secret,
                   resource_owner_key=self.oauth_token,
                   resource_owner_secret=self.oauth_token_secret)
        url = f'https://api.meocloud.pt/1/List/meocloud{path}'
        r = requests.get(url=url, auth=oauth)
        return r.content
    
    def auth_in_request(self):
        return OAuth1(self.consumer_key,
                   client_secret=self.consumer_secret,
                   resource_owner_key=self.oauth_token,
                   resource_owner_secret=self.oauth_token_secret)

    @property
    def authorize(self):
        if self.oauth_token is None:
            oauth = OAuth1(client_key=self.consumer_key, client_secret=self.consumer_secret, callback_uri=self.callback_uri)
            r = requests.post(url=self.REQUEST_TOKEN, auth=oauth)
            credentials = dict(parse_qsl(r.content.decode("utf-8") ))
            self.oauth_token = credentials.get('oauth_token')
            self.oauth_token_secret = credentials.get('oauth_token_secret')
            self.authorize_url = self.AUTHORIZE + self.oauth_token
            return {
                'oauth_token': self.oauth_token,
                'oauth_token_secret': self.oauth_token_secret,
                'authorize_url': self.authorize_url,
            }
        else:
            return True
    
    def get_my_credential(self, pin):
        self.pin = pin
        oauth = OAuth1(self.consumer_key,
                client_secret=self.consumer_secret,
                resource_owner_key=self.oauth_token,
                resource_owner_secret=self.oauth_token_secret,
                verifier=self.pin)
        r = requests.post(url=self.ACCESS_TOKEN, auth=oauth)
        credentials = dict(parse_qsl(r.content.decode("utf-8") ))
        self.oauth_token = credentials.get('oauth_token')
        self.oauth_token_secret = credentials.get('oauth_token_secret')
        return {
            'oauth_token': self.oauth_token,
            'oauth_token_secret': self.oauth_token_secret
        }
    
    @property
    def consumer_key(self):
        return self._consumer_key

    @consumer_key.setter
    def consumer_key(self, item):
        if item is None:
            self._consumer_key = os.environ['CONSUMER_KEY', None]
        else:
            self._consumer_key = item

    @property
    def consumer_secret(self):
        return self._consumer_secret

    @consumer_secret.setter
    def consumer_secret(self, item):
        if item is None:
            self._consumer_secret = os.environ['CONSUMER_SECRET', None]
        else:
            self._consumer_secret = item