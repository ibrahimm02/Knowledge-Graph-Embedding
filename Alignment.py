import owlrl
from owlready2 import *
from rdflib import Graph, BNode, URIRef, Literal, Namespace, OWL


class Onto_Alignment(object):
    def __init__(self, pizza_file, cw_file):

        self.pizza_file = pizza_file
        self.graph = Graph()
        self.cw_file = cw_file

        self.file1 = get_ontology(self.cw_file).load()
        self.file2 = get_ontology(self.pizza_file).load()

        self.pizza_res_uri = self.file1.get_base_iri()
        self.pizza_uri = self.file2.get_base_iri()

        res = Namespace(self.pizza_res_uri)
        pizza = Namespace(self.pizza_uri)

        self.graph.bind("res", res)
        self.graph.bind("pizza", pizza)

        self.ontologies = (self.file1, self.file2)

    def get_Classes(self, onto):
        onto_1, onto_2 = onto
        onto = (list(onto_1.classes()), list(onto_2.classes()))
        return onto

    # def get_Classes(self, onto):
    #     return onto.classes()

    def get_DataProperties(self, onto):
        onto_1, onto_2 = onto
        onto = (list(onto_1.data_properties()), list(onto_2.data_properties()))
        return onto

    def get_ObjectProperties(self, onto):
        onto_1, onto_2 = onto
        onto = (list(onto_1.object_properties()), list(onto_2.object_properties()))
        return onto

    def get_Individuals(self, onto):
        onto_1, onto_2 = onto
        onto = (list(onto_1.individuals()), list(onto_2.individuals()))
        return onto

    def get_RDFSLabelsForEntity(self, entity):
        return entity.label

    def task_alignment(self):

        print('Alignment Task:')

        dem_classes = self.get_Classes(self.ontologies)
        dem_object = self.get_ObjectProperties(self.ontologies)
        dem_data = self.get_DataProperties(self.ontologies)
        dem_individuals = self.get_Individuals(self.ontologies)
        self.for_looper(dem_classes)
        self.for_looper(dem_object)
        self.for_looper(dem_data)
        self.for_looper(dem_individuals)

        # self.graph.serialize('ontology_alignment_task1.ttl', format='ttl')

        # for file1_class in self.get_Classes(self.file1):
        #     for file2_class in self.get_Classes(self.file2):
        #
        #         if file1_class.name in file2_class.name:
        #             print('FOUND MATCHING TRIPLE {} AND {}'.format(file1_class, file2_class))
        #             # subject = URIRef(self.pizza_uri + file1_class)
        #             # obj = URIRef(self.pizza_res_uri + file2_class)
        #             # self.graph.add((subject, OWL.equivalentClass, obj))
        #             #

    def for_looper(self, entity_type):
        it1, it2 = entity_type
        for first_file in it1:
            # print('First For {}'.format(first_file) + '\n')
            for second_file in it2:
                # print('Second For {}'.format(second_file) + '\n')
                if first_file.name == second_file.name:
                    print('FOUND MATCHING TRIPLE {} AND {}'.format(first_file, second_file))
                    subject = URIRef(self.pizza_uri + str(first_file))
                    obj = URIRef(self.pizza_res_uri + str(second_file))
                    self.graph.add((subject, OWL.equivalentClass, obj))

    def task_reasoning(self, generatedOntoFile, cwOntoFile, pizzaFile, ontoAlignmentFile):

        self.graph.parse(generatedOntoFile, format='ttl')
        self.graph.parse(cwOntoFile, format='ttl')
        self.graph.parse(pizzaFile, format='ttl')
        self.graph.parse(ontoAlignmentFile, format='ttl')

        self.graph.serialize('ontology_alignment_task2.ttl', format='ttl')

        print("Triples before reasoning: {}".format(len(self.graph)))

        # RDFS reasoning using owlrl semantics:
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics, axiomatic_triples=True, datatype_axioms=False).expand(self.graph)

        print("Triples after reasoning: {}".format(len(self.graph)))

    def task_sparql(self, file_query_out):

        qres = self.graph.query(
            """
            
                SELECT DISTINCT ?Pizza
                WHERE {
                ?Pizza rdf:type pizza:MeatyPizza .
                } 
            """
        )

        print("QUERY - pizzas with ontology type pizza:MeatyPizza : %s" % (str(len(qres))))

        f_out = open(file_query_out, "w+")

        for row in qres:
            # Row is a list of matched RDF terms: URIs, literals or blank nodes
            line_str = '\"%s\"\n' % row.pizza

            f_out.write(line_str)

        f_out.close()

    def saveGraph(self, filename):

        # print(self.graph.serialize(format="turtle"))
        self.graph.serialize(destination=filename, format='ttl')
