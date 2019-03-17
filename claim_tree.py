from time import time
from lxml import etree
import claims
import os
from parsing import *


def add_to_dict(claim_xml_element, patent_edge_dict, patent_info_dict):
    claim_number_string = claim_xml_element.get("num")
    patent_info_dict[claim_number_string]= claim_xml_element.text
    # get parents if any
    parent_claims_strings = []
    for p in claim_xml_element.iter("claim-ref"):
        parent_claim_num = p.get("idref")
        parent_claims_strings.append(parent_claim_num)
        if parent_claim_num in patent_edge_dict:
            patent_edge_dict[claim_number_string].add(parent_claim_num)
        else:
            patent_edge_dict[claim_number_string] = {parent_claim_num}

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
    return (patent_edge_dict, patent_info_dict)

class Graph(object):
    nodes_dict = {}
    children = {}

    class Node(object):
        def __init__(self, parents_set, depth, info, number):
            self.depth = depth
            self.parents = parents_set
            self.info = info
            nodes_dict[number] = self
            for parent in parents_set:
                if(parent in children):
                    children[parent].add(self)
                else
                    children[parent] = {self}

                if(parent in nodes_dict):
                    nodes_dict[parent].depth= max(nodes_dict.get[parent].depth, depth+1)
                else:
                    nodes_dict[parent] = Node(patent_edge_dict[parent], depth+1, patent_info_dict[parent], parent)

    def __init__(self, patent):
        self.patent_edge_dict, self.patent_info_dict = create_patent_dict(patent)
        for claim in self.patent_info_dict:
            if(claim not in nodes_dict):
                Node(self.patent_edge_dict[claim], 0, self.patent_info_dict[claim], claim)

    def isIndependent(self, number):
        assert(number in nodes_dict)
        return len(nodes_dict[number].parents_set)==0
    
    def num_claims(self):
        return len(nodes_dict)

    def find_ancestors(self, number):
        assert(number in nodes_dict)
        ancestors = []
        for parent in nodes_dict[number].parents:
            ancestors.append(parent)
            ancestors+= self.find_ancestors(parent)
        ancestors.sort(key = lambda node: nodes_dict[node].depth)
        return ancestors

    def find_independent_claims(self):
        nodes = [node for node in nodes_dict]
        independent_claims = filter(nodes, isIndependent)
        return independent_claims

    def num_independent_claims(self): 
        return len(self.find_independent_claims())

    def findLeaves(self):
        nodes = [node for node in nodes_dict]
        leaves = filter(nodes, lambda node: node.depth==0)
        return leaves

    def num_dependent_claims(self):
        return len(nodes_dict) - self.num_independent_claims()

    def find_children(self, number):
        assert(number in nodes_dict)
        if(number not in children):
            return set()
        return children[number]


    def find_connected_comp(self, number):
        connected_comps = set()
        assert(number in nodes_dict)
        undirected_edges = []
        for child in self.patent_edge_dict:
            parent = self.patent_edge_dict[edge]
            undirected_edges+= [(child, parent), (parent, child)]

        for leaf in self.findLeaves():
            visited = set()
            #if(leaf not in visited):
































