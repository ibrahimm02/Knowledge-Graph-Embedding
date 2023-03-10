class Query:
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

        print("%s : QUERY1 - Resaurant that sell pizzas without tomato." % (str(len(qres))))

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

        print("%s : QUERY2 - Average price of Margherita Pizza." % (str(len(qres))))

        f_out = open(file_query_out, "w+")

        for row in qres:
            # Row is a list of matched RDF terms: URIs, literals or blank nodes
            line_str = '\"%s\"\n' % (row.average)

            f_out.write(line_str)

        f_out.close()

    def performSPARQLQuery3(self, file_query_out):

        qres = self.graph.query(
                """PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
                SELECT DISTINCT ?city (COUNT(?rname) AS ?count)
                WHERE {
                    ?rname cw:locatedInAdress ?add .
                    ?add cw:locatedInCity ?city .
                    ?city cw:locatedInstate ?state .
                }
                GROUP BY ?city
                HAVING (?count > 6)
                ORDER BY ASC(?state) ASC(?count)"""
        )

        print("%s record satisfying the query3." % (str(len(qres))))

        f_out = open(file_query_out, "w+")

        for row in qres:
            # Row is a list of matched RDF terms: URIs, literals or blank nodes
            line_str = '\"%s\",\"%s\"\n' % (row.city, row.count)

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

        print("%s average satisfying the query4." % (str(len(qres))))

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

        print("%s pizzas satisfying the query5." % (str(len(qres))))

        f_out = open(file_query_out, "w+")

        for row in qres:
            # Row is a list of matched RDF terms: URIs, literals or blank nodes
            line_str = '\"%s\",\"%s\",\"%s\"\n' % (row.RestaurantName, row.Restaurant, row.City)

            f_out.write(line_str)

        f_out.close()





# QUERY 1
# PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
# SELECT DISTINCT ?restaurantName ?Address ?City
# WHERE {
#     ?restaurantName cw:locatedInAdress ?Address.
#     ?Address cw:locatedInCity ?City.
#     ?restaurantName cw:servesMenuItem ?pizzaItem.
#     ?pizzaItem cw:pizzaName ?pizza_name.
#     ?pizzaItem cw:hasIngredient ?ingre.
#     ?ingre cw:Ingredient ?ingredient.
#     FILTER NOT EXISTS
#     {
#         FILTER(regex(?pizza_name, 'tomat', 'i') || regex(?ingredient, 'tomat', 'i'))
#     }
# } GROUP BY ?restaurantName ?Address ?City


#QUERY 2
# PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
# SELECT (AVG(?amount) AS ?average)
# WHERE {
#     ?pizza cw:pizzaName ?pname .
#     ?pizza cw:hasValue ?value .
#     ?value cw:amount ?amount .
#     FILTER regex(?pname, 'marg', 'i')
# }


# QUERY 3
# PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
# SELECT DISTINCT ?city (COUNT(?rname) AS ?count)
# WHERE {
#     ?rname cw:locatedInAdress ?add .
#     ?add cw:locatedInCity ?city .
#     ?city cw:locatedInstate ?state .
# }
# GROUP BY ?city
# HAVING (?count > 6)
# ORDER BY ASC(?state) ASC(?count)


# QUERY 4  - OK
# PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
# SELECT ?rname ?Address ?postCode
# where
# {
#     ?rname cw:locatedInAdress ?Address .
#     ?Address cw:locatedInCity ?City .
#     ?City cw:hasAdress ?Address .
#     ?Address cw:hasPostCode ?postCode .
#     FILTER(?postCode=cw:) .
# }group by ?rname ?Address ?postCode


# QUERY 5  - OK
# PREFIX cw: <http://www.semanticweb.org/in3067-inm713/restaurants#>
# SELECT
# DISTINCT ?RestaurantName ?City ?Restaurant
# WHERE
# {
#     ?RestaurantName cw:hasRestaurant ?Restaurant .
#     ?Restaurant cw:Restaurant ?restaurant_type .
#     ?RestaurantName cw:locatedInAdress ?Address .
#     ?Address cw:locatedInCity ?City .
#     FILTER(regex(?restaurant_type, 'american', 'i') || regex(?restaurant_type, 'asian', 'i'))
# }GROUP BY ?RestaurantName ?City ?Restaurant
