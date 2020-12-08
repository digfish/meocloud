import click
from meocloud.services import MeoCloud

@click.group()
def cli():
    pass

@cli.command()
@click.option('--consumer_key', prompt='Your consumer key', help='your consumer key')
@click.option('--consumer_secret', prompt='Your consumer secret', help='your consumer secret')
@click.option('--callback_uri', prompt='Your callback uri', default='oob', help='your callback uri')
def mycredential(consumer_key, consumer_secret, callback_uri):
    meo = MeoCloud(consumer_key=consumer_key, consumer_secret=consumer_secret)
    authorize = meo.authorize
    click.echo(f'Go to the following link in your browser: {authorize["authorize_url"]}')
    pin = click.prompt('Please enter a valid pin', type=str)
    meo = MeoCloud(consumer_key=consumer_key, consumer_secret=consumer_secret, oauth_token=authorize["oauth_token"], oauth_token_secret=authorize["oauth_token_secret"], callback_uri=callback_uri)
    result = meo.get_my_credential(pin)
    click.echo(f'oauth_token={result["oauth_token"]}')
    click.echo(f'oauth_token_secret={result["oauth_token_secret"]}')
    click.echo('Well done!')

if __name__ == '__main__':
    cli()

def main():
    cli()