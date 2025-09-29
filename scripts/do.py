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
@click.option("-b", "--paperback", is_flag=True, help="Generate Paperback PDF")
@click.option("-e", "--epub", is_flag=True, help="Generate ePub")
@click.option("-d", "--docx", is_flag=True, help="Generate DOCX")
def compile(book, paperback, pdf, epub, docx):
    """
    Compile into output file formats
    """
    # If neither is specified, do both
    if not pdf and not paperback and not epub and not docx:
        pdf = True
        paperback = True
        epub = True
        docx = True

    booker = BOOKS.get(book)()
    if not booker:
        print(f"Unknown book: {book}")
        sys.exit(1)

    booker.create_md()
    if epub:
        booker.create_epub()
    if pdf:
        booker.create_pdf()
    if paperback:
        booker.create_paperback_pdf()
    if docx:
        booker.create_docx()
    booker.copy_downloads()


@cli.command(short_help="Publish book assets")
@click.argument("book")
@click.option("--no-compile", is_flag=True, help="Do not compile first")
def publish(book, no_compile):
    """
    Publish book assets
    """
    if not no_compile:
        exit_code = os.system(f"do compile {book}")
        if exit_code != 0:
            print("Failed to compile")
            sys.exit(1)
    
    booker = BOOKS.get(book)()
    if not booker:
        print(f"Unknown book: {book}")
        sys.exit(1)
    booker.publish()


def pistis_sophia():
    from books.pistis_sophia import PistisSophia
    return PistisSophia()


def the_greater_mercy():
    from books.the_greater_mercy import TheGreaterMercy
    return TheGreaterMercy()


def the_journey_home():
    from books.the_journey_home import TheJourneyHome
    return TheJourneyHome()


def the_way_of_the_pilgrim():
    from books.the_way_of_the_pilgrim import TheWayOfThePilgrim
    return TheWayOfThePilgrim()


BOOKS = {
    "pistis-sophia": pistis_sophia,
    "the-greater-mercy": the_greater_mercy,
    "the-journey-home": the_journey_home,
    "the-way-of-the-pilgrim": the_way_of_the_pilgrim,
}

if __name__ == "__main__":
    cli(prog_name="do")
