# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------

# Add the package directory to sys.path
package_root = Path(__file__).resolve().parents[2]  # two levels up from source/
sys.path.insert(0, str(package_root / "src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'simeasren'
copyright = '2025, Nicolas Campion, Giulia Montanari'
author = 'Nicolas Campion, Giulia Montanari'
release = '0.0.1'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",    # Google-style or NumPy-style docstrings
    "sphinx.ext.viewcode",    # add links to source code
    "myst_parser",            # Markdown support
    "autoapi.extension",      # Automatic API docs
]


# -------------------- AutoAPI settings --------------------
autoapi_type = "python"
autoapi_dirs = [str(package_root / "src" / "simeasren")]  # your package folder
autoapi_root = "api"  # where docs will be generated (inside 'build/html/api')
autoapi_add_toctree_entry = True
autoapi_keep_files = True   # keeps intermediate files
autoapi_member_order = "bysource"

# Paths that contain templates
templates_path = ["_templates"]

# List of patterns to ignore
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']