#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: rosariouceda-sosa

API for ULKB. Access to the RDF/OWL UL_KB_V6 graph

Self-contained. Follow the instructions below as to how to update the SPARQL server

"""

from SPARQLWrapper import SPARQLWrapper, JSON
from nltk.stem import PorterStemmer
#import requests
#import operator
#import json

# ################################################
# CUSTOMIZE:  Enter  here the triplestore. As an example, we have a local blazegraphs server
ulkbServer = "http://127.0.0.1:9999/blazegraph/namespace/ULKB_V6"
sparql = SPARQLWrapper(ulkbServer)

# QUERIES TO THE ULKB SERVER ################################################

#This is the query prefix that is used in every query. 
query_prefix = ("prefix glo: <http://www.ibm.com/GLO_V2#> \n"
                "prefix ulvn: <http://www.ibm.com/UL_VN#> \n"
                "prefix ulwn: <http://www.ibm.com/UL_WN#> \n"
                "prefix ulpb: <http://www.ibm.com/UL_PB#> \n"
                "prefix ulkb: <http://www.ibm.com/ULKB#> \n")



query_roles_for_pb_str = """SELECT DISTINCT ?verb ?pbSemRole ?pbSemRoleDesc ?vnVerbLabel ?vnVarType ?vnVarName WHERE {{
  ?verb rdfs:label "{}" . 
  #?verb ulkb:inKB ulkb:PropBank .
  ?verb ulkb:hasParameter ?pbParam .
  ?pbParam ulkb:description ?pbSemRoleDesc .  
  ?pbParam rdfs:label ?pbSemRole . 
  OPTIONAL {{
  ?vnVerb ulkb:inKB ulkb:VerbNet . 
  ?vnVerb rdfs:label ?vnVerbLabel . 
  ?vnVerb ulkb:hasComponent ?vnFrame . 
  ?vnFrame ulkb:hasComponent ?semPred . 
  ?semPred ulkb:hasParameter ?vnParam . 
  ?pbParam ulkb:mapsTo ?vnParam . 
  ?vnParam ulkb:varType ?vnVarType . 
  ?vnParam ulkb:varName ?vnVarName . 
  }}
  }}
"""

query_roles_for_lemma_str = """SELECT DISTINCT ?pbSemRole ?vnVerbLabel ?pbVerbLabel ?vnVarType ?vnVarName WHERE {{  
  ?entity rdfs:label "{}" . 
  ?entity a ulkb:Lemma . 
  ?vnVerb ulkb:hasComponent ?entity .
  ?vnVerb ulkb:inKB ulkb:VerbNet . 
  ?vnVerb rdfs:label ?vnVerbLabel . 
  ?verb ulkb:hasParameter ?pbParam . 
  ?verb ulkb:inKB ulkb:PropBank. 
  ?verb rdfs:label ?pbVerbLabel . 
  ?pbParam rdfs:label ?pbSemRole . 
  ?vnVerb ulkb:hasComponent ?vnFrame . 
  ?vnFrame ulkb:hasComponent ?semPred . 
  ?semPred ulkb:hasParameter ?vnParam . 
  ?pbParam ulkb:mapsTo ?vnParam . 
  ?vnParam ulkb:varType ?vnVarType . 
  ?vnParam ulkb:varName ?vnVarName . 
  }} """

query_all_parents_str = """SELECT DISTINCT ?entity ?entityLabel {{  
     <{}> wdt:P31* ?entityClass . 
     ?entityClass wdt:P279* ?entity . 
     ?entity rdfs:label ?entityLabel .  
     FILTER (lang(?entityLabel) = 'en')
     }}  """

query_label_str = """SELECT DISTINCT ?entityLabel {{
     <{}>  rdfs:label ?entityLabel .  
     FILTER (lang(?entityLabel) = 'en') 
  }}
"""

query_map_classes = """SELECT DISTINCT  ?otherEntityLabel ?provenance ?KB  WHERE {{
                  <{}> ulkb:hasMapping ?mapping . 
                  ?otherEntity ulkb:hasMapping ?mapping .
                  ?otherEntity ulkb:provenance ?provenance . 
                  ?otherEntity ulkb:inKB ?KB .               
                  ?otherEntity rdfs:label ?otherEntityLabel. 
                }} ORDER BY ?otherEntity
                  """

query_sem_predicates_vn_str = """SELECT DISTINCT ?example ?roleList ?operator ?semanticPredicate ?semanticPredicateLabel ?param ?type ?value  WHERE {{
                  {} ulkb:hasComponent ?frame . 
                  ?frame ulkb:example ?example . 
                  OPTIONAL {{ ?frame ulkb:roleList ?roleList }} . 
                  ?frame ulkb:hasComponent ?semanticPredicate . 
                  ?semanticPredicate a ulkb:SemanticPredicate .
                  ?semanticPredicate rdfs:label ?semanticPredicateLabel. 
                  ?semanticPredicate ulkb:hasParameter ?param . 
                  OPTIONAL {{
                    ?semanticPredicate ulkb:logicOperatorName ?operator .  
                   }}
                  ?param ulkb:varType ?type . 
                  ?param ulkb:varName ?value . 
                }} ORDER BY ?semanticPredicate
                  """

#If you want the more exact result, use   FILTER (?label = "{}")  instead of regex 
query_sem_predicates_str = """SELECT DISTINCT ?example ?roleList ?operator ?semanticPredicate ?semanticPredicateLabel ?param ?type ?vnVarName  WHERE {{
                  ?entity rdfs:label ?label . 
                  FILTER regex(?label, "{}", "i") . 
                  ?entity ulkb:hasComponent ?frame . 
                  ?frame ulkb:example ?example . 
                  OPTIONAL {{ ?frame ulkb:roleList ?roleList }} . 
                  ?frame ulkb:hasComponent ?semanticPredicate . 
                  ?semanticPredicate a ulkb:SemanticPredicate .
                  ?semanticPredicate rdfs:label ?semanticPredicateLabel. 
                  ?semanticPredicate ulkb:hasParameter ?param . 
                  OPTIONAL {{
                    ?semanticPredicate ulkb:logicOperatorName ?operator .  
                   }}
                  ?param ulkb:varType ?type . 
                  ?param ulkb:varName ?vnVarName .
                }} ORDER BY ?semanticPredicate
                  """

query_check_verb_name_str = """SELECT DISTINCT ?entity ?provenance  WHERE {{
  {{ ?entity a ulkb:Lemma }} UNION {{ ?entity a ulkb:LinguisticClass }} 
  ?entity rdfs:label ?name . 
  FILTER regex(?name, "{}", "i")
  ?entity ulkb:provenance ?provenance. 
}} ORDER BY ?mapping"""


query_pb_lemma_str = """SELECT DISTINCT ?propbankVerb ?lemma  WHERE {{
  ?propbankVerbNode rdfs:label ?propbankVerb . 
  ?propbankVerbNode ulkb:lemmaText ?lemma . 
   ?propbankVerbNode a ulkb:LinguisticClass . 
  ?propbankVerbNode ulkb:inKB ulkb:PropBank . 
  
  }} ORDER BY ?propbankVerb
"""

query_vn_lemma_str = """SELECT DISTINCT ?verbnetVerb ?lemma  WHERE {
  ?verbnetNode rdfs:label ?verbnetVerb . 
  ?verbnetNode ulkb:hasComponent ?lemmaNode . 
  ?lemmaNode ulkb:lemmaText ?lemma . 
  ?verbnetNode a ulkb:LinguisticClass . 
  ?verbnetNode ulkb:inKB ulkb:VerbNet . 
  
} ORDER BY ?verbnetVerb
"""

query_lemma_for_pbverb_str = """SELECT DISTINCT ?lemma ?argument  WHERE {{
  ?propbankVerbNode rdfs:label "{}" . 
  ?propbankVerbNode ulkb:lemmaText ?lemma . 
  ?propbankVerbNode a ulkb:LinguisticClass . 
  ?propbankVerbNode ulkb:inKB ulkb:PropBank . 
  ?propbankVerbNode ulkb:hasParameter ?param . 
  ?param rdfs:label ?argument . 
  }} ORDER BY ?propbankVerb
"""

query_lemma_for_vnverb_str = """SELECT DISTINCT ?verbnetNode ?verbnetVerb ?roleList WHERE {{
  ?verbnetNode rdfs:label ?verbnetVerb . 
  ?verbnetNode ulkb:hasComponent ?lemmaNode . 
  ?lemmaNode ulkb:lemmaText ?lemmaText . 
  FILTER regex(?lemmaText, "^{}$", "i")
  ?verbnetNode ulkb:hasComponent ?frame . 
  ?frame ulkb:roleList ?roleList . 
}} ORDER BY ?verbnetVerb
"""

query_args_for_vnverb_str = """SELECT DISTINCT ?vnVerbLabel ?arg WHERE {{ 
  ?vnVerb a ulkb:LinguisticClass . 
  ?vnVerb ulkb:inKB ulkb:VerbNet . 
  ?vnVerb rdfs:label "{}" . 
  ?vnVerb ulkb:hasComponent ?frame . 
  ?frame ulkb:hasComponent ?pred . 
  ?pred ulkb:hasParameter ?param . 
  ?param rdfs:label ?arg . 
  
  }} ORDER BY ?vnVerbLabel

"""

query_pb_roles_by_lemma_str = """SELECT DISTINCT ?verb ?pbSemRole ?pbSemRoleDesc ?vnVerbLabel ?vnVarType ?vnVarName WHERE {{
  ?verb a ulkb:LinguisticClass . 
  ?verb ulkb:inKB ulkb:PropBank . 
  ?verb ulkb:lemmaText "^{}$" .  
  
  ?verb ulkb:hasParameter ?pbParam .
  ?pbParam ulkb:description ?pbSemRoleDesc .  
  ?pbParam rdfs:label ?pbSemRole . 
  ?vnVerb ulkb:inKB ulkb:VerbNet . 
  ?vnVerb rdfs:label ?vnVerbLabel . 
  ?vnVerb ulkb:hasComponent ?vnFrame . 
  ?vnFrame ulkb:hasComponent ?semPred . 
  ?semPred ulkb:hasParameter ?vnParam . 
  ?pbParam ulkb:mapsTo ?vnParam . 
  ?vnParam ulkb:varType ?vnVarType . 
  ?vnParam ulkb:varName ?vnVarName . 
  }}"""
    
    
query_synonyms_str = """SELECT DISTINCT ?symLemma  WHERE {{
		?verb rdfs:label ?verbLabel . 
        filter(regex(?verbLabel, "^{}$", "i" )) . 
        ?verb ulkb:lemmaText ?symLemma . 
    }} ORDER BY ?symLemma
"""

query_version_str = """SELECT DISTINCT ?version 
    WHERE {
		ulkb:Base owl:versionInfo ?version . 
        }
"""

###############################################################################
# AUXILIARY FUNCTIONS
###############################################################################

#Iselects any matching pair
 
def one_mappingResult(_lemma: str, _roleset: str, _pbRoles: {}, _returnResults : {}) :
    
    #iterated through the results and see (1) which results are more common: 
        
    tempResults = []
    mostMatched = 0 
    bestResult = {}
    toDelete = []
    for pbVerb in _returnResults: 
        vnVerbDict = _returnResults[pbVerb]
        for vnVerb in vnVerbDict : 
            args = vnVerbDict[vnVerb]
            matched = 0 
            for role in _pbRoles : 
                if role in  args : 
                    matched +=1
                else : 
                   toDelete.append(role) 
            if matched > mostMatched : 
                mostMatched = matched
                bestResult = vnVerbDict
            else : 
                toDelete = []
    
    if len(bestResult) == 0 :
        return {"info": "NO semantic mappings for " + _roleset + ", or its lemma",
    _lemma: {}}
    
    #Let's make sure all the mappings are right. 
    for item in toDelete:  
        for vnVerb in bestResult : 
            args = vnVerbDict[vnVerb]
            args.pop(item, None)
            
    returnResults = {}
    returnResults[_roleset] = bestResult
    returnResults["info"] = "Map lemma " + _lemma + ", as " + _roleset
    returnResults["provenance"] = "Unified Mapping"
                    
    return returnResults                
 
# Order the predicates. 

def order_predicates(_predList : []) -> [] : 
    
    resultList = []
    for entry in _predList : 
        thisID = entry['id_predicate']
        thisOrderStr = thisID.split('_')[-1]
        thisOrder = int(thisOrderStr)
        if len(resultList) == 0 : 
            resultList.append(entry)
        else : 
            i = 0
            inserted = False
            while i < len(resultList):
                resultID = resultList[i]['id_predicate']
                resultOrderStr = resultID.split('_')[-1]
                resultOrder = int(resultOrderStr)
                if thisOrder < resultOrder  : 
                    resultList.insert(i, entry)
                    inserted = True
            if not inserted : 
                resultList.append(entry)

# Retrieves the equivalence classes for all entities.

def get_version() -> str : 
    query_text = query_version_str
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        version = result["version"]["value"]
        return version 
    return ""

def ulkb_analyze_coverage_text(_entries: {}, _output: str):
    max = -1
    counter = 0
    outDict = {}
    for entry in _entries:
        if "COVID-19 pandemic in" in entry:
            continue
        verbList = _entries[entry]
        for rawVerb in verbList:
            verb = stem_verb(rawVerb)
            counter += 1
            if len(verb) == 0:
                continue
            if verb in outDict:
                continue
            listItems = check_verb_name(verb)
            if len(listItems) > 0:
                outDict[verb] = "YES"
                print("process " + verb + ", YES")
            else:
                outDict[verb] = "NO"
                print("process " + verb + ", NO")
        if max > 0 and counter > max:
            break

    with open(_output, 'w') as f:
        for key, value in outDict.items():
            f.write('%s:%s\n' % (key, value))
        # if verbList in ourDict:
        #    continue

    f.close()


def link_to_terms_list(_list: []) -> []:
    resultList = []
    for link in _list:
        resultList.append(link.split['/'])


def check_verb_name(_name: str) -> {}:
    query_text = query_check_verb_name_str.format(_name)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    returnResults = {}
    for result in results["results"]["bindings"]:
        verb = result["entity"]["value"]
        provenance = result["provenance"]["value"]
        returnResults[verb] = provenance
    return returnResults


def stem_verb(_inputVerb: str) -> str:
    ps = PorterStemmer()
    return ps.stem(_inputVerb)



#####################################################################
# API  -- ulkb_pb_vn_mappings("enter.01")
# Usage : from a propbank verb, it gives the mappings for it.  
#         if _lemmaMatching is true, we match by lemma in the absence of 
#           a literal VerbNet match. 
#####################################################################
def ulkb_pb_vn_map_parameters(_pbName: str, _lemmaMatching = True) -> {}:
    returnResults = []
    query_text = query_roles_for_pb_str.format(_pbName)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    returnResults = {}
    # ?verb ?pbSemRole ?vnVerbLabel ?vnParamLabel
    verbResults = {}

    returnResults["info"] = "semantic roles for " + _pbName
    returnResults["provenance"] = "Unified Mapping"
    
    vnMapsFound = False
    
    pbTRoles = {}
    
    # ?verb ?pbSemRole ?pbSemRoleDesc ?vnVerbLabel ?vnVarType ?vnVarName
    
    for result in results["results"]["bindings"]:
        pbSemRole = result["pbSemRole"]["value"]
        pbSemRoleDesc = result["pbSemRoleDesc"]["value"]
        if pbSemRole not in pbTRoles : 
            pbTRoles[pbSemRole] = pbSemRoleDesc
        if "vnVerbLabel" in result :  
            vnVerbLabel = result["vnVerbLabel"]["value"]
            vnMapsFound = True
            vnVarType = result["vnVarType"]["value"]
            vnVarExpression = result["vnVarName"]["value"]
            if vnVerbLabel not in verbResults:
                verbResults[vnVerbLabel] = {}
            curVerb = verbResults[vnVerbLabel]
            if pbSemRole not in curVerb:
                curVerb[pbSemRole] = vnVarType + "(" + vnVarExpression + ")"
        # print(pbSemRole + "\t(" + vnVerbLabel + ", " + vnParamLabel + ")")

    if  _lemmaMatching and len(verbResults) == 0 :
        lemma = _pbName 
        if "." in _pbName: 
            lemma = _pbName.split(".", -1)[0]
        return ulkb_lemma_mappings(lemma, pbTRoles, _pbName)
    returnResults[_pbName] = verbResults
    return returnResults

#####################################################################
# API  -- ulkb_verb_synonyms("see.01")
# Usage: from a propbank (OR Verbnet) verb, get a list of synonyms
#####################################################################

def ulkb_verb_synonyms(_verb: str) -> {}:
    returnResults = []
    
    query_text = query_synonyms_str.format(_verb)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    returnResults = {}
    # pbVerb [?vnVerbLabel : pbVerbArg ?vnVarType ?vnVarExpression
    verbResults = []

    for result in results["results"]["bindings"]:
        symLemma = result["symLemma"]["value"]
        verbResults.append(symLemma)
        
        
    if len(verbResults) == 0 : 
        returnResults["info"] = "NO synonyms found for " + _verb
    else : 
        returnResults["info"] = "synonyms for " + _verb
        returnResults[_verb] = verbResults
    
    return returnResults
   
#####################################################################
# API  -- ulkb_sem_roles_for_pb_by_role("enter.01") to be deprecated
# Usage : from a propbank verb, it gives the semantic role mappings
#         for it and returns results after arranging by roles
#####################################################################
def ulkb_sem_roles_for_pb_by_role(_pbName: str) -> {}:
    query_text = query_roles_for_pb_str.format(_pbName)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # ?verb ?pbSemRole ?vnVerbLabel ?vnParamLabel
    verbResults = {}
    for result in results["results"]["bindings"]:
        pbSemRole = result["pbSemRole"]["value"]
        pbSemRoleDesc = result["pbSemRoleDesc"]["value"]
        vnVerbLabel = result["vnVerbLabel"]["value"]
        vnVarExpression = result["vnVarName"]["value"]
        if pbSemRole not in verbResults:
            verbResults[pbSemRole] = []
        verbResults[pbSemRole].append({
            "vncls": "-".join(vnVerbLabel.split("-")[1:]),
            "vntheta": vnVarExpression.lower(),
            "description": pbSemRoleDesc
        })
    return verbResults



#####################################################################
# API  -- ulkb_sem_predicates_SHORT("escape-51.1-2")
# Usage: from a VN verb, get a list of its semantic predicates. The 
#       predicate expressions are strings 
#####################################################################
def ulkb_sem_predicates_short(_verb: str) -> []:
    global query_prefix

    query_text = query_sem_predicates_str.format(_verb)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    output = []
    thisFrame = {}
    output.append(thisFrame)
    curPredicateID = ""
    thisPredicate = {}
    for result in results["results"]["bindings"]:
        example = result["example"]["value"]

        if 'example' not in thisFrame:
            thisFrame['example'] = example
            
        if 'roleList' in result and 'roleList' not in thisFrame:
            thisFrame['roleList'] = result['roleList']['value'].split(',')

        if example != thisFrame['example']:
            thisFrame = {}
            output.append(thisFrame)
            thisFrame['example'] = example
            curPredicateID = ""
        thisPredicateID = result["semanticPredicate"]["value"]

        if 'predicates' not in thisFrame:
            thisFrame['predicates'] = []
        predicates = thisFrame['predicates']
        
       
        if thisPredicateID != curPredicateID:
            thisPredicate = {}
            predicates.append(thisPredicate)
            curPredicateID = thisPredicateID

        # predicateText = result["predicateText"]["value"]
        predLabel = result["semanticPredicateLabel"]["value"]

        thisPredicate['label_predicate'] = predLabel
        if "operator" in result:
            thisPredicate['operator'] = result["operator"]["value"]

        if 'params' not in thisPredicate:
            thisPredicate['params'] = []
        params = thisPredicate['params']
        params.append(result["type"]["value"] + "(" + result["vnVarName"]["value"] + ")")
        # thisPredicate['type'] = result["type"]["value"]
        # thisPredicate['value'] = result["value"]["value"]
        # print(example + " " + " " +  thisPredicateID + " " +  predLabel + " " +
        #      result["type"]["value"] + " " + result["value"]["value"] )
    return output

#####################################################################
# API  -- ulkb_lemma_mappings("enter")
# Usage: from a lemma, get a list of mappings from pb to vn that 
#           correspond to that lemma
#####################################################################

def ulkb_lemma_mappings(_lemma: str, _pbRoles = [],  _roleset = "") -> {}:
    returnResults = []
    query_text = query_roles_for_lemma_str.format(_lemma)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    returnResults = {}
    # pbVerb [?vnVerbLabel : pbVerbArg ?vnVarType ?vnVarExpression
    verbResults = {}

    for result in results["results"]["bindings"]:
        pbSemRole = result["pbSemRole"]["value"]
        vnVerbLabel = result["vnVerbLabel"]["value"]
        pbVerbLabel = result["pbVerbLabel"]["value"]
        vnVarType = result["vnVarType"]["value"]
        vnVarName = result["vnVarName"]["value"]
        # The vnVerb
        if pbVerbLabel not in verbResults:
            verbResults[pbVerbLabel] = {}
        curpbVerb = verbResults[pbVerbLabel]
        
        if vnVerbLabel not in curpbVerb : 
            curpbVerb[vnVerbLabel] = {}
        curvnVerb = curpbVerb[vnVerbLabel]
            
        if pbSemRole not in curvnVerb:
            curvnVerb[pbSemRole] = vnVarType + "(" + vnVarName + ")"
        # print(pbSemRole + "\t(" + vnVerbLabel + ", " + vnParamLabel + ")")
    if len(_roleset) > 0 : 
        returnResults["info"] = "NO semantic mapping for " + _roleset + ", use lemma " + _lemma
    else : 
        returnResults["info"] = "semantic roles for lemma " + _lemma
    returnResults[_lemma] = verbResults
    
    if len(_pbRoles) > 0 : 
       return one_mappingResult(_lemma, _roleset, _pbRoles, verbResults) 
        
    return returnResults



#####################################################################
# API  -- ulkb_sem_predicates_for_lemma_SHORT("enter.01")
# Usage: from a Propbank roleset, get a list of relevant semantic predicates 
#        (from Verbnet). The predicate expressions are strings 
#####################################################################

def ulkb_sem_predicates_for_lemma_SHORT(_verb: str) -> []:
    global query_prefix

    query_text = query_sem_predicates_str.format(_verb)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    output = []
    thisFrame = {}
    output.append(thisFrame)
    curPredicateID = ""
    thisPredicate = {}
    for result in results["results"]["bindings"]:
        example = result["example"]["value"]

        if 'example' not in thisFrame:
            thisFrame['example'] = example
        if example != thisFrame['example']:
            thisFrame = {}
            output.append(thisFrame)
            thisFrame['example'] = example
            curPredicateID = ""
        thisPredicateID = result["semanticPredicate"]["value"]
        
        if 'roleList' in result and 'roleList' not in thisFrame:
            thisFrame['roleList'] = result['roleList']['value'].split(',')

        if 'predicates' not in thisFrame:
            thisFrame['predicates'] = []
        predicates = thisFrame['predicates']

        if thisPredicateID != curPredicateID:
            thisPredicate = {}
            predicates.append(thisPredicate)
            curPredicateID = thisPredicateID

        # predicateText = result["predicateText"]["value"]
        predLabel = result["semanticPredicateLabel"]["value"]

        thisPredicate['label_predicate'] = predLabel
        if "operator" in result:
            thisPredicate['operator'] = result["operator"]["value"]

        if 'params' not in thisPredicate:
            thisPredicate['params'] = []
        params = thisPredicate['params']
        params.append(result["type"]["value"] + "(" + result["expression"]["value"] + ")")
        # thisPredicate['type'] = result["type"]["value"]
        # thisPredicate['value'] = result["value"]["value"]
        # print(example + " " + " " +  thisPredicateID + " " +  predLabel + " " +
        #      result["type"]["value"] + " " + result["value"]["value"] )
    return output


############################################################
# API -- return the current version
############################################################
def ulkb_get_info() -> {}:
     
        info = {}
        info["ulkb service"] = ulkbServer
        info["ulkb version"] = get_version()
        return info
    

if __name__ == '__main__':
    
    #API call : test output of a non existent verb name
    #output = str(check_verb_name("NotAVerb"))
    #print(str(output))    

    # API call : From Probank to Verbnet: map the parameters
    output = ulkb_pb_vn_map_parameters("enter.01")
    print(str(output))

    # API call : obtain logical predicates associated to a Verbnet class
    output = ulkb_sem_predicates_short("escape-51.1-2")
    print(str(output))

