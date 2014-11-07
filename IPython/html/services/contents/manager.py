"""A base class for contents managers."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from fnmatch import fnmatch
import itertools
import json
import os

from tornado.web import HTTPError

from IPython.config.configurable import LoggingConfigurable
from IPython.nbformat import sign, validate, ValidationError
from IPython.nbformat.v4 import new_notebook
from IPython.utils.traitlets import Instance, Unicode, List


class ContentsManager(LoggingConfigurable):
    """Base class for serving files and directories.

    This serves any text or binary file,
    as well as directories,
    with special handling for JSON notebook documents.

    Most APIs take a path argument,
    which is always an API-style unicode path,
    and always refers to a directory.

    - unicode, not url-escaped
    - '/'-separated
    - leading and trailing '/' will be stripped
    - if unspecified, path defaults to '',
      indicating the root path.

    """

    notary = Instance(sign.NotebookNotary)
    def _notary_default(self):
        return sign.NotebookNotary(parent=self)

    hide_globs = List(Unicode, [
            u'__pycache__', '*.pyc', '*.pyo',
            '.DS_Store', '*.so', '*.dylib', '*~',
        ], config=True, help="""
        Glob patterns to hide in file and directory listings.
    """)

    untitled_notebook = Unicode("Untitled", config=True,
        help="The base name used when creating untitled notebooks."
    )

    untitled_file = Unicode("untitled", config=True,
        help="The base name used when creating untitled files."
    )

    untitled_directory = Unicode("Untitled Folder", config=True,
        help="The base name used when creating untitled directories."
    )

    # ContentsManager API part 1: methods that must be
    # implemented in subclasses.

    def dir_exists(self, path):
        """Does the API-style path (directory) actually exist?

        Like os.path.isdir

        Override this method in subclasses.

        Parameters
        ----------
        path : string
            The path to check

        Returns
        -------
        exists : bool
            Whether the path does indeed exist.
        """
        raise NotImplementedError

    def is_hidden(self, path):
        """Does the API style path correspond to a hidden directory or file?

        Parameters
        ----------
        path : string
            The path to check. This is an API path (`/` separated,
            relative to root dir).

        Returns
        -------
        hidden : bool
            Whether the path is hidden.

        """
        raise NotImplementedError

    def file_exists(self, path=''):
        """Does a file exist at the given path?

        Like os.path.isfile

        Override this method in subclasses.

        Parameters
        ----------
        name : string
            The name of the file you are checking.
        path : string
            The relative path to the file's directory (with '/' as separator)

        Returns
        -------
        exists : bool
            Whether the file exists.
        """
        raise NotImplementedError('must be implemented in a subclass')

    def exists(self, path):
        """Does a file or directory exist at the given name and path?

        Like os.path.exists

        Parameters
        ----------
        path : string
            The relative path to the file's directory (with '/' as separator)

        Returns
        -------
        exists : bool
            Whether the target exists.
        """
        return self.file_exists(path) or self.dir_exists(path)

    def get_model(self, path, content=True):
        """Get the model of a file or directory with or without content."""
        raise NotImplementedError('must be implemented in a subclass')

    def save(self, model, path):
        """Save the file or directory and return the model with no content."""
        raise NotImplementedError('must be implemented in a subclass')

    def update(self, model, path):
        """Update the file or directory and return the model with no content.

        For use in PATCH requests, to enable renaming a file without
        re-uploading its contents. Only used for renaming at the moment.
        """
        raise NotImplementedError('must be implemented in a subclass')

    def delete(self, path):
        """Delete file or directory by path."""
        raise NotImplementedError('must be implemented in a subclass')

    def create_checkpoint(self, path):
        """Create a checkpoint of the current state of a file

        Returns a checkpoint_id for the new checkpoint.
        """
        raise NotImplementedError("must be implemented in a subclass")

    def list_checkpoints(self, path):
        """Return a list of checkpoints for a given file"""
        return []

    def restore_checkpoint(self, checkpoint_id, path):
        """Restore a file from one of its checkpoints"""
        raise NotImplementedError("must be implemented in a subclass")

    def delete_checkpoint(self, checkpoint_id, path):
        """delete a checkpoint for a file"""
        raise NotImplementedError("must be implemented in a subclass")

    # ContentsManager API part 2: methods that have useable default
    # implementations, but can be overridden in subclasses.

    def info_string(self):
        return "Serving contents"

    def get_kernel_path(self, path, model=None):
        """ Return the path to start kernel in """
        return path

    def increment_filename(self, filename, path=''):
        """Increment a filename until it is unique.

        Parameters
        ----------
        filename : unicode
            The name of a file, including extension
        path : unicode
            The API path of the target's directory

        Returns
        -------
        name : unicode
            A filename that is unique, based on the input filename.
        """
        path = path.strip('/')
        basename, ext = os.path.splitext(filename)
        for i in itertools.count():
            name = u'{basename}{i}{ext}'.format(basename=basename, i=i,
                                                ext=ext)
            if not self.file_exists(u'{}/{}'.format(path, name)):
                break
        return name

    def validate_notebook_model(self, model):
        """Add failed-validation message to model"""
        try:
            validate(model['content'])
        except ValidationError as e:
            model['message'] = u'Notebook Validation failed: {}:\n{}'.format(
                e.message, json.dumps(e.instance, indent=1, default=lambda obj: '<UNKNOWN>'),
            )
        return model

    def new(self, model=None, path='', ext='.ipynb'):
        """Create a new file or directory and return its model with no content."""
        path = path.strip('/')
        if model is None:
            model = {}
        else:
            model.pop('path', None)
        if 'content' not in model and model.get('type', None) != 'directory':
            if ext == '.ipynb':
                model['content'] = new_notebook()
                model['type'] = 'notebook'
                model['format'] = 'json'
            else:
                model['content'] = ''
                model['type'] = 'file'
                model['format'] = 'text'
        if self.dir_exists(path):
            if model['type'] == 'directory':
                untitled = self.untitled_directory
            elif model['type'] == 'notebook':
                untitled = self.untitled_notebook
            elif model['type'] == 'file':
                untitled = self.untitled_file
            else:
                raise HTTPError(400, "Unexpected model type: %r" % model['type'])
            
            name = self.increment_filename(untitled + ext, path)
            path = u'{0}/{1}'.format(path, name)
        model = self.save(model, path)
        return model

    def copy(self, from_path, to_path=None):
        """Copy an existing file and return its new model.

        If to_name not specified, increment `from_name-Copy#.ext`.

        copy_from can be a full path to a file,
        or just a base name. If a base name, `path` is used.
        """
        path = from_path.strip('/')
        if '/' in path:
            from_dir, from_name = path.rsplit('/', 1)
        else:
            from_dir = ''
            from_name = path
        
        model = self.get_model(path)
        model.pop('path', None)
        model.pop('name', None)
        if model['type'] == 'directory':
            raise HTTPError(400, "Can't copy directories")
        
        if not to_path:
            to_path = from_dir
        if self.dir_exists(to_path):
            base, ext = os.path.splitext(from_name)
            copy_name = u'{0}-Copy{1}'.format(base, ext)
            to_name = self.increment_filename(copy_name, to_path)
            to_path = u'{0}/{1}'.format(to_path, to_name)
        
        model = self.save(model, to_path)
        return model

    def log_info(self):
        self.log.info(self.info_string())

    def trust_notebook(self, path):
        """Explicitly trust a notebook

        Parameters
        ----------
        path : string
            The path of a notebook
        """
        model = self.get_model(path)
        nb = model['content']
        self.log.warn("Trusting notebook %s", path)
        self.notary.mark_cells(nb, True)
        self.save(model, path)

    def check_and_sign(self, nb, path=''):
        """Check for trusted cells, and sign the notebook.

        Called as a part of saving notebooks.

        Parameters
        ----------
        nb : dict
            The notebook dict
        path : string
            The notebook's path (for logging)
        """
        if self.notary.check_cells(nb):
            self.notary.sign(nb)
        else:
            self.log.warn("Saving untrusted notebook %s", path)

    def mark_trusted_cells(self, nb, path=''):
        """Mark cells as trusted if the notebook signature matches.

        Called as a part of loading notebooks.

        Parameters
        ----------
        nb : dict
            The notebook object (in current nbformat)
        path : string
            The notebook's directory (for logging)
        """
        trusted = self.notary.check_signature(nb)
        if not trusted:
            self.log.warn("Notebook %s is not trusted", path)
        self.notary.mark_cells(nb, trusted)

    def should_list(self, name):
        """Should this file/directory name be displayed in a listing?"""
        return not any(fnmatch(name, glob) for glob in self.hide_globs)
