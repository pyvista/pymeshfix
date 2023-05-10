"""Configuration for the documentation generation of pymeshfix."""
import datetime
import os

import numpy as np
import pymeshfix

# -- pyvista configuration ---------------------------------------------------
import pyvista

# Manage errors
pyvista.set_error_output_file("errors.txt")
# Ensure that offscreen rendering is used for docs generation
pyvista.OFF_SCREEN = True  # Not necessary - simply an insurance policy
# Preferred plotting style for documentation
pyvista.set_plot_theme("document")
pyvista.rcParams["window_size"] = np.array([1024, 768]) * 2
# Save figures in specified directory
pyvista.FIGURE_PATH = os.path.abspath("./images/")
if not os.path.exists(pyvista.FIGURE_PATH):
    os.makedirs(pyvista.FIGURE_PATH)

pyvista.BUILDING_GALLERY = True

# -- Project information -----------------------------------------------------

project = "pymeshfix"
year = datetime.date.today().year
copyright = f"2017-{year}, The PyVista Developers"
author = "Alex Kaszynski"

# The short X.Y version
version = release = pymeshfix.__version__


# -- General configuration ---------------------------------------------------
html_logo = "./_static/pyvista_logo_sm.png"

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    "notfound.extension",
    "sphinx_copybutton",
    "sphinx_gallery.gen_gallery",
    "sphinx.ext.extlinks",
]

html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Copy button customization ---------------------------------------------------
# exclude traditional Python prompts from the copied code
copybutton_prompt_text = r">>> ?|\.\.\. "
copybutton_prompt_is_regexp = True


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_context = {
    # Enable the "Edit in GitHub link within the header of each page.
    "display_github": True,
    # Set the following variables to generate the resulting github URL for each page.
    # Format Template: https://{{ github_host|default("github.com") }}/{{ github_user }}/{{ github_repo }}/blob/{{ github_version }}{{ conf_py_path }}{{ pagename }}{{ suffix }}
    "github_user": "pyvista",
    "github_repo": "pymeshfix",
    "github_version": "master/doc/",
    "menu_links_name": "Getting Connected",
    "menu_links": [
        ('<i class="fa fa-slack fa-fw"></i> Slack Community', "http://slack.pyvista.org"),
        (
            '<i class="fa fa-comment fa-fw"></i> Support',
            "https://github.com/pyvista/pyvista-support",
        ),
        ('<i class="fa fa-github fa-fw"></i> Source Code', "https://github.com/pyvista/pymeshfix"),
    ],
}

html_theme_options = {
    "show_prev_next": False,
    "github_url": "https://github.com/pyvista/pymeshfix",
    "logo": {
        "image_light": "pyvista_logo_sm.png",
        "image_dark": "pyvista_logo_sm.png",
    },
}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "PyMeshFix"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "pymeshfix.tex", "PyMeshFix Documentation", "Alex Kaszynski", "manual"),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "PyMeshFix", "PyMeshFix Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "PyMeshFix",
        "PyMeshFix Documentation",
        author,
        "PyMeshFix",
        "One line description of project.",
        "Miscellaneous",
    ),
]


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "https://docs.python.org/": None,
    "https://docs.pyvista.org": None,
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Sphinx Gallery Options
from sphinx_gallery.sorting import FileNameSortKey

sphinx_gallery_conf = {
    # path to your examples scripts
    "examples_dirs": [
        "../examples/",
    ],
    # path where to save gallery generated examples
    "gallery_dirs": ["examples"],
    # Pattern to search for example files
    "filename_pattern": r"\.py",
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    "within_subsection_order": FileNameSortKey,
    # directory where function granular galleries are stored
    "backreferences_dir": None,
    # Modules for which function level galleries are created.  In
    "doc_module": "pymeshfix",
    "image_scrapers": (pyvista.Scraper(), "matplotlib"),
    "thumbnail_size": (350, 350),
}


# -- Custom 404 page

notfound_no_urls_prefix = True
