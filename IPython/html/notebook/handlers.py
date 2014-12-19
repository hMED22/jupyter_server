"""Tornado handlers for the live notebook view."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import os
from tornado import web
HTTPError = web.HTTPError

from ..base.handlers import (
    IPythonHandler, FilesRedirectHandler, path_regex,
)
from ..utils import url_escape


class NotebookHandler(IPythonHandler):

    @web.authenticated
    def get(self, path):
        """get renders the notebook template if a name is given, or 
        redirects to the '/files/' handler if the name is not given."""
        path = path.strip('/')
        cm = self.contents_manager
        
        # will raise 404 on not found
        model = cm.get(path, content=False)
        if model['type'] != 'notebook':
            # not a notebook, redirect to files
            return FilesRedirectHandler.get(self, path)
        name = url_escape(path.rsplit('/', 1)[-1])
        path = url_escape(path)
        self.write(self.render_template('notebook.html',
            notebook_path=path,
            notebook_name=name,
            kill_kernel=False,
            mathjax_url=self.mathjax_url,
            )
        )


#-----------------------------------------------------------------------------
# URL to handler mappings
#-----------------------------------------------------------------------------


default_handlers = [
    (r"/notebooks%s" % path_regex, NotebookHandler),
]

