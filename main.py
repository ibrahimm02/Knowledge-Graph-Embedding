# This is a sample Python script.
from Ontology import Ontology
from rdflib import Graph
import os
from Alignment import Onto_Alignment
from Queries import Query
import numpy
import sys


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def s(se):
    se = [se]
    v = []
    for s in se:
        er = s.split(',')
        for a in er:
            v.append(a)
    return v


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    g = Graph()
    pizza_restaurant = 'cw_onto.ttl'
    ont = Ontology("cw_data.csv", g, pizza_restaurant, True)



    # ont.usingExternal()
    # ont.saveGraph('cw_onto_with_external_uris.ttl')

    ont.RDFSolution()
    #
    formatOWL = 'owl'
    formatTTL = 'ttl'
    cw_onto = 'cw_onto_without_reasoning.'
    # cw_onto_2 = 'cw_onto_without_reasoning.'
    cw_onto_r = 'cw_onto_with_reasoning.'
    # #
    ont.saveTTL(cw_onto + formatTTL)
    ont.saveOWL(cw_onto + formatOWL)
    #
    ont.performReasoning(cw_onto + formatTTL)  ##ttl format
    #
    ont.saveTTL(cw_onto_r + formatTTL)
    ont.saveOWL(cw_onto_r + formatOWL)
    #
    ont.performSPARQLQuery1('queries/query1-results.csv')
    ont.performSPARQLQuery2('queries/query2-results.csv')
    ont.performSPARQLQuery3('queries/query3-results.csv')
    ont.performSPARQLQuery4('queries/query4-results.csv')
    ont.performSPARQLQuery5('queries/query5-results.csv')
    #
    alignment = Onto_Alignment('pizza.owl', 'cw_onto.owl')
    alignment.task_alignment()
    alignment.saveGraph('ontology_alignment_task1.ttl')
    alignment.task_reasoning('cw_onto_with_reasoning.ttl', 'cw_onto.ttl', 'pizza.ttl', 'ontology_alignment_task1.ttl')
    alignment.saveGraph('ontology_alignment_task2.ttl')
    # #
    alignment.task_sparql('queries/alignment-query-result.csv')
