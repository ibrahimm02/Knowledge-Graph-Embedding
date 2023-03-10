from rdflib import OWL, RDF, URIRef, Literal, Namespace, Graph, BNode
from rdflib.namespace import FOAF, DCTERMS, XSD, RDF, SDO, OWL, RDFS
from rdflib.util import guess_format

from lookup import DBpediaLookup, WikidataAPI, GoogleKGLookup
from isub import isub
import pandas as pd
import csv
import re
import numpy
import owlrl


class Ontology(object):
    def __init__(self, file, graph, pizza_restaurant, is_external):
        self.file = file

        self.stringToURI = dict()

        self.graph = graph
        self.graph.parse(pizza_restaurant)
        self.is_external = is_external
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

        numpy.warnings.filterwarnings('ignore', category=numpy.VisibleDeprecationWarning)
        extra = numpy.array(extra)
        extra = extra.reshape((501, 11))
        # extra = extra.flatten()

        return extra

    def create_property(self, subject, object):

        self.graph.add((URIRef(subject), RDF.type, object))

    def createURIForEntity(self, name, useExternalURI):

        # We create fresh URI (default option)
        self.stringToURI[name] = self.cw_ns_str + name.replace(" ", "_")

        if useExternalURI:  # We connect to online KG
            uri = self.getExternalKGURI(name)
            if uri != "":
                self.stringToURI[name] = uri

        return self.stringToURI[name]

    def getExternalKGURI(self, name):
        '''
        Approximate solution: We get the entity with highest lexical similarity
        The use of context may be necessary in some cases
        '''

        entities = self.dbpedia.getKGEntities(name, 5)
        # print("Entities from DBPedia:")
        current_sim = -1
        current_uri = ''
        for ent in entities:
            isub_score = isub(name, ent.label)
            if current_sim < isub_score:
                current_uri = ent.ident
                current_sim = isub_score

            # print(current_uri)
        return current_uri

    def type_triple(self, subject, class_type, useExternalURI):
        subject = str(subject)
        sbj = re.sub(r'[^\w]', '', subject)
        sbj_uri = self.cw + sbj

        sbj_uri = self.createURIForEntity(sbj.lower(), useExternalURI)
        self.graph.add((URIRef(sbj_uri), RDF.type, class_type))

        # self.graph.add((URIRef(sbj_uri), RDF.type, object))
        # self.create_property(object, OWL.Class)

    def literal_triple(self, subject, object, predicate, datatype):
        subject = str(subject)
        object = str(object)
        sbj = re.sub(r'[^\w]', '', subject)
        sbj_uri = self.cw + sbj
        lit = Literal(object, datatype=datatype)

        self.graph.add((URIRef(sbj_uri), predicate, lit))

    def object_triple(self, subject, predicate, object):
        subject = str(subject)
        object = str(object)
        subject = re.sub(r'[^\w]', '', subject)
        object = re.sub(r'[^\w]', '', object)

        sbj_uri = self.cw + subject
        obj_uri = self.cw + object

        self.graph.add((URIRef(sbj_uri), predicate, URIRef(obj_uri)))
        self.create_property(predicate, OWL.ObjectProperty)

    # def location_triple(self, subject, object):
    #     subject = str(subject)
    #     object = str(object)
    #     subject = re.sub(r'[^\w]', '', subject)
    #     object = re.sub(r'[^\w]', '', object)
    # self.graph.add((URIRef(self.cw + subject), self.cw.Location, URIRef(self.cw + object)))

    def RDFSolution(self):
        self.knowledge_graph(False)

    def usingExternal(self):
        self.knowledge_graph(True)

    def knowledge_graph(self, useExternalURI):
        lst = self.preprocessing()
        # URIs FOR DIFFERENT PIZZAS WITH SAME NAME

        for i, a in enumerate(lst):

            id = str(i)

            # restaurant_name = aprtin[0] + i
            pizza_item = a[7]
            restaurants = a[6]
            price = a[8]  # for literals only
            if price == '':
                price = '0'
            # price = float(price)

            if type(pizza_item) == list:
                blank_string = ''
                for iter_pizza in pizza_item:
                    blank_string = blank_string + iter_pizza
                pizza_item = blank_string
            pizza_item = pizza_item + '_' + id

            if type(restaurants) == str:
                restaurants = [restaurants]
            # category filter used for dbpedia
            filter_city = 'http://dbpedia.org/resource/Category:Cities_in_the_United_States'
            filter_States = 'http://dbpedia.org/resource/Category:States_of_the_United_States'

            # TYPES --> subject, type, object
            # LITERALS --> subject, object, predicate, datatype

            # restaurantName
            # self.type_triple(a[0], self.cw.restaurantName)
            self.literal_triple(a[0], a[0], self.cw.restaurantName, XSD.string)

            # Address
            self.type_triple(a[1], self.cw.Address, None)
            self.literal_triple(a[1], a[1], self.cw.Address, XSD.string)

            # City
            self.type_triple(a[2], self.cw.City, useExternalURI)  # add DBpedia
            self.literal_triple(a[2], a[2], self.cw.City, XSD.string)

            # Country
            self.type_triple(a[3], self.cw.Country, useExternalURI)  # add DBpedia
            self.literal_triple(a[3], a[3], self.cw.Country, XSD.string)

            # postCode
            # self.type_triple(a[4], self.cw.postCode)
            self.literal_triple(a[4], a[4], self.cw.postCode, XSD.string)

            # State
            self.type_triple(a[5], self.cw.State, useExternalURI)  # add DBpedia
            self.literal_triple(a[5], a[5], self.cw.State, XSD.string)

            # Restaurant category
            for r in restaurants:
                self.type_triple(r, self.cw.Restaurant, None)  # --> Category
            for r in restaurants:
                self.literal_triple(r, r, self.cw.Restaurant, XSD.string)  # --> Category

            # MenuItem
            self.type_triple(pizza_item, self.cw.MenuItem, None)
            self.literal_triple(pizza_item, pizza_item, self.cw.pizzaName, XSD.string)  # check again

            # ItemValue
            self.type_triple(price, self.cw.ItemValue, None)
            self.literal_triple(price, price, self.cw.amount, XSD.double)

            # Currency
            self.type_triple(a[9], self.cw.Currency, None)
            self.literal_triple(a[9], a[9], self.cw.Currency, XSD.string)

            # Ingredients
            for r in a[10]:
                self.type_triple(r, self.cw.Ingredient, None)  # REMOVE BRACKETS in triples
            for r in a[10]:
                self.literal_triple(r, r, self.cw.Ingredient, XSD.string)

            # ----------------------------------------------------------------------------------------------------------

            # OBJECTS --> subject, predicate, object
            self.object_triple(a[0], self.cw.IsLocatedIn, a[1])
            restaurant = a[6] if isinstance(a[6], list) else [a[6]]
            for rest in restaurant:
                self.object_triple(a[0], self.cw.hasRestaurant, rest)

            self.object_triple(a[9], self.cw.isCurrencyOf, a[3])
            self.object_triple(a[1], self.cw.hasPostCode, a[4])

            # amountCurrency
            self.object_triple(price, self.cw.amountCurrency, a[9])

            # hasIngredient
            ingredient = a[10] if isinstance(a[10], list) else [a[10]]
            for ingre in ingredient:
                self.object_triple(pizza_item, self.cw.hasIngredient, ingre)

            # hasLocation
            # hasAdress
            self.object_triple(a[2], self.cw.hasAdress, a[1])
            # hasCity
            self.object_triple(a[5], self.cw.hasCity, a[2])
            # hasState
            self.object_triple(a[3], self.cw.hasState, a[5])

            # hasValue
            self.object_triple(pizza_item, self.cw.hasValue, price)

            # isIngredientOf
            ingredient = a[10] if isinstance(a[10], list) else [a[10]]
            for ingre in ingredient:
                self.object_triple(ingre, self.cw.isIngredientOf, pizza_item)

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
            self.object_triple(pizza_item, self.cw.servedInRestaurant, a[0])

            # serves
            # servesMenuItem
            self.object_triple(a[0], self.cw.servesMenuItem, pizza_item)

            # ----------------------------------------------------------------------------------------------------------
            #
            # # DATA PROPERTIES
            # # amount
            # self.create_property(self.cw.amount, OWL.DatatypeProperty)
            #
            # # firstLineAddress
            # self.create_property(self.cw.firstLineAddress, OWL.DatatypeProperty)
            #
            # # itemName
            # self.create_property(self.cw.itemName, OWL.DatatypeProperty)
            #
            # # name
            # self.create_property(self.cw.name, OWL.DatatypeProperty)
            #
            # # postCode
            # self.create_property(self.cw.postCode, OWL.DatatypeProperty)
            #
            # # restaurantName
            # self.create_property(self.cw.restaurantName, OWL.DatatypeProperty)

            # ----------------------------------------------------------------------------------------------------------

        # print("Data triples from CSV: '" + str(len(self.graph)) + "'.")
        # print(self.graph.serialize(format="turtle"))

    def saveGraph(self, filename):
        self.graph.serialize(destination=filename, format='ttl')

    def saveOWL(self, filename):
        self.graph.serialize(destination=filename, format='xml')

    def saveTTL(self, filename):
        self.graph.serialize(destination=filename, format='ttl')

    def performReasoning(self, ontology_file):

        # We expand the graph with the inferred triples
        # We use owlrl library with OWL2 RL Semantics (instead of RDFS semantic as we saw in lab 4)
        # More about OWL 2 RL Semantics in lecture/lab 7

        print("Data triples from CSV: '" + str(len(self.graph)) + "'.")

        # We should load the ontology first
        # print(guess_format(ontology_file))
        self.graph.parse(ontology_file, format=guess_format(ontology_file))  # e.g., format=ttl

        print("Triples including ontology: '" + str(len(self.graph)) + "'.")

        # We apply reasoning and expand the graph with new triples
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics, axiomatic_triples=False, datatype_axioms=False).expand(self.graph)

        print("Triples after OWL 2 RL reasoning: '" + str(len(self.graph)) + "'.")

    def performSPARQLQuery1(self, file_query_out):
        qres = self.graph.query(
            """PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
                SELECT DISTINCT ?restaurantName ?Address ?City
                WHERE {
                    ?restaurantName cw:locatedInAdress ?Address.
                    ?Address cw:locatedInCity ?City.
                    ?restaurantName cw:servesMenuItem ?pizzaItem.
                    ?pizzaItem cw:pizzaName ?pizza_name.
                    ?pizzaItem cw:hasIngredient ?ingre.
                    ?ingre cw:Ingredient ?ingredient.
                    FILTER NOT EXISTS
                    {
                        FILTER(regex(?pizza_name, 'tomat', 'i') || regex(?ingredient, 'tomat', 'i'))
                    }
                } GROUP BY ?restaurantName ?Address ?City"""
        )

        print("QUERY1 - Restaurant that sell pizzas without tomato : %s" % (str(len(qres))))

        f_out = open(file_query_out, "w+")

        for row in qres:
            # Row is a list of matched RDF terms: URIs, literals or blank nodes
            line_str = '\"%s\",\"%s\",\"%s\"\n' % (row.restaurantName, row.Address, row.City)

            f_out.write(line_str)

        f_out.close()

    def performSPARQLQuery2(self, file_query_out):

        qres = self.graph.query(
            """PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
            SELECT (AVG(?amount) AS ?average)
            WHERE {
                ?pizza cw:pizzaName ?pname .
                ?pizza cw:hasValue ?value .
                ?value cw:amount ?amount .
            FILTER regex(?pname, 'marg', 'i')
            }"""
        )

        print("QUERY2 - Average price of Margherita Pizza : %s" % (str(len(qres))))

        f_out = open(file_query_out, "w+")

        for row in qres:
            # Row is a list of matched RDF terms: URIs, literals or blank nodes
            line_str = '\"%s\"\n' % (row.average)

            f_out.write(line_str)

        f_out.close()

    def performSPARQLQuery3(self, file_query_out):

        qres = self.graph.query(
            """PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
            SELECT (COUNT(DISTINCT ?rname) AS ?cnt) ?city 
            WHERE {
                ?rname cw:locatedInAdress ?add .
                ?add cw:locatedInCity ?city .
                ?city cw:locatedInstate ?state .
            }
            GROUP BY ?city
            HAVING ((?cnt) >= 6)
            ORDER BY ASC(?state) ASC(?cnt)"""
        )

        print("QUERY3 - Cities with more than 6 restaurants : %s" % (str(len(qres))))
        print("OUTPUT SHOULD BE (cnt - 6) (city - NewYork), HAVING Clause does not work for some reason in python, "
              "but works fine on GraphDB")
        f_out = open(file_query_out, "w+")

        for row in qres:
            # Row is a list of matched RDF terms: URIs, literals or blank nodes
            line_str = '\"%s\",\"%s\"\n' % (row.cnt, row.city)

            f_out.write(line_str)

        f_out.close()

    def performSPARQLQuery4(self, file_query_out):

        qres = self.graph.query(
            """PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
                SELECT ?rname ?Address ?postCode
                WHERE
                {
                    ?rname cw:locatedInAdress ?Address .
                    ?Address cw:locatedInCity ?City .
                    ?City cw:hasAdress ?Address .
                    ?Address cw:hasPostCode ?postCode .
                    FILTER(?postCode=cw:) .
                }GROUP BY ?rname ?Address ?postCode"""
        )

        print("QUERY4 - List of restaurants with missing postcode : %s" % (str(len(qres))))

        f_out = open(file_query_out, "w+")

        for row in qres:
            # Row is a list of matched RDF terms: URIs, literals or blank nodes
            line_str = '\"%s\",\"%s\",\"%s\"\n' % (row.rname, row.Address, row.postCode)

            f_out.write(line_str)

        f_out.close()

    def performSPARQLQuery5(self, file_query_out):

        qres = self.graph.query(
            """PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
                SELECT DISTINCT ?RestaurantName ?Restaurant ?City 
                WHERE
                {
                    ?RestaurantName cw:hasRestaurant ?Restaurant .
                    ?Restaurant cw:Restaurant ?restaurant_type .
                    ?RestaurantName cw:locatedInAdress ?Address .
                    ?Address cw:locatedInCity ?City .
                        FILTER(regex(?restaurant_type, 'american', 'i') || regex(?restaurant_type, 'asian', 'i'))
                }GROUP BY ?RestaurantName ?Restaurant ?City """
        )

        print("QUERY5 - List of American and Asian Restaurants : %s" % (str(len(qres))))

        f_out = open(file_query_out, "w+")

        for row in qres:
            # Row is a list of matched RDF terms: URIs, literals or blank nodes
            line_str = '\"%s\",\"%s\",\"%s\"\n' % (row.RestaurantName, row.Restaurant, row.City)

            f_out.write(line_str)

        f_out.close()
