from rdflib import OWL, RDF, URIRef, Literal, Namespace, Graph, BNode
from rdflib.namespace import FOAF, DCTERMS, XSD, RDF, SDO, OWL, RDFS
from rdflib.util import guess_format

from lookup import DBpediaLookup, WikidataAPI, GoogleKGLookup
from stringcmp import isub
import pandas as pd
import csv
import re
import numpy
import owlrl


class Ontology(object):
    def __init__(self, file, graph):
        self.file = file;
        self.graph = graph

        # Namespace to create URIRefs
        self.cw_ns_str = 'http://www.semanticweb.org/in3067-inm713/restaurants#'
        # Special namespaces class to create directly URIRefs in python.
        self.cw = Namespace(self.cw_ns_str)
        # Prefix for the serialization
        self.graph.bind("cw", self.cw)  # cw is a newly created namespace

        # Enable DBPedia lookups
        self.dbpedia = DBpediaLookup()

    def dframed(self):
        df = pd.read_csv(self.file)
        df = pd.DataFrame(df)
        return df

    def ingr_split(self, ingredients):
        new_ingredients = []
        for i in [ingredients]:
            i = str(i)
            temp = ''
            i = i.replace('and', ',')
            i = i.replace('with', ',')
            i = i.replace('or', ',')
            i = i.replace('any', ',')
            if ',' in i:
                temp = ','
            if (temp != ''):
                t = i.split(temp)

                for e in t:
                    if e == ' ' or e == '':
                        continue
                    e = e.replace(' ', '')
                    new_ingredients.append(e)
            else:

                if i == 'nan':
                    i = ''
                new_ingredients.append(i)
        return new_ingredients

    def preprocessing(self):
        temp = self.dframed()
        print(temp.shape)
        extra = []
        for a in range(temp.shape[0]):
            # print('------------------------------')
            for b in temp.columns:

                if b == 'item description':
                    splt_ing = self.ingr_split(str(temp.iloc[a][b]))

                else:
                    splt_ing = str(temp.iloc[a][b])

                temp2 = splt_ing
                # print(temp2)
                if temp2 == 'nan':
                    temp2 = ''

                # temp2 = re.sub(r'[^\w]', '', temp2)

                if ',' in temp2:
                    temp2 = temp2.split(',')
                if b == 'categories':
                    for cat in range(len(temp2)):
                        if 'and' in temp2[cat]:
                            temp2[cat] = temp2[cat].replace('and', '')

                extra.append(temp2)

        extra = numpy.array(extra)
        extra = extra.reshape((501, 11))
        # extra = extra.flatten()

        return extra

    def type_triple(self, subject, object):
        subject = str(subject)
        sbj = re.sub(r'[^\w]', '', subject)
        self.graph.add((URIRef(self.cw + sbj), RDF.type, object))

    def literal_triple(self, subject, object, predicate, datatype):
        object = str(object)
        sbj = re.sub(r'[^\w]', '', subject)
        lit = Literal(object, datatype=datatype)
        self.graph.add((URIRef(self.cw + sbj), predicate, lit))

    def object_triple(self, subject, predicate, object):
        subject = str(subject)
        object = str(object)
        subject = re.sub(r'[^\w]', '', subject)
        object = re.sub(r'[^\w]', '', object)
        self.graph.add((URIRef(self.cw + subject), predicate, URIRef(self.cw + object)))

    # def location_triple(self, subject, object):
    #     subject = str(subject)
    #     object = str(object)
    #     subject = re.sub(r'[^\w]', '', subject)
    #     object = re.sub(r'[^\w]', '', object)
    # self.graph.add((URIRef(self.cw + subject), self.cw.Location, URIRef(self.cw + object)))

    def knowledge_graph(self):
        lst = self.preprocessing()

        # URIs FOR DIFFERENT PIZZAS WITH SAME NAME

        for a in lst:

            # TYPES --> subject, type, object
            self.type_triple(a[0], self.cw.restaurantName)
            self.type_triple(a[1], self.cw.Address)
            self.type_triple(a[2], self.cw.City)  # add DBpedia
            self.type_triple(a[3], self.cw.Country)  # add DBpedia
            self.type_triple(a[4], self.cw.PostCode)
            self.type_triple(a[5], self.cw.State)  # add DBpedia
            # category
            for r in a[6]:
                self.type_triple(r, self.cw.Category)  # --> Category
            self.type_triple(a[7], self.cw.MenuItem)
            self.type_triple(a[8], self.cw.ItemValue)
            self.type_triple(a[9], self.cw.Currency)
            # ingredients
            for r in a[10]:
                self.type_triple(r, self.cw.Ingredient)  # REMOVE BRACKETS in triples

            # ----------------------------------------------------------------------------------------------------------

            # lITERALS --> subject, object, predicate, datatype
            self.literal_triple(a[0], a[0], self.cw.restaurantName, 'string')
            self.literal_triple(a[1], a[1], self.cw.Address, 'string')
            self.literal_triple(a[2], a[2], self.cw.City, 'string')
            self.literal_triple(a[3], a[3], self.cw.Country, 'string')
            self.literal_triple(a[4], a[4], self.cw.PostCode, 'string')
            self.literal_triple(a[5], a[5], self.cw.State, 'string')

            for r in a[6]:
                self.literal_triple(r, r, self.cw.Category, 'string')  # --> Category

            # self.literal_triple(a[7], a[7], self.cw.MenuItem, 'string')    #check again
            self.literal_triple(a[8], a[8], self.cw.ItemValue, 'double')
            self.literal_triple(a[9], a[9], self.cw.Currency, 'string')
            for r in a[10]:
                self.literal_triple(r, r, self.cw.Ingredient, 'string')

            # ----------------------------------------------------------------------------------------------------------

            # OBJECTS --> subject, predicate, object
            self.object_triple(a[0], self.cw.IsLocatedIn, a[1])

            category = a[6] if isinstance(a[6], list) else [a[6]]
            for cat in category:
                self.object_triple(a[0], self.cw.Category, cat)

            self.object_triple(a[9], self.cw.isCurrencyOf, a[3])

            self.object_triple(a[1], self.cw.hasPostCode, a[4])

            # amountCurrency
            self.object_triple(a[8], self.cw.amountCurrency, a[9])

            # hasIngredient
            ingredient = a[10] if isinstance(a[10], list) else [a[10]]
            for ingre in ingredient:
                self.object_triple(a[7], self.cw.hasIngredient, ingre)

            # hasLocation
            # hasAdress
            self.object_triple(a[2], self.cw.hasAdress, a[1])
            # hasCity
            self.object_triple(a[5], self.cw.hasCity, a[2])
            # hasState
            self.object_triple(a[3], self.cw.hasState, a[5])

            # hasValue
            self.object_triple(a[7], self.cw.hasValue, a[8])

            # isIngredientOf
            ingredient = a[10] if isinstance(a[10], list) else [a[10]]
            for ingre in ingredient:
                self.object_triple(ingre, self.cw.isIngredientOf, a[7])

            # locatedIn
            # locatedInAdress
            self.object_triple(a[0], self.cw.locatedInAdress, a[1])
            # locatedInCity
            self.object_triple(a[1], self.cw.locatedInCity, a[2])
            # locatedInCountry
            self.object_triple(a[5], self.cw.locatedInCountry, a[3])
            # locatedInState
            self.object_triple(a[2], self.cw.locatedInstate, a[5])

            # servedIn
            # servedInRestaurant
            self.object_triple(a[7], self.cw.servedInRestaurant, a[0])

            # serves
            # servesMenuItem
            self.object_triple(a[0], self.cw.servesMenuItem, a[7])

            # ----------------------------------------------------------------------------------------------------------

            # DATA PROPERTIES
            # amount
            # firstLineAddress
            # itemName
            # name
            # postCode
            # restaurantName

            # ----------------------------------------------------------------------------------------------------------

            # # a[1], predicate, subject
            # #g.add(URIREF(  URI + clean(a[0]), Literal(a[0], XSD.String))
            # for b in a[11]:
            #     # g.add(URIREF(  URI + clean(b), Rdf.type, cw_URI.Ingredient)
            #     # g.add(URIREF(  URI + clean(b), Rdf.type, cw_URI.Ingredient)

        # print("Data triples from CSV: '" + str(len(self.graph)) + "'.")

        print(self.graph.serialize(format="turtle"))

    def performReasoning(self, ontology_file):

        # We expand the graph with the inferred triples
        # We use owlrl library with OWL2 RL Semantics (instead of RDFS semantic as we saw in lab 4)
        # More about OWL 2 RL Semantics in lecture/lab 7

        print("Data triples from CSV: '" + str(len(self.graph)) + "'.")

        # We should load the ontology first
        # print(guess_format(ontology_file))
        self.graph.load(ontology_file, format=guess_format(ontology_file))  # e.g., format=ttl

        print("Triples including ontology: '" + str(len(self.graph)) + "'.")

        # We apply reasoning and expand the graph with new triples
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics, axiomatic_triples=False, datatype_axioms=False).expand(self.graph)

        print("Triples after OWL 2 RL reasoning: '" + str(len(self.graph)) + "'.")
