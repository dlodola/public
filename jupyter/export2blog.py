#!/usr/bin/env python

import argparse
from datetime import date
from datetime import datetime
from html.parser import HTMLParser
import logging
import logging
from math import ceil, log
from os import rename, remove
from os.path import basename, splitext, join, normpath, isdir, isfile
import re
import sys
from shutil import move, rmtree
import sys
import tempfile
from urllib.parse import quote_plus, quote

from bs4 import BeautifulSoup
from nbformat import read
from nbconvert import MarkdownExporter
from nbconvert.nbconvertapp import NbConvertApp
from nbconvert.preprocessors import Preprocessor
from nbconvert.writers import FilesWriter


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(levelname)-12s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


rootLogger = logging.getLogger("Root Logger")
rootLogger.setLevel(logging.DEBUG)
# consolelogFormatter = logging.Formatter("[%(levelname)-5.5s]  %(message)s")
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(CustomFormatter())
rootLogger.addHandler(consoleHandler)

# extract notebook address from args
parser = argparse.ArgumentParser()
parser.add_argument("notebook")
args = parser.parse_args()
notebook = args.notebook
output_dir = tempfile.mkdtemp()
notebook_name = splitext(basename(notebook))[0]
rootLogger.info("Converting '{}'.".format(notebook))

with open(notebook, 'r', encoding='utf-8') as f:
    nb = read(f, 4)

try:
    date = nb.metadata.date
except AttributeError:
    date = date.isoformat(date.today())
    rootLogger.warn('No date found in notebook metadata.')

try:
    output_name = quote_plus(
        date
        + '-'
        + nb.metadata.title, safe='/'
    )
except AttributeError:
    output_name = quote_plus(
        date
        + '_'
        + notebook_name
    )
    rootLogger.warn('No title found in notebook metadata.')
finally:
    rootLogger.info("Setting post name to '{}'.".format(notebook_name))


def format_number(a, digits=3, e_lim=1e6):
    if a == 0:
        fmt = '.0f'
    elif abs(a) >= e_lim:
        fmt = '.1e'
    elif abs(a) >= 1:
        digits = max(0, digits - ceil(log(abs(a), 10) - 1))
        fmt = '.{}f'.format(digits)
    else:
        fmt = '.{}f'.format(-ceil(log(abs(a), 10)) + digits)
    return '{:,{}}'.format(a, fmt)


class CustomPreprocess(Preprocessor):

    def preprocess(self, nb, resources):

        files = []
        pre = """<div class="equation">\n\t<div>"""
        post = """</div>\n<div class="equation_dots"></div>\n"""
        post += "<div></div>\n"
        post += "</div>\n"
        img_pre = '{{ site.url }}' + 'assets/images/posts/'
        img_pre += quote(output_name) + '_files/'

        for cell in nb.cells[:]:

            try:
                assert cell.metadata["exclude"]
            except KeyError:
                pass
            else:
                nb.cells.remove(cell)
                continue

            if cell.source == '':
                nb.cells.remove(cell)
                continue

            if cell.cell_type == 'markdown':
                s = re.sub(r"^\# .+\n\n",
                           '',
                           cell.source,
                           flags=re.MULTILINE)
                s = re.sub(r'\\\\\[', pre + r'\\[', s)
                s = re.sub(r'\\\\\]', r'\\]' + post, s)

                soup = BeautifulSoup(s, 'html.parser')

                for img in soup.findAll('img'):
                    files.append(img['src'])
                    img['src'] = img_pre + basename(img['src'])
                    del img['width']
                    img['class'] = 'scaled'
                for a in soup.findAll('a'):
                    try:
                        a['href'] = (a.img['src'])
                    except KeyError:
                        pass
                for caption in soup.findAll('figcaption'):
                    c = caption.get_text()
                    c = re.sub(r'^Figure \d+: ', '', c)
                    caption.string = c

                # replace > for md quotes
                cell.source = re.sub(
                    '^&gt; ',
                    '> ',
                    str(soup),
                    flags=re.MULTILINE
                )
if len(md_writer.files) > 0:
    rootLogger.info("Collating files...")
    for file in md_writer.files:
        src = normpath(
            join(
                output_dir,
                file
            )
        )
        dst = join(
            output_dir,
            output_name + '_files',
            basename(file)
        )
        rename(src, dst)
        rootLogger.info("Moving '{}'".format(src))
        rootLogger.info("to '{}'".format(dst))
    rootLogger.info("...done.")
                            except ValueError:
                                pass
                            else:
                                td.string = format_number(val, 3)
                        output.data['text/html'] = str(soup)

        try:
            nb.metadata.notebook

        except AttributeError:
            nb.metadata.notebook = notebook_name

        md_writer.files = files

        return nb, resources


app = NbConvertApp(
    output_base=output_name
)
md_exporter = MarkdownExporter(
    template_file='./index.md.j2',
    preprocessors=[CustomPreprocess]
)
md_writer = FilesWriter(
    build_directory=output_dir
)
app.exporter = md_exporter
app.writer = md_writer
app.convert_single_notebook(notebook)

if len(md_writer.files) > 0:
    rootLogger.info("Collating files...")
    for file in md_writer.files:
        src = normpath(
            join(
                output_dir,
                file
            )
        )
        dst = join(
            output_dir,
            output_name + '_files',
            basename(file)
        )
        rename(src, dst)
        rootLogger.info("Moving '{}'".format(src))
        rootLogger.info("to '{}'".format(dst))
    rootLogger.info("...done.")

src = join(output_dir, output_name + '_files')
dst = join('../docs/assets/images/posts/', output_name + '_files')
try:
    assert isdir(dst)
except AssertionError:
    pass
else:
    
    rmtree(dst)
finally:
    try:
        assert isdir(src)
    except AssertionError:
        pass
    else:
        move(src, dst)

src = join(output_dir, output_name + '.md')
dst = join('../docs/_posts/', output_name + '.md')
try:
    assert isfile(dst)
except AssertionError:
    pass
else:
    remove(dst)
finally:
    try:
        assert isfile(src)
    except AssertionError:
        pass
    else:
        rename(src, dst)

rmtree(output_dir)
