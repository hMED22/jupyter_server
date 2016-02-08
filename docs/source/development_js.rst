.. _development_js:

Installing JavaScript machinery
===============================

.. note::

    This section is prepared for contributors to the Notebook source code.
    Users of the released Notebook do not need to install the JavaScript
    tools.

Building the Notebook from its GitHub source code requires some tools to
create and minify JavaScript components and the CSS. These tools and the
following steps are used when making a Notebook release.

#. Install `Node.js`_ and :program:`npm`.

   - Using the installers on `Node.js`_ website:
     Select a pre-built installer
     on the `Node.js`_ website. The installer will include Node.js and
     Node's package manager, :program:`npm`.

   - Using system's package manager:
     Install Node.js and :program:`npm` using the
     system's package manager. For example, the command for Ubuntu or Debian
     is:

     .. code:: bash

         sudo apt-get install nodejs-legacy npm

#. Install the notebook:

   In the notebook repo, do a development install:
   
   .. code:: bash
   
       pip install -e .

#. Rebuild JavaScript and CSS

   There is a build step for the JavaScript and CSS in the notebook.
   You will need to run this command whenever there are changes to JavaScript or LESS sources:
  
   .. code:: bash

       python setup.py js css

   This command will automatically fetch any missing dependencies (bower,
   less) and install them in a subdirectory.


Prototyping tip
---------------

When doing prototyping which needs quick iteration of the Notebook's
JavaScript, the bundled and minified JavaScript may be deactivated. To do
this, start the Notebook with the option
``--NotebookApp.ignore_minified_js=True``.  This increases
the number of requests that the browser makes to the server, but it allows
testing JavaScript file modification without going through the time consuming
compilation step that may take up to 30 seconds.


.. _Node.js: https://nodejs.org
