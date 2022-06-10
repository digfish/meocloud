import os
from posixpath import basename
from urllib.parse import parse_qsl, urlencode

import requests
from requests_oauthlib import OAuth1


class MeoCloud(object):
    REQUEST_TOKEN = 'https://meocloud.pt/oauth/request_token'
    AUTHORIZE = 'https://meocloud.pt/oauth/authorize?oauth_token='
    ACCESS_TOKEN = 'https://meocloud.pt/oauth/access_token'
    MEOCLOUD_CONTENT_ENDPOINT = 'https://api-content.meocloud.pt/1'
    MEOCLOUD_ENDPOINT = 'https://api.meocloud.pt/1'
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


    def get_list(self, path=''):
        url = f'{self.MEOCLOUD_ENDPOINT}/List/meocloud/{path}'
        r = self.session.get(url=url)
        return r
    
    def get_file(self,file):
        url = f'{self.MEOCLOUD_CONTENT_ENDPOINT}/Files/meocloud/{file}'
        r = self.session.get(url=url)
        return r

    def upload_file(self,lfile,rpath=''):
        return self.upload_data(f"{rpath}/{lfile}",open(lfile,'rb').read())

    def upload_data(self,path='',data=''):
        url = f'{self.MEOCLOUD_CONTENT_ENDPOINT}/Files/meocloud/{path}'
        r = self.session.put(url=url,data=data)
        return r

    def _chunk_upload(self,data='',offset=0,upload_id=''):
        url = f'{self.MEOCLOUD_CONTENT_ENDPOINT}/ChunkedUpload'
        if offset == 0 or len(upload_id) == 0:
            r = self.session.put(url=url,data=data)
        else:
            r = self.session.put(url=url,data=data,params={'offset':offset,'upload_id':upload_id})
        return r

    def _chunk_upload_commit(self,rpath,upload_id):
        url = f'{self.MEOCLOUD_CONTENT_ENDPOINT}/CommitChunkedUpload/meocloud/{rpath}'
        r = self.session.post(url=url,data={'upload_id':upload_id,'overwrite':True})
        return r

    def delete_file(self,path):
        url = f'{self.MEOCLOUD_ENDPOINT}/Fileops/Delete'
        r = self.session.post(url=url,data={'root':'meocloud','path': f"/{path}"})
        return r

    def properties(self,path):
        url = f'{self.MEOCLOUD_ENDPOINT}/Metadata/meocloud/{path}'
        r = self.session.get(url=url)
        return r


    def account_data(self):
        url = f'{self.MEOCLOUD_ENDPOINT}/Account/Info'
        r = self.session.get(url)
        return r

    def user_last_events(self):
        url = f'{self.MEOCLOUD_ENDPOINT}/ListEvents'
        r = self.session.get(url)
        return r

    def schedule_download_remote(self,_url,name=''):
        if len(name.strip()) == 0:
            name = basename(_url)
        url = f'{self.MEOCLOUD_CONTENT_ENDPOINT}/SaveUrl/meocloud/{name}'
        r = self.session.post(url=url,data={'root':'meocloud','url':_url})
        return r
    
    def pending_remote_download_status(self,job_id):
        url = f'{self.MEOCLOUD_CONTENT_ENDPOINT}/SaveUrlJob/{job_id}'
        r = self.session.get(url=url)
        return r

    def mkdir(self,newdirname):
        url = f'{self.MEOCLOUD_ENDPOINT}/Fileops/CreateFolder'
        r = self.session.post(url=url,data={'root':'meocloud','path': f"/{newdirname}"})
        return r

    def get_media_url(self,rpath):
        url = f'{self.MEOCLOUD_ENDPOINT}/Media/meocloud/{rpath}'
        r = self.session.post(url=url)
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
            self._consumer_key = os.environ['CONSUMER_KEY',None]
        else:
            self._consumer_key = item

    @property
    def consumer_secret(self):
        return self._consumer_secret

    @consumer_secret.setter
    def consumer_secret(self, item):
        if item is None:
            self._consumer_secret = os.environ['CONSUMER_SECRET',None]
        else:
            self._consumer_secret = item
