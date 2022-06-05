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

# IMPROVEMENTS AND IMPLEMENTATIONS (REPL)
The improvements made by [digfish](https://github.com/digfish) were: storing the received credentials in a [.env](https://zetcode.com/javascript/dotenv/) and a [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) for the most basic commands: like retrieving files, upload them, delete and list, in the likeness of the [FTP command](https://manpages.org/ftp
).
To call the REPL type:
 ```
    > meocloudrepl
    Welcome to meo cloud repl!
    Enter Press Tab to see commands
    help <cmd> or ?<cmd> for description
    ^D or exit to quit
    meocloud [/]>
```
The following commands are implemented:
- cat
- exit
- help
- lls
- mkdir
- properties
- pwd
- rcd
- rup
- del
- get
- lcd
- lup
- mls
- put
- rcat
- rls

To know the meaning of each one, write `help <cmd>` .

Comments and improvements: sam@digfish.org

