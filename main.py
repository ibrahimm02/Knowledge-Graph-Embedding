# This is a sample Python script.
from Ontology import Ontology
from rdflib import Graph
import numpy
import sys
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def s(se):

    se = [se]
    v = []
    for s in se:
        er = s.split((','))
        for a in er:
            v.append(a)
    return v


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    g = Graph()
    ont = Ontology("cw_data.csv", g)
    # ont.data_cleaning()
    # ont.another_attempt()


    ont.knowledge_graph()

    # OWL 2 RL reasoning
    # We will see reasoning next week. Not strictly necessary for this
    ont.performReasoning("cw_onto.ttl")  ##ttl format
    # solution.performReasoning("ontology_lab6.owl") ##owl (rdf/xml) format

    # Graph with ontology triples and entailed triples
    # ont.saveGraph(file.replace(".csv", "-" + task) + "-reasoning.ttl")

