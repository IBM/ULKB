import os
import sys
sys.path.insert(0, os.path.abspath('..'))


def get_copyright():
    import datetime
    copyright = os.getenv('COPYRIGHT')
    if copyright.endswith('.'):
        copyright = copyright[:-1]
    end_year = datetime.date.today().year
    start_year = int(os.getenv('COPYRIGHT_START_YEAR', end_year))
    if start_year < end_year:
        return f'{start_year}-{end_year}, {copyright}'
    else:
        return f'{end_year}, {copyright}'


project = os.getenv('PACKAGE')
copyright = get_copyright()

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
add_module_names = False
autosummary_generate = True
#autodoc_member_order = 'groupwise'
#autodoc_member_order = 'bysource'
#autodoc_member_order = 'alphabetical'
graphviz_output_format = 'svg'
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

html_static_path = ['_static']
#html_theme = 'sphinx_rtd_theme'
html_theme = 'pydata_sphinx_theme'
html_context = {'default_mode': 'light'}
