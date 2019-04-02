from time import time
from lxml import etree
import claims
import os
from parsing import *
import collections

'''
add_to_dict(claim_xml_element, patent_edge_dict, patent_info_dict) :
Takes in a claim, the edge dictionary, and the info dictionary, and updates 
the dictionary with this claim. 
claim_xml_element: a claim in the patent
patent_edge_dict: dictionary with child claims (keys) and set of parent claims (values)
patent_info_dict: dictionary with all claims (keys) and their info text (values)
''' 
def add_to_dict(claim_xml_element, patent_edge_dict, patent_info_dict):
    claim_number_string = claim_xml_element.get("num")
    claimtext2 = ""
    for el in claim_xml_element.iter():
        claimtext2 += '\n'
        # print('Element:', el, ' tag=', el.tag, ', num children=', len(list(el)))
        if el.text != None:
            element_text = el.text
            claimtext2 += element_text
    
        if el.tail != None:
            element_text = el.tail
            # if element_text != '\n':
            if len(element_text.strip()) > 0:
                # assert len(element_text) > 0, "element_text of claim is empty"
                element_text = element_text.strip()
                claimtext2 += element_text
                
    patent_info_dict[claim_number_string]= claimtext2
    # get parents if any
    if(claim_number_string not in patent_edge_dict):
        patent_edge_dict[claim_number_string]={}
    parent_claims_strings = []
    count = 0
    for p in claim_xml_element.iter("claim-ref"):
        count+=1
        parent_claim_num = p.get("idref")
        parent_claims_strings.append(parent_claim_num)
        if parent_claim_num in patent_edge_dict.get(claim_number_string, {}):
            patent_edge_dict[claim_number_string].add(parent_claim_num[4:])
        else:
            patent_edge_dict[claim_number_string] = {parent_claim_num[4:]}



'''
create_patent_dict(patent):
Takes in a patent and creates the patent edge dictionary and the info dictionary
Output:
patent_edge_dict: dictionary with child claims (keys) and set of parent claims (values)
patent_info_dict: dictionary with all claims (keys) and their info text (values)
''' 
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
            add_to_dict(claimXML, patent_edge_dict, patent_info_dict)
    else: print("is design patent\n")
    return (patent_edge_dict, patent_info_dict)


'''
Node class: represents one claim in the claim graph of a patent.
Has the claim along with a set of its parents, its info, etc
Won't really be used outside of the ClaimSet class
'''
class Node(object):
    def __init__(self, patent, parents_set, depth, info, number):
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
                patent.nodes_dict[parent].depth= max(patent.nodes_dict[parent].depth, depth+1)
            else:
                patent.nodes_dict[parent] = Node(patent, patent.patent_edge_dict[parent], depth+1, patent.patent_info_dict[parent], parent)

    def __hash__(self):
        return hash(self.number)

'''
ClaimSet class: represents the claim graph for a given patent.
Creating a ClaimSet object for a patent causes it to create the entire graph of the patent
'''
class ClaimSet(object):

    def __init__(self, patent):
    	#patent_edge_dict maps children to a set of parents
    	#patent_info_dict maps claims to their info text
        self.patent_edge_dict, self.patent_info_dict = create_patent_dict(patent)
        #nodes_dict maps each claim ID to the Node object for that claim
        self.nodes_dict = {}
        self.children = {}
        for claim in self.patent_info_dict:
            if(claim not in self.nodes_dict):
                Node(self, self.patent_edge_dict.get(claim, set()), 0, self.patent_info_dict[claim], claim)
        print(self.patent_info_dict)


        '''
		connected_comps is a dictionary with the leaves as keys and the entire 
		connected component of each leaf as the value (implemented DFS, basically)
        '''
        def find_all_connected_comps():
            connected_comps = {}
            undirected_edges = {}

            for child in self.patent_edge_dict:
                parents = self.patent_edge_dict[child]
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
                    for node in undirected_edges.get(vertex, {}):
                        if node not in seen:
                            seen.add(node)
                            queue.append(node)
                        connected_comps[leaf] = seen
                return connected_comps

        self.connected_comps = find_all_connected_comps()

    #true if a claim has no parents (ie: the claim refers to no other claim), else false
    def is_independent(self, number):
        assert(number in self.nodes_dict)
        return len(self.nodes_dict[number].parents_set)==0

	#number of claims in the patent
    def num_claims(self):
        return len(self.nodes_dict)

    #creates a list of ancestors (in order from direct parent to root) for the given claim
    def find_ancestors(self, number):
        assert(number in self.nodes_dict)
        ancestors = []
        for parent in self.nodes_dict[number].parents:
            ancestors.append(parent)
            ancestors+= self.find_ancestors(parent)
        ancestors.sort(key = lambda node: self.nodes_dict[node].depth)
        return ancestors

    #gives a list of independent claims in the patent
    def find_independent_claims(self):
        nodes = [node for node in self.nodes_dict]
        independent_claims = filter(isIndependent, nodes )
        return independent_claims

    #number of independent claims in the patent
    def num_independent_claims(self):
        return len(self.find_independent_claims())

    #finds the leaves (ie, claims that are not parents for any other claim)
    def find_leaves(self):
        nodes = [node for node in self.nodes_dict]
        leaves = filter(lambda node: self.nodes_dict[node].depth==0, nodes)
        return leaves

    #number of dependent claims in the patent 
    def num_dependent_claims(self):
        return len(self.nodes_dict) - self.num_independent_claims()

    #finds the set t=of claims that are directly dependent on the given claim
    def find_children(self, number):
        assert(number in self.nodes_dict)
        if(number not in self.children):
            return set()
        return self.children[number]

    #get the connected component (set of claim IDs) of the given claim
    def get_connected_comp(self, number):
        for leaf in self.connected_comps:
            if number in self.connected_comps[leaf]:
                return self.connected_comps[leaf]
