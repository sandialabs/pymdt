# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
sys.path.insert(0, os.path.abspath(".."))
print("curr path is " + os.path.abspath("."))
items = os.listdir(os.path.abspath("."))
for item in items:
    print(item)

print("parent path is " + os.path.abspath(".."))
items = os.listdir(os.path.abspath(".."))
for item in items:
    print(item)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'sandia-pymdt'
copyright = '2025, John Eddy'
author = 'Sandia National Laboratories'
release = '1.4.2520'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc']
todo_include_todos = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

def skip(app, what, name, obj, skip, options):
    if what == "module" and "details" in name:
        return True
    return None

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


def setup(app):
    print("connecting to skipmember")
    app.connect("autodoc-skip-member", skip)
