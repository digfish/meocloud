# MEOCLOUD
UNOFFICIAL MEOCLOUD PACKAGE

## Install

Use **pip** to install the latest stable version of `meocloud`:

```
$ pip install meocloud
```
## Create a credential
Before, create a new app in https://meocloud.pt/my_apps, then:
```
meocloud mycredential
```

## Use mode
```python
from meocloud.services import MeoCloud

consumer_key='***'
consumer_secret='***'
oauth_token='***'
oauth_token_secret='***'
meo = MeoCloud(consumer_key=consumer_key, consumer_secret=consumer_secret, oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
print(meo.get_list('/'))
```

## Use with `requests` package
before you need run `pip install requests`
```python
import requests
from meocloud.services import MeoCloud

meo = MeoCloud(consumer_key=consumer_key, consumer_secret=consumer_secret, oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
auth = meo.auth_in_request()
url = f'https://api.meocloud.pt/1/List/meocloud('
r = requests.get(url=url, auth=auth)
r.content
```

If you have questions, send them to igordantas91@icloud.com