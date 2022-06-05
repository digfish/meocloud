from meocloud.services import MeoCloud
import pprint
import os,sys
import dotenv

def get_meo_client():
    dotenv.load_dotenv()
    return MeoCloud(
        consumer_key = os.getenv('CONSUMER_KEY'),
        consumer_secret=os.getenv('CONSUMER_SECRET'),
        oauth_token=os.getenv('OAUTH_TOKEN'),
        oauth_token_secret=os.getenv(
            'OAUTH_TOKEN_SECRET'
        )
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
