"""Tornado handlers for the sessions web service.

Preliminary documentation at https://github.com/ipython/ipython/wiki/IPEP-16%3A-Notebook-multi-directory-dashboard-and-URL-mapping#sessions-api
"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import os

from tornado import gen, web

from ...base.handlers import APIHandler, json_errors
from jupyter_client.jsonutil import date_default
from notebook.utils import url_path_join
from jupyter_client.kernelspec import NoSuchKernel


class SessionRootHandler(APIHandler):

    @web.authenticated
    @json_errors
    @gen.coroutine
    def get(self):
        # Return a list of running sessions
        sm = self.session_manager
        sessions = yield gen.maybe_future(sm.list_sessions())
        self.finish(json.dumps(sessions, default=date_default))

    @web.authenticated
    @json_errors
    @gen.coroutine
    def post(self):
        # Creates a new session
        #(unless a session already exists for the named session)
        sm = self.session_manager

        model = self.get_json_body()
        if model is None:
            raise web.HTTPError(400, "No JSON data provided")

        try:
            name = model['name']
        except KeyError:
            raise web.HTTPError(400, "Missing field in JSON data: name")

        try:
            directory = model['directory']
        except KeyError:
            raise web.HTTPError(400, "Missing field in JSON data: directory")

        model_type = model.get('type', 'notebook')

        kernel = model.get('kernel', {})
        kernel_name = kernel.get('name') or None
        kernel_id = kernel.get('id') or None

        if not kernel_id and not kernel_name:
            self.log.debug("No kernel specified, using default kernel")
            kernel_name = None

        # Check to see if session exists
        path = os.path.join(directory, name)
        exists = yield gen.maybe_future(sm.session_exists(path=path))
        if exists:
            model = yield gen.maybe_future(sm.get_session(path=path))
        else:
            try:
                model = yield gen.maybe_future(
                    sm.create_session(path=path, kernel_name=kernel_name,
                                      kernel_id=kernel_id,
                                      type=model_type))
            except NoSuchKernel:
                msg = ("The '%s' kernel is not available. Please pick another "
                       "suitable kernel instead, or install that kernel." % kernel_name)
                status_msg = '%s not found' % kernel_name
                self.log.warning('Kernel not found: %s' % kernel_name)
                self.set_status(501)
                self.finish(json.dumps(dict(message=msg, short_message=status_msg)))
                return

        location = url_path_join(self.base_url, 'api', 'sessions', model['id'])
        self.set_header('Location', location)
        self.set_status(201)
        self.finish(json.dumps(model, default=date_default))


class SessionHandler(APIHandler):

    @web.authenticated
    @json_errors
    @gen.coroutine
    def get(self, session_id):
        # Returns the JSON model for a single session
        sm = self.session_manager
        model = yield gen.maybe_future(sm.get_session(session_id=session_id))
        self.finish(json.dumps(model, default=date_default))

    @web.authenticated
    @json_errors
    @gen.coroutine
    def patch(self, session_id):
        """Patch updates sessions:

        - notebook.path updates session to track renamed notebooks
        - kernel.name starts a new kernel with a given kernelspec
        """
        sm = self.session_manager
        km = self.kernel_manager
        model = self.get_json_body()
        if model is None:
            raise web.HTTPError(400, "No JSON data provided")

        # get the previous session model
        before = yield gen.maybe_future(sm.get_session(session_id=session_id))

        changes = {}
        if 'name' in model:
            changes['name'] = model['name']
        if 'type' in model:
            changes['type'] = model['type']
        if 'kernel' in model:
            # Kernel id takes precedence over name.
            if model['kernel'].get('id') is not None:
                kernel_id = model['kernel']['id']
                if kernel_id not in km:
                    raise web.HTTPError(400, "No such kernel: %s" % kernel_id)
                changes['kernel_id'] = kernel_id
            elif model['kernel'].get('name') is not None:
                kernel_name = model['kernel']['name']
                kernel_id = yield sm.start_kernel_for_session(
                    session_id, kernel_name=kernel_name, path=before['notebook']['path'])
                changes['kernel_id'] = kernel_id

        yield gen.maybe_future(sm.update_session(session_id, **changes))
        model = yield gen.maybe_future(sm.get_session(session_id=session_id))

        if model['kernel']['id'] != before['kernel']['id']:
            # kernel_id changed because we got a new kernel
            # shutdown the old one
            yield gen.maybe_future(
                km.shutdown_kernel(before['kernel']['id'])
            )
        self.finish(json.dumps(model, default=date_default))

    @web.authenticated
    @json_errors
    @gen.coroutine
    def delete(self, session_id):
        # Deletes the session with given session_id
        sm = self.session_manager
        try:
            yield gen.maybe_future(sm.delete_session(session_id))
        except KeyError:
            # the kernel was deleted but the session wasn't!
            raise web.HTTPError(410, "Kernel deleted before session")
        self.set_status(204)
        self.finish()


#-----------------------------------------------------------------------------
# URL to handler mappings
#-----------------------------------------------------------------------------

_session_id_regex = r"(?P<session_id>\w+-\w+-\w+-\w+-\w+)"

default_handlers = [
    (r"/api/sessions/%s" % _session_id_regex, SessionHandler),
    (r"/api/sessions",  SessionRootHandler)
]

