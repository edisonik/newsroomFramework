from django.shortcuts import render
from rdflib import Graph, Literal, BNode, Namespace, RDF, OWL, RDFS, URIRef
from rdflib.namespace import DC, FOAF, Namespace, URIRef

# Create your views here.



#zika_virus_owl = Graph()
#result = zika_virus_owl.parse("file://localhost/home/edison/Desktop/UnB/projetos/webSemantica/zika_virus.owl")

def kms(request):

    dados=[]

    zika_virus_owl = Graph()
    result = zika_virus_owl.parse("file://localhost/home/edison/newsroomFramework/kms/rdf_owl/zika_virus.rdf")

    #search2 = Graph()
    #search2.add(  )

    #inter = zika_virus_owl #& search2
    for s, p, o in result: #inter:
         dados.append( (s, p, o))
         dados.append("nnnn")
         #print((s, p, o))

    dados.append("AAAAAAAAAAAAAAAAAAAAAAAAAAA")



    qres = result.query(
        """SELECT ?p ?o
        WHERE{
            ?s ?p ?o
        }
        """
    )

    dados.append(qres)

    dados.append("xxxxxxxxxxxxxxxxxxxxxxxxxxx")

    g = Graph() #g e o grafo principal da ontologia

    # Create an identifier to use as the subject for Zika.
    Zika = BNode()

    name = Literal('Zika virus')

    # Add triples using store's add method.
    g.add( (Zika, Literal('causa'), Literal('doenca')) )
    g.add( (Literal('doenca'), Literal('tem'), Literal('prognostico')) )
    g.add( (Literal('prognostico'), Literal("pode ser"), Literal("maligno")) )
    g.add( (Literal('prognostico'), Literal("pode ser"), Literal("benigno")) )
    g.add( (Literal('maligno'), Literal("pode ser"), Literal("microcefalia")) )
    g.add( (Literal('maligno'), Literal("pode ser"), Literal("Sindrome de Guilain Barre")) )
    g.add( (Literal('maligno'), Literal("pode ser"), Literal("Fibromialgia")) )
    g.add( (Literal('maligno'), Literal("pode ser"), Literal("Cegueira neonatal")) )
    g.add( (Zika, Literal("tem"), Literal("diagnostico")) )
    g.add( (Literal('diagnostico'), Literal("realizado por"), Literal("teste")) )
    g.add( (Literal('teste'), Literal("pode ser"), Literal("PCR")) )



    g1 = Graph() #g1 e o grafo do documento 1
    g1.add( (Zika, Literal('causa'), Literal('doenca')) ) #note BNode em comum entre os grafos
    g1.add( (Literal('doenca'), Literal('tem'), Literal('prognostico')) )
    g1.add( (Literal('prognostico'), Literal("pode ser"), Literal("maligno")) )
    #g1.add( (Literal('maligno'), Literal("pode ser"), Literal("microcefalia")) )

    g2 = Graph() #g2 e o grafo do documento 2
    g2.add( (Zika, Literal('causa'), Literal('doenca')) ) #note BNode em comum entre os grafos
    g2.add( (Literal('doenca'), Literal('tem'), Literal('prognostico')) )
    g2.add( (Literal('prognostico'), Literal("pode ser"), Literal("maligno")) )
    g2.add( (Literal('maligno'), Literal("pode ser"), Literal("cegueira neonatal")) )
    g2.add( (Zika, Literal("tem"), Literal("diagnostico")) )
    g2.add( (Literal('diagnostico'), Literal("realizado por"), Literal("teste")) )
    g2.add( (Literal('teste'), Literal("pode ser"), Literal("PCR")) )

    search = Graph() #search e o grafo de busca
    search.add( (Zika, Literal('causa'), Literal('doenca')) ) #note BNode em comum entre os grafos
    search.add( (Literal('doenca'), Literal('tem'), Literal('prognostico')) )
    search.add( (Literal('maligno'), Literal("pode ser"), Literal("cegueira neonatal")) )
    search.add( (Zika, Literal("tem"), Literal("diagnostico")) )
    search.add( (Literal('diagnostico'), Literal("realizado por"), Literal("teste")) )
    search.add( (Literal('prognostico'), Literal("pode ser"), Literal("maligno")) )



    interseccao1=Graph()

    interseccao1 = search & g1

    # Iterate over triples in store and print them out.
    print("--- printing raw triples ---")
    dados.append("--- printing raw triples ---")
    match1=0
    for s, p, o in interseccao1:
        match1=match1 + 1
        print((s, p, o))
        dados.append((s, p, o))

    interseccao2=Graph()

    interseccao2 = search & g2
    print("--- printing raw triples ---")
    match2=0
    for s, p, o in interseccao2:
        match2=match2 + 1
        print((s, p, o))

    print("----------------------------------------------------------------")

    #print( interseccao.serialize(format='n3') )

    print("match1 = ",match1)
    print("match2 = ",match2)

    if ('Zica', None, None) in g:
        print("This graph contains triples about Bob!")

    #ver merging graphs
    context = {'dados': dados}

    return render(request, 'kms/kms.html', context)
