The RDF/OWL files (in ttl format) for the current version of ULKB. Both the individual building blocks and the aggregate, single-file deployment are included here: 

INDIVIDUAL FILES: 

1. ulkb.ttl -- This is the upper ontology of ULKB. It defines the main hierarchies of the ontology: 
      ulkb:Context,  represents subgraphs pointing to knowledge bases, overlays, spatial and temporal contexts, etc.
      
      ulkb:DataTypesAndExpressionsBase,  represents the logic statements plus special types.

      ulkb:DomainEntity, represents the ontologic knowledge.  The objects in the world that the underlying KBs describe. The current public version does not include instances of this hierarchy. 

      ulkb:KBElement,  describes the federated knowledge bases.  Currently, the following knowledge bases are supported: PropBank (https://propbank.github.io/), VerbNet (https://verbs.colorado.edu/verb-index/vn/class-h.php), WordNet verbs (https://wordnet.princeton.edu/download/current-version). In upcoming versions we'll support Wikidata and ConceptNet as virtual graphs (not directly included in ULKB but accessed through entity and relation overlays).  When an item is stored directly in ULKB, it has a property, ulkb:inKB, which points to its provenance in one or more of the federated knowledge bases.
      
      ulkb:LinguisticClass, describes the linguistic knowledge bases. In particular, the class ulkb:Semset represents the main lexical unit of the KB, be it a roleset in PropBank, a class in VerbNet or a synset in WordNet. Other important classes in this hierarchy include ulkb:Lemma, ulkb:Frame, and ulkb:SemanticRole. 
 
2. time.owl -- encapsulates the OWL-Time ontology (from https://www.w3.org/TR/owl-time/ a W3C candidate recommendation), included here for convenience. 

3. ULKB_DATA_V6.ttl -- Instances and instance relations. The current version includes Propbank rolesets, Verbnet Classes and Wordnet verb synsets, linked using Semlink (https://verbs.colorado.edu/semlink/) and human curation.

AGGREGATE FILE: ULKB_V6_PUB.ttl -- It includes all of the above graphs in a single file for deployment convenience. 
