from time import time
from lxml import etree
import claims
import os
from parsing import *

def add_to_dict(claim_xml_element, patent_edge_dict):
    claim_number_string = claim_xml_element.get("num")
    patent_edge_dict[claim_number_string] = patent_edge_dict.get(claim_number_string,set())

    # get parents if any
    parent_claims_strings = []
    for p in claim_xml_element.iter("claim-ref"):
        parent_claim_text = p.get("idref")
        parent_claims_strings.append(parent_claim_text)
        if parent_claim_text in patent_edge_dict:
            patent_edge_dict[parent_claim_text].add(claim_number_string)
        else:
            patent_edge_dict[parent_claim_text] = {claim_number_string}

def create_patent_dict(patent):
    patent_edge_dict = {}
    patentNum = getPatentNumber(patent)
    typeOfPatent = getTypeOfPatent(patent)
    filterInterestingTypesOfPatents(typeOfPatent)
    # dont want to process design orplant patents
    # Also note: design patents always have one vacuous claim (unnumbered)
    if is_utility_patent(typeOfPatent):
        for claimXML in patent.iter("claim"):
            claim = add_to_dict(claimXML, patent_edge_dict)
    print(patent_edge_dict)
    return patent_edge_dict













