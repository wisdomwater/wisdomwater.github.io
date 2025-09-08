import os
import re
import sys
import time

import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command(short_help="Compile into output files")
@click.argument("book")
@click.option("-p", "--pdf", is_flag=True, help="Generate PDF")
@click.option("-e", "--epub", is_flag=True, help="Generate ePub")
def compile(book, pdf, epub):
    """
    Compile into output file formats
    """
    # If neither is specified, do both
    if not pdf and not epub:
        pdf = True
        epub = True

    compiler = BOOKS.get(book)()
    if not compiler:
        print(f"Unknown book: {book}")
        sys.exit(1)

    compiler.create_md()
    if epub:
        compiler.create_epub()
    if pdf:
        compiler.create_pdf()
    compiler.copy_downloads()


def pistis_sophia():
    from books.pistis_sophia import PistisSophia
    return PistisSophia()


BOOKS = {
    "pistis-sophia": pistis_sophia,
}

if __name__ == "__main__":
    cli(prog_name="do")
