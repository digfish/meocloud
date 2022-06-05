from turtle import dot
import click
from meocloud.services import MeoCloud
import webbrowser

@click.group()
def cli():
    pass

@cli.command()
@click.option('--consumer_key', prompt='Your consumer key', help='your consumer key')
@click.option('--consumer_secret', prompt='Your consumer secret', help='your consumer secret')
@click.option('--callback_uri', prompt='Your callback uri', default='oob', help='your callback uri')
@click.option('--save-env',prompt='store the credentials in a .env file?',default=True,help='save the credentials in a .env file', type=bool)
def mycredential(consumer_key, consumer_secret, callback_uri, save_env):
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
    if save_env:
        dotenv_values = {
            'CONSUMER_KEY' : consumer_key,
            'CONSUMER_SECRET': consumer_secret,
            'OAUTH_TOKEN': result["oauth_token"],
            'OAUTH_TOKEN_SECRET': result['oauth_token_secret']
        }
        save_dotenv(dotenv_values)
    


def save_dotenv(dotenv_values:dict):
    with open('.env','w') as dotenv_file:
        for (k,v) in dotenv_values.items():
            dotenv_file.write(f"{k}={v}\n")
        dotenv_file.close()

if __name__ == '__main__':
    cli()

def main():
    cli()
