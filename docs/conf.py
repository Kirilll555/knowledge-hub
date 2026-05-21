import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'Knowledge Hub'
copyright = '2026, Knowledge Hub Team'
author = 'Knowledge Hub Team'
release = '0.10.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build']

html_theme = 'alabaster'
html_static_path = ['_static']
language = 'ru'

autodoc_member_order = 'bysource'
