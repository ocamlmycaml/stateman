import click

from examples import hello_world


@click.group()
def cli():
    """This is a management script for hello_world"""


@cli.command()
def print_hello_world():
    """
    Example command, prints hello world to stdout
    """
    hello_world.print_hello_world()


if __name__ == "__main__":
    cli()
