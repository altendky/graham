import click
import requests


@click.command()
@click.option('--topics', type=click.File('r'), default='.gitignore.io')
@click.option('--local', type=click.File('r'), default='.gitignore.local')
@click.option(
    '--output',
    type=click.File('w+', atomic=True),
    default='.gitignore',
)
def cli(topics, local, output):
    topic_list = [line.strip() for line in topics.readlines()]

    response = requests.get(
        'https://www.gitignore.io/api/' + ','.join(topic_list),
    )
    response.raise_for_status()

    output.write('# Local\n\n')
    output.write(local.read().strip() + '\n\n')
    output.write(response.text)
