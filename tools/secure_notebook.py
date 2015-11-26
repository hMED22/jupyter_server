#!/usr/bin/env python
"""
script to automatically setup notebook over SSL.

Generate cert and keyfiles (rsa 1024) in ~/.ssh/, ask for a password, and add
the corresponding entries in the notbook json configuration file. 

"""

import six

from notebook.auth import passwd
from traitlets.config.loader import JSONFileConfigLoader, ConfigFileNotFound
from jupyter_core.paths import jupyter_config_dir
from traitlets.config import Config

from contextlib import contextmanager

from OpenSSL import crypto, SSL
from socket import gethostname
from pprint import pprint
from time import gmtime, mktime
from os.path import exists, join

import io
import os
import json


def create_self_signed_cert(cert_dir, keyfile, certfile):
    """
    Create a self-signed `keyfile` and `certfile` in `cert_dir`

    Abort if one of the
    """

    if not exists(join(cert_dir, certfile)) \
            or not exists(join(cert_dir, keyfile)):

        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 1024)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "US"
        cert.get_subject().ST = "Jupyter notebook self-signed certificate"
        cert.get_subject().L = "Jupyter notebook self-signed certificate"
        cert.get_subject().O = "Jupyter notebook self-signed certificate"
        cert.get_subject().OU = "my organization"
        cert.get_subject().CN = "Jupyter notebook self-signed certificate"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha256')

        with io.open(join(cert_dir, certfile), "wt") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf8'))
        with io.open(join(cert_dir, keyfile), "wt") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode('utf8'))
    else :
        raise FileExistsError('{} or {} already exist in {}. Aborting.'.format(keyfile, certfile, certdir))



@contextmanager
def load_config():
    """Conext manager that can be use to modify a config object

    on exit of the context manager, the config will be written back to disk. 
    """

    loader = JSONFileConfigLoader('jupyter_notebook_config.json', jupyter_config_dir())
    try:
        config = loader.load_config()
    except ConfigFileNotFound:
        config = Config()

    yield config

    with io.open(os.path.join(jupyter_config_dir(), 'jupyter_notebook_config.json'), 'w') as f:
        f.write(six.u(json.dumps(config, indent=2)))


def set_password():
    """Ask user for password, store it in notebook json configuration file"""

    print("first choose a password.")
    pw = passwd()
    print("We will store your password encrypted in the notebook configuration file: ")
    print(pw)

    with load_config() as config:
        config.NotebookApp.password = pw

    print('... done\n')


def set_certifs():
    """
    generate certificate to run notebook over ssl and set up the notebook config.
    """
    print("Let's generate self-signed certificates to secure your connexion.")
    print("where should the certificate live?")

    location = input('path [~/.ssh]: ')
    if not location.strip():
        location = os.path.expanduser('~/.ssh')
    keyfile = input('keyfile name [jupyter_server.key]: ')
    if not keyfile.strip():
        keyfile = 'jupyter_server.key'
    certfile = input('certfile name [jupyter_server.crt]: ')
    if not certfile.strip():
        certfile = 'jupyter_server.crt'

    create_self_signed_cert(location, keyfile, certfile)

    fullkey = os.path.join(location, keyfile)
    fullcrt = os.path.join(location, certfile)
    with load_config() as config:
        config.NotebookApp.certfile = fullcrt
        config.NotebookApp.keyfile = fullkey

    print('done.\n')


if __name__ == '__main__':
    print("This guide you into securing your notebook server.")
    set_password()
    set_certifs()
