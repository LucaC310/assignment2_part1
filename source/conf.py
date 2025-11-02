# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import subprocess
import sys

# Add your package source path
sys.path.insert(0, os.path.abspath('../..'))

# Add the path to generated ROS Python modules
ros_generated_path = os.path.abspath('../../devel/lib/python3/dist-packages')
if os.path.isdir(ros_generated_path):
    sys.path.insert(0, ros_generated_path)

# Mock ROS-specific imports if they still fail (prevents autodoc warnings)
autodoc_mock_imports = [
    'rospy',
    'actionlib',
    'nav_pkg.msg',
    'nav_pkg.srv'
]

show_authors=True

project = 'nav_pkg'
copyright = '2025, Luca Carpaneto'
author = 'Luca Carpaneto'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [ 
'sphinx.ext.autodoc', 
'sphinx.ext.doctest', 
'sphinx.ext.intersphinx', 
'sphinx.ext.todo', 
'sphinx.ext.coverage', 
'sphinx.ext.mathjax', 
'sphinx.ext.ifconfig', 
'sphinx.ext.viewcode', 
'sphinx.ext.githubpages', 
'sphinx.ext.napoleon',
'sphinx.ext.inheritance_diagram',
'breathe'
 ]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

highlight_language = 'python'
source_suffix = '.rst'
master_doc = 'index'
html_theme = 'sphinx_rtd_theme'
