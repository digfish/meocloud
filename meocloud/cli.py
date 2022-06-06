from turtle import dot
import click
from meocloud.services import MeoCloud
import webbrowser
import os
import configparser

@click.group()
def cli():
    pass

@cli.command()
@click.option('--consumer_key', prompt='Your consumer key', help='your consumer key')
@click.option('--consumer_secret', prompt='Your consumer secret', help='your consumer secret')
@click.option('--callback_uri', prompt='Your callback uri', default='oob', help='your callback uri')
@click.option('--save-config',prompt='store the credentials in a .ini file?',default=True,help='save the credentials in a .ini file', type=bool)
def mycredential(consumer_key, consumer_secret, callback_uri, save_config):
    meo = MeoCloud(consumer_key=consumer_key, consumer_secret=consumer_secret)
    authorize = meo.authorize
    click.echo(f'Go to the following link in your browser: {authorize["authorize_url"]}')
    webbrowser.open_new_tab(authorize["authorize_url"])
    pin = click.prompt('Please enter a valid pin', type=str)
    meo = MeoCloud(consumer_key=consumer_key, consumer_secret=consumer_secret, oauth_token=authorize["oauth_token"], oauth_token_secret=authorize["oauth_token_secret"], callback_uri=callback_uri)
    result = meo.get_my_credential(pin)
    click.echo(f'oauth_token={result["oauth_token"]}')
    click.echo(f'oauth_token_secret={result["oauth_token_secret"]}')
    click.echo('Well done!')
    if save_config:
        config_values = {
            'DEFAULT' : {
                'CONSUMER_KEY' : consumer_key,
                'CONSUMER_SECRET': consumer_secret,
                'OAUTH_TOKEN': result["oauth_token"],
                'OAUTH_TOKEN_SECRET': result['oauth_token_secret']
            }
        }
        save_config_file(config_values,os.path.expanduser('~'))
    


def save_config_file(config_dict:dict,dir='.'):
    config = configparser.ConfigParser()
    config.read_dict(config_dict)
    with open(f"{dir}/meocloud.ini",'w') as ini_file:
        config.write(ini_file)
        ini_file.close()

if __name__ == '__main__':
    cli()

def main():
    cli()
