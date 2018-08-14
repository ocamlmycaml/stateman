import click

from examples import demo


@click.group()
def cli():
    """This is a management script for hello_world"""


@cli.command()
def run_demo():
    """Performs a demo, considering a server group with a few nodes"""
    demo.run_demo()


if __name__ == "__main__":
    cli()
