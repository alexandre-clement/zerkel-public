# coding: utf-8

import importlib
import subprocess
import sys
import os


def open_docs():
    from flask import Flask, send_from_directory
    
    app = Flask(__name__)

    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def catch_all(path):
        return send_from_directory(os.path.join('build', 'html'), path)

    app.run('0.0.0.0', port='8080')


def main():
    open_docs()


if __name__ == '__main__':
    main()