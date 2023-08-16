# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import requests

from .. import util
from .error import GraphError

__all__ = [
    'SPARQL'
]


class SPARQL:
    def __init__(self, uri, **kwargs):
        self._uri = uri
        self._timeout = None
        self._headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/sparql-query',
        }

    @property
    def uri(self):
        return self._uri

    @property
    def headers(self):
        return self._headers

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout

    def eval(self, text):
        res = requests.post(
            self.uri, data=text, headers=self.headers, timeout=self.timeout)
        try:
            res.raise_for_status()
            return res.json()
        except Exception as err:
            raise GraphError(f'bad response for query:\n{res.text}')
