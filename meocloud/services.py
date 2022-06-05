import os
from posixpath import basename
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
        self.session = requests.Session()
        self.session.auth = self.auth_in_request()

    def auth_in_request(self):
        return OAuth1(self.consumer_key,
                      client_secret=self.consumer_secret,
                      resource_owner_key=self.oauth_token,
                      resource_owner_secret=self.oauth_token_secret)


    def get_list(self, path='/'):
        if path == '':
            path = '/'
        url = f'https://api.meocloud.pt/1/List/meocloud{path}'
        r = self.session.get(url=url)
        return r
    
    def get_file(self,file):
        url = f'https://api-content.meocloud.pt/1/Files/meocloud/{file}'
        r = self.session.get(url=url)
        return r

    def upload_file(self,lfile,rpath=''):
        return self.upload_data(f"{rpath}/{lfile}",open(lfile,'rb').read())

    def upload_data(self,path='',data=''):
        url = f'https://api-content.meocloud.pt/1/Files/meocloud{path}'
        print(f"Uploading to {url}")
        r = self.session.put(url=url,data=data)
        return r

    def delete_file(self,path):
        url = 'https://api.meocloud.pt/1/Fileops/Delete'
        r = self.session.post(url=url,data={'root':'meocloud','path': f"{path}"})
        return r

    def properties(self,path):
        url = f'https://api.meocloud.pt/1/Metadata/meocloud{path}'
        r = self.session.get(url=url)
        return r

    def account_data(self):
        url = 'https://api.meocloud.pt/1/Account/Info'
        r = self.session.get(url)
        return r

    def user_last_events(self):
        url = 'https://api.meocloud.pt/1/ListEvents'
        r = self.session.get(url)
        return r

    def schedule_download_remote(self,_url,name=''):
        if len(name.strip()) == 0:
            name = basename(_url)
        print(f"Downloading to {name}")
        url = f'https://api-content.meocloud.pt/1/SaveUrl/meocloud/{name}'
        r = self.session.post(url=url,data={'root':'meocloud','url':_url})
        return r
    
    def pending_remote_download_status(self,job_id):
        url = f'https://api-content.meocloud.pt/1/SaveUrlJob/{job_id}'
        r = self.session.get(url=url)
        return r

    def mkdir(self,newdirname):
        url = 'https://api.meocloud.pt/1/Fileops/CreateFolder'
        r = self.session.post(url=url,data={'root':'meocloud','path': f"/{newdirname}"})
        return r

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