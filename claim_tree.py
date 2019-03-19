from time import time
from lxml import etree
import claims
import os
from parsing import *
import collections


def add_to_dict(claim_xml_element, patent_edge_dict, patent_info_dict):
    claim_number_string = claim_xml_element.get("num")
    patent_info_dict[claim_number_string]= claim_xml_element.text
    # get parents if any
    if(claim_number_string not in patent_edge_dict):
        patent_edge_dict={}
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
    patent_info_dict = {}
    patentNum = getPatentNumber(patent)
    typeOfPatent = getTypeOfPatent(patent)
    filterInterestingTypesOfPatents(typeOfPatent)
    # dont want to process design orplant patents
    # Also note: design patents always have one vacuous claim (unnumbered)
    if is_utility_patent(typeOfPatent):
        for claimXML in patent.iter("claim"):
            claim = add_to_dict(claimXML, patent_edge_dict, patent_info_dict)

    print(patent_edge_dict)
    return (patent_edge_dict, patent_info_dict)

class ClaimSet(object):
    

    class Node(object):
        def __init__(patent, self, parents_set, depth, info, number):
            self.depth = depth
            self.parents = parents_set
            self.info = info
            self.number = number
            patent.nodes_dict[number] = self
            for parent in parents_set:
                if(parent in patent.children):
                    patent.children[parent].add(self)
                else:
                    patent.children[parent] = {self}

                if(parent in patent.nodes_dict):
                    patent.nodes_dict[parent].depth= max(patent.nodes_dict.get[parent].depth, depth+1)
                else:
                    patent.nodes_dict[parent] = Node(patent.patent_edge_dict[parent], depth+1, patent.patent_info_dict[parent], parent)

        def __hash__(self):
            return hash(self.number)

    def __init__(self, patent):
        self.patent_edge_dict, self.patent_info_dict = create_patent_dict(patent)
        self.nodes_dict = {}
        self.children = {}
        for claim in self.patent_info_dict:
            if(claim not in self.nodes_dict):
                self.Node(self.patent_edge_dict[claim], 0, self.patent_info_dict[claim], claim)
        
        def find_all_connected_comps():
            connected_comps = {}
            undirected_edges = {}
    
            for child in self.patent_edge_dict:
                parents = self.patent_edge_dict[edge]
                for parent in parents:
                    if child in undirected_edges:
                        undirected_edges[child].add(parent)
                    else:
                        undirected_edges[child] = {parent}
                    if parent in undirected_edges:
                        undirected_edges[parent].add(child)
                    else:
                        undirected_edges[parent] = {child}
    
            for leaf in self.find_leaves():
    
                seen, queue = set([leaf]), collections.deque([leaf])
                while queue:
                    vertex = queue.popleft()
                    for node in undirected_edges[vertex]:
                        if node not in seen:
                            seen.add(node)
                            queue.append(node)
                        connected_comps[leaf] = seen
    
                return connected_comps

        self.connected_comps = find_all_connected_comps()

    def is_independent(self, number):
        assert(number in self.nodes_dict)
        return len(self.nodes_dict[number].parents_set)==0

    def num_claims(self):
        return len(self.nodes_dict)

    def find_ancestors(self, number):
        assert(number in self.nodes_dict)
        ancestors = []
        for parent in self.nodes_dict[number].parents:
            ancestors.append(parent)
            ancestors+= self.find_ancestors(parent)
        ancestors.sort(key = lambda node: self.nodes_dict[node].depth)
        return ancestors

    def find_independent_claims(self):
        nodes = [node for node in self.nodes_dict]
        independent_claims = filter(isIndependent, nodes )
        return independent_claims

    def num_independent_claims(self):
        return len(self.find_independent_claims())

    def find_leaves(self):
        nodes = [node for node in self.nodes_dict]
        leaves = filter(lambda node: node.depth==0, nodes)
        return leaves

    def num_dependent_claims(self):
        return len(self.nodes_dict) - self.num_independent_claims()

    def find_children(self, number):
        assert(number in self.nodes_dict)
        if(number not in self.children):
            return set()
        return self.children[number]

    def get_connected_comp(self, number):
        for leaf in self.connected_comps:
            if number in self.connected_comps[leaf]:
                return self.connected_comps[leaf]


