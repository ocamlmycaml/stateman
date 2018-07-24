import click

from examples import hello_world


@click.group()
def cli():
    """This is a management script for hello_world"""


@cli.command()
def say_hello():
    """
    Example command, prints hello world to stdout
    """
    hello_world.say_hello()


if __name__ == "__main__":
    cli()
