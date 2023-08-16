# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .. import util
from ..settings import Settings

__all__ = [
    'GraphSettings',
]


class GraphSettings(Settings):
    uri = 'https://query.wikidata.org/sparql'

    namespaces = {
        'bd': 'http://www.bigdata.com/rdf#',
        'cn': 'http://conceptnet.io/',
        'cnc': 'http://conceptnet.io/c/en/',
        'cnr': 'http://conceptnet.io/r/',
        'schema': 'http://schema.org/',
        'skos': 'http://www.w3.org/2004/02/skos/core#',
        'ulkb': 'http://www.ibm.com/ULKB#',
        'wd': 'http://www.wikidata.org/entity/',
        'wdno': 'http://www.wikidata.org/prop/novalue/',
        'wds': 'http://www.wikidata.org/entity/statement/',
        'wdt': 'http://www.wikidata.org/prop/direct/',
        'wdv': 'http://www.wikidata.org/value/',
        'wikibase': 'http://wikiba.se/ontology#',
    }

    with_description = True
    with_description_suffix = 'Description'
    with_description_predicate = 'schema:description'
    with_description_language = 'en'
    with_description_extra = None

    with_label = True
    with_label_suffix = 'Label'
    with_label_predicate = 'rdfs:label'
    with_label_language = 'en'
    with_label_extra = None

    limit = None
    timeout = None

    def _get_namespace_manager(self, extra=dict()):
        from rdflib import Graph, URIRef
        from rdflib.namespace import NamespaceManager
        nsm = NamespaceManager(Graph())
        ns_dict = dict()
        for k, v in util.chain(self.namespaces.items(), extra.items()):
            nsm.bind(k, v)
            ns_dict[k] = v
        setattr(nsm, '_namespace_dict', ns_dict)
        return nsm
