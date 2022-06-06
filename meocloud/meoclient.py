import configparser

from meocloud.services import MeoCloud

import os,sys
import configparser


def get_meo_client():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~')+'/meocloud.ini')
    app_config = config['DEFAULT']
    return MeoCloud(
        consumer_key = app_config['CONSUMER_KEY'],
        consumer_secret=app_config['CONSUMER_SECRET'],
        oauth_token=app_config['OAUTH_TOKEN'],
        oauth_token_secret=app_config['OAUTH_TOKEN_SECRET']
    )


def json_pprint(json_obj):
    import json
#    obj = json.loads(json_str)
    print(json.dumps(json_obj,indent=True))


def is_html(str):
    from bs4 import BeautifulSoup as bs
    str1 = str[:]
    soup = bs(str,'html.parser')
    return str1 != soup.text
