# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 14:48:29 2017

@author: fubao
"""
import codecs
import csv
import networkx as nx
from enum import Enum
from collections import defaultdict


#from CommonFiles.commons import  writeListRowToFileWriterTsv
#from preprocessCiscoData import  readCiscoNodesInfo

#product database node types
class PRODUCTDATATYPE(Enum):
    PRODUCT = 0
    VULNERABILITY = 1
    BUGID = 2
    WORKAROUND = 3
    TECHNOLOGY = 4
    WORKGROUP = 5
    PRODUCTSITE = 6

#synthetic data graph
class SYNTHETICGRAPHNODETYPE(Enum):
    TYPE0HIER = 0             #hierarchical nodes with subcategory, category     30%
    TYPE1HIER = TYPE0HIER+1   #hierarchical nodes with subcategory, category      30%
    TYPE0INHERIT = TYPE0HIER + 2   #node that inheritance among hierarchical nodes 10%
    TYPE1INHERIT = TYPE0HIER + 3   #node that inheritance among hierarchical nodes 10%                               
    TYPE0GENERIC = TYPE0HIER + 4   #5%
    TYPE1GENERIC = TYPE0HIER + 5   #10%
    TYPE2GENERIC = TYPE0HIER + 6   #10%


#DBLP database node types
class DBLPDATATYPE(Enum):
    PEOPLE = 1
    PAPER = 2
    TOPIC = 3
    TIME = 4
    ARTICLE = 5
    BOOK = 6
    INCOLLECTION =7
    INPROCEEDINGS = 8
    MASTERSTHESIS = 9
    PHDTHESIS = 10
    PROCEEDINGS = 11
    WWW = 12
    
    
#read Graph
'''
def readGraph(adjacentListFile, nodeInfoFile1, nodeInfoFile2):
    
    #G.add_node('abc', dob=1185, pob='usa', dayob='monday')
    
    NodeNameMap = {}         #including previousDrugDBNodeMap ; #NewExerciseNodeMap
    
    with codecs.open(nodeInfoFile1, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        i = 0
        for row in tsvin:
            if len(row) >= 4:
                nodeId = row[0].strip().lower()         #string type
                nodeName = row[3].strip().lower()
                if nodeId not in NodeNameMap:
                    NodeNameMap[nodeId] = nodeName
                    
    with codecs.open(nodeInfoFile2, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        i = 0
        for row in tsvin:
            if len(row) >= 4:
                nodeId = row[0].strip().lower()         #string type
                nodeName = row[3].strip().lower()
                if nodeId not in NodeNameMap:
                    NodeNameMap[nodeId] = nodeName                

    G = nx.Graph() 
    with codecs.open(adjacentListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        i = 0
        for row in tsvin:
            if len(row) >= 2:
                nodeId = int(row[0])
                nodeType = int(row[1].split(';')[0].strip().lower())
                neighborLst = row[1].split(';')[1].strip().lower().split(' ')
                
                if nodeId in NodeNameMap:
                    nodeName = NodeNameMap[nodeId]
                else:
                    nodeName = "test"
                G.add_node(nodeId, type = nodeType, name=nodeName)
                for nb in neighborLst:
                    G.add_edge(nodeId, int(nb))
                
    print('G nodes: ', G.nodes(), "ddddd= ")  # G.node[1]['type'], nx.get_node_attributes(G,'type')[1])
    print('G edges: ', G.edges())
    #nx.draw(G, pos=nx.spring_layout(G))
    #nx.draw_networkx_labels(G,pos=nx.spring_layout(G))
    #plt.show()            
    nx.draw(G, with_labels = True)        # labels=nx.get_node_attributes(G,'type'))
    #plt.savefig('labels.png')
    return G   
'''

#read adjacency list test graph
def readTestGraph(adjacentListFile):
    G = nx.Graph() 
    with codecs.open(adjacentListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        i = 0
        for row in tsvin:
            if len(row) >= 2:
                nodeId = int(row[0])
                nodeType = int(row[1].split(';')[0].strip().lower())
                neighborLst = row[1].split(';')[1].strip().lower().split(' ')
                
                G.add_node(nodeId, labelType = nodeType)
                for nb in neighborLst:
                    G.add_edge(nodeId, int(nb))
                
    print('G nodes: ', G.nodes(), "ddddd= ")  # G.node[1]['type'], nx.get_node_attributes(G,'type')[1])
    print('G edges: ', G.edges())
    #nx.draw(G, pos=nx.spring_layout(G))
    #nx.draw_networkx_labels(G,pos=nx.spring_layout(G))
    #plt.show()            
    nx.draw(G, with_labels = True)        # labels=nx.get_node_attributes(G,'type'))
    #plt.savefig('labels.png')
    return G   
    
#read animal graph, multi edge graph
#sameHierarchy, higherHierarchy, lowerHierarchy edge

#node type:  0: animal
#            1: property
def readAnimalGraph(adjacentListFile, nodeInfoFile1):
    #G.add_node('abc', dob=1185, pob='usa', dayob='monday')
    
    NodeNameMap = {}
    with codecs.open(nodeInfoFile1, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        i = 0
        for row in tsvin:
            if len(row) >= 3:
                nodeId = int(row[0].strip().lower())         #string type
                nodeName = row[1].strip().lower()
                if nodeId not in NodeNameMap:
                    NodeNameMap[nodeId] = nodeName
                                        
    G = nx.MultiDiGraph()           #nx.DiGraph() 
    with codecs.open(adjacentListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        for row in tsvin:
            if len(row) >= 2:
                nodeId = int(row[0])
                nodeType = int(row[1].strip().lower())      # int(row[1].split(';')[0].strip().lower())
                neighborEdgeStr= row[2].strip().lower()        # row[1].split(';')[1].strip().lower().split(' ')
                
                if nodeId in NodeNameMap:
                    nodeName = NodeNameMap[nodeId]
                else:
                    nodeName = "test"
                G.add_node(nodeId, labelType=nodeType, labelName=nodeName)
                
                #hierarchy are recorded in the edge property
                sameIndex = neighborEdgeStr.find('same::')
                
                if sameIndex != -1:
                    #print ('xxx: ', len(lst), neighborEdgeStr[sameIndex+6:].split(' '))
                    for nb1 in neighborEdgeStr[sameIndex+6::].split(' '):
                        if 'lower::' in nb1 or 'higher::' in nb1:
                            break
                        else:
                            #print ('nb1: ', nb1)
#                            if nb1 == '54692':
#                                print ('nb1: ', nb1)
                            nb = nb1.strip().lower()
                            G.add_edge(nodeId, int(nb), key='sameHierarchy', edgeHierDistance = 0)
                
                higherIndex = neighborEdgeStr.find('higher::')
                if higherIndex != -1:
                    for nb1 in neighborEdgeStr[higherIndex+8::].split(' '):
                        if 'lower::' in nb1 or 'same::' in nb1:
                            break
                        else:
                            #print ('nb: ', nb1, nodeId)
                            nb = nb1.strip().lower()
#                            if nb == '54692':
#                                print ('nb1: ', nb)
                            G.add_edge(nodeId, int(nb), key='higherHierarchy', edgeHierDistance = 1)
                
                lowerIndex = neighborEdgeStr.find('lower::')
                if lowerIndex != -1:
                    for nb1 in neighborEdgeStr[lowerIndex+7::].split(' '):
                        if 'same::' in nb1 or 'higher::' in nb1:
                            break
                        else:
                            nb = nb1.strip().lower()
#                            if nb == '54692':
#                                print ('nb1: ', nb)
                            G.add_edge(nodeId, int(nb), key='lowerHierarchy', edgeHierDistance = -1)
                
#                if i >= 1:
#                    break
#                i += 1
                
    #print('G nodes: ', G.nodes(), "ddddd= ")  # G.node[1]['type'], nx.get_node_attributes(G,'type')[1])
    #print('G edges: ', G.edges())
    #print ('G one node: ', G[1], len(G[1]))    
    #print ('G one node2: ', G[54692], len(G[54692]))            
    #print ('G one edge18: ', G[1][8])    #['relativeHierarchy']['edgeHierDistance'] 
    #print ('G one edge2: ', G[2][54355]['relativeHierarchy']['edgeHierDistance'])
    #print ('G one edge3: ', G[54355][2])    
    #print ('G one edge4: ', G[54355][2]['relativeHierarchy']['edgeHierDistance'])
    #nx.draw(G, pos=nx.spring_layout(G))
    #nx.draw_networkx_labels(G,pos=nx.spring_layout(G))
    #plt.show()  
    #nodes = [i for i in range(1, 3)]
    #subG = G.subgraph(nodes) 
    #nx.draw(subG, with_labels = True, labels =nx.get_node_attributes(subG,'labelName'))  
    #nx.draw(G, with_labels = True, labels =nx.get_node_attributes(G,'labelName'))        # labels=nx.get_node_attributes(G,'type'))
    #plt.savefig('graph.pdf')

    return G 

'''
0	product
1	vulnerability
2	bug_Id
3	workaround
4	technology
5	workgroup
6	product site
'''

#read prodct data adjacency list file
def readCiscoDataGraph(adjacentListFile, ciscoNodeInfoFile):
    #G.add_node('abc', dob=1185, pob='usa', dayob='monday')

    NodeNameMap = {}
    with codecs.open(ciscoNodeInfoFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        for row in tsvin:
            if len(row) >= 3:
                nodeId = int(row[0].strip().lower())         #string type
                nodeName = row[1].strip().lower()
                if nodeId not in NodeNameMap:
                    NodeNameMap[nodeId] = nodeName
                    
    G = nx.MultiDiGraph()           #nx.DiGraph() 
    with codecs.open(adjacentListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        for row in tsvin:
            if len(row) >= 2:
                nodeId = int(row[0])
                nodeType = int(row[1].strip().lower())      # int(row[1].split(';')[0].strip().lower())
                neighborEdgeStr= row[2].strip().lower()        # row[1].split(';')[1].strip().lower().split(' ')
                
                if nodeId in NodeNameMap:
                    nodeName = NodeNameMap[nodeId]
                else:
                    nodeName = "test"
                G.add_node(nodeId, labelType=nodeType, labelName=nodeName)
                
                #hierarchy are recorded in the edge property
                sameIndex = neighborEdgeStr.find('same::')
                
                if sameIndex != -1:
                    #print ('xxx: ', len(lst), neighborEdgeStr[sameIndex+6:].split(' '))
                    for nb1 in neighborEdgeStr[sameIndex+6::].split(' '):
                        if 'lower::' in nb1 or 'higher::' in nb1:
                            break
                        else:
                            #print ('nb1: ', nb1)
#                            if nb1 == '54692':
#                                print ('nb1: ', nb1)
                            #print ('nodeIdaa: ',nodeId)
                            nb = nb1.strip().lower()
                            if nb != '':
                                G.add_edge(nodeId, int(nb), key='sameHierarchy', edgeHierDistance = 0)
                
                higherIndex = neighborEdgeStr.find('higher::')
                if higherIndex != -1:
                    for nb1 in neighborEdgeStr[higherIndex+8::].split(' '):
                        if 'lower::' in nb1 or 'same::' in nb1:
                            break
                        else:
                            #print ('nb: ', nb1, nodeId)
                            nb = nb1.strip().lower()
#                            if nb == '54692':
#                                print ('nb1: ', nb)
                            G.add_edge(nodeId, int(nb), key='higherHierarchy', edgeHierDistance = 1)
                
                lowerIndex = neighborEdgeStr.find('lower::')
                if lowerIndex != -1:
                    for nb1 in neighborEdgeStr[lowerIndex+7::].split(' '):
                        if 'same::' in nb1 or 'higher::' in nb1:
                            break
                        else:
                            nb = nb1.strip().lower()
#                            if nb == '54692':
#                                print ('nb1: ', nb)
                            G.add_edge(nodeId, int(nb), key='lowerHierarchy', edgeHierDistance = -1)
                
#                if i >= 1:
#                    break
#                i += 1
                
    #print('G nodes: ', G.nodes(), "ddddd= ")  # G.node[1]['labelType'], nx.get_node_attributes(G,'labelType')[1])
    #print('G edges: ', G.edges())
    #print ('G one node: ', G[1], len(G[1]))    
    #print ('G one node2: ', G[54692], len(G[54692]))            
    #print ('G one edge18: ', G[1][8])    #['relativeHierarchy']['edgeHierDistance'] 
    #print ('G one edge2: ', G[2][54355]['relativeHierarchy']['edgeHierDistance'])
    #print ('G one edge3: ', G[54355][2])    
    #print ('G one edge4: ', G[54355][2]['relativeHierarchy']['edgeHierDistance'])
    #nx.draw(G, pos=nx.spring_layout(G))
    #nx.draw_networkx_labels(G,pos=nx.spring_layout(G))
    #plt.show()  
    #nodes = [i for i in range(1, 3)]
    #subG = G.subgraph(nodes) 
    #nx.draw(subG, with_labels = True, labels =nx.get_node_attributes(subG,'labelName'))  
    #nx.draw(G, with_labels = True, labels =nx.get_node_attributes(G,'labelName'))        # labels=nx.get_node_attributes(G,'type'))
    #plt.savefig('graph.pdf')
    return G



def optimizeCiscoGraphEdgeList(edgeListFile, nodeInfoFile, newEdgeListFileOutput):
    '''
    optimize the ciscoGraph edgeList, there are could some noises in the edge list; e.g. non-hierarchical type could have 'higher' or 'lower' relations
    keep them all 'same' relations
    '''
    hierarchiType = 0
    hierarchicalNodeIdMap = {}         #only product type
    with codecs.open(nodeInfoFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        for row in tsvin:
            if len(row) >= 2:
                nodeNameTypeInfo = row[0].strip().lower()
                nodeType = int(nodeNameTypeInfo.split("+++")[1].strip().lower())
                nodeId = int(row[1].strip().lower())         #string type
                if nodeType == hierarchiType:
                    hierarchicalNodeIdMap[nodeId] = nodeType
                #print ('eeeee: ', nodeIdtoTypeMap)
                
                
    fd = open(newEdgeListFileOutput,'a')
     
    with codecs.open(edgeListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        newEdgeLst = []
        for row in tsvin:
            if len(row) >= 2:
                nodeSrcId = int(row[0].strip().lower())
                nodeDstId= int(row[1].strip().lower())       # row[1].split(';')[1].strip().lower().split(' ')
                relation = row[2].strip().lower()
                if nodeSrcId in hierarchicalNodeIdMap and nodeDstId in hierarchicalNodeIdMap:
                    newEdgeLst = [nodeSrcId, nodeDstId, relation]
                else:
                    newEdgeLst = [nodeSrcId, nodeDstId, 'same']
                writeListRowToFileWriterTsv(fd, newEdgeLst, '\t')
            
    fd.close()
    
#read edgelistToGraph
def readEdgeListToGraph(edgeListFile, nodeInfoFile):
    #G.add_node('abc', dob=1185, pob='usa', dayob='monday')

    nodeIdtoNameMap = defaultdict()
    nodeIdtoTypeMap = defaultdict()
    
    with codecs.open(nodeInfoFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        for row in tsvin:
            if len(row) >= 2:
                nodeNameTypeInfo = row[0].strip().lower()
                nodeName = nodeNameTypeInfo.split("+++")[0]
                nodeType = int(nodeNameTypeInfo.split("+++")[1].strip().lower())
                nodeId = int(row[1].strip().lower())         #string type
                nodeIdtoNameMap[nodeId] = nodeName
                nodeIdtoTypeMap[nodeId] = nodeType
                #print ('eeeee: ', nodeIdtoTypeMap)

    
    G = nx.MultiDiGraph()           #nx.DiGraph() 
    with codecs.open(edgeListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        for row in tsvin:
            if len(row) >= 2:
                nodeSrcId = int(row[0].strip().lower())
                nodeDstId= int(row[1].strip().lower())       # row[1].split(';')[1].strip().lower().split(' ')
                relation = row[2].strip().lower()
                G.add_node(nodeSrcId, labelType=nodeIdtoTypeMap[nodeSrcId], labelName=nodeIdtoNameMap[nodeSrcId])
                G.add_node(nodeDstId, labelType=nodeIdtoTypeMap[nodeDstId], labelName=nodeIdtoNameMap[nodeDstId])

            if relation == "higher":
                G.add_edge(nodeSrcId, nodeDstId, key='hierarchy', edgeHierDistance = 1)
            elif relation == "lower":
                G.add_edge(nodeSrcId, nodeDstId, key='hierarchy', edgeHierDistance = -1)
            else:
                G.add_edge(nodeSrcId, nodeDstId, key='hierarchy', edgeHierDistance = 0)

                
                
                
    #print ('nodeIdtoTypeMap: ', nodeIdtoTypeMap)
    #G = nx.read_edgelist(edgeListFile, nodetype=int, create_using=nx.MultiGraph(), data=(('hierarchy', str),))
    
    #nx.set_node_attributes(G, name='labelType', values=nodeIdtoTypeMap)
    #for n, d in G.nodes_iter(data=True):
        #d['labelType'] =  nodeIdtoTypeMap[n]
    #for n, d in G.nodes_iter(data=True):
        #d['labelType'] = nodeIdtoTypeMap[nodeId]    # len(G), G[1], 
    print ('graphInfo: ', len(G)) # G[2], G.node[8501]['labelType'])
    
    return G 

                   
#basic statisics of the graph
def statistGraphInfo(G):
    nodeNum = len(G)
    edgeNum = G.size()
    
    avgDegree = sum(G.degree().values())/float(len(G))
    print ('graphInfo: ', nodeNum, edgeNum, avgDegree)
    
#read the string to id;  natural language processing tranformation;
def queryInputStringtoNodeId(nodeInfoFile1, inputNameLst):
    nodeNameMap = {}
    nodeIdTypeMap = {}
    nodeIdTypeNameMap = {}
    #labelSet = set()
    with codecs.open(nodeInfoFile1, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        for row in tsvin:
            if len(row) >= 3:
                nodeId = int(row[0].strip().lower())         #string type
                nodeName = row[1].strip().lower()
                nodeTypeId = int(row[2].strip().lower())
                nodeTypeName = row[3].strip().lower()
                if nodeName not in nodeNameMap:
                    nodeNameMap[nodeName] = nodeId
                if nodeId not in nodeIdTypeMap:
                    nodeIdTypeMap[nodeId] = nodeTypeId
                if nodeId not in nodeIdTypeNameMap:
                    nodeIdTypeNameMap[nodeId] = nodeTypeName
                    #if nodeTypeId != 0:    #all properties type
                #    labelSet.add(nodeTypeName)
                
    #labelLst = list(labelSet)
    inputSrcNodeIdLst = []
    inputNameLst = [name.lower().strip() for name in inputNameLst]
    for ls in inputNameLst:
        inputSrcNodeIdLst.append(nodeNameMap[ls])
        #print ('input name id: ',ls, nodeNameMap[ls])
    return inputSrcNodeIdLst, nodeIdTypeMap, nodeIdTypeNameMap




'''
def queryInputStringtoNodeIdNew(nodeInfoFile1):
    nodeNameMap = {}
    nodeIdTypeMap = {}
    nodeIdTypeNameMap = {}
    nodeTypeNametoIdMap = {}
    #labelSet = set()
    with codecs.open(nodeInfoFile1, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        for row in tsvin:
            if len(row) >= 3:
                nodeId = int(row[0].strip().lower())         #string type
                nodeName = row[1].strip().lower()
                nodeTypeId = int(row[2].strip().lower())
                nodeTypeName = row[3].strip().lower()
                if nodeName not in nodeNameMap:
                    nodeNameMap[nodeName] = nodeId
                if nodeId not in nodeIdTypeMap:
                    nodeIdTypeMap[nodeId] = nodeTypeId
                if nodeId not in nodeIdTypeNameMap:
                    nodeIdTypeNameMap[nodeId] = nodeTypeName
                    #if nodeTypeId != 0:    #all properties type
                #    labelSet.add(nodeTypeName)
                if nodeTypeName not in nodeTypeNametoIdMap:
                    nodeTypeNametoIdMap[nodeTypeName] = nodeTypeId
                    
                
    #labelLst = list(labelSet)

    return nodeIdTypeMap, nodeIdTypeNameMap, nodeTypeNametoIdMap
'''
 

def testShortedPath():
    dblpEdgeListfile = "../../GraphQuerySearchRelatedPractice/Data/dblpParserGraph/output/finalOutput/newOutEdgeListFile.tsv"
    dblpNodeInfoFile = "../../GraphQuerySearchRelatedPractice/Data/dblpParserGraph/output/finalOutput/newOutNodeNameToIdFile.tsv"
    G = readEdgeListToGraph(dblpEdgeListfile, dblpNodeInfoFile)
    
    srcId = 188421
    dstId = 120096
    shortestPathLst = [p for p in nx.all_shortest_paths(G,source=srcId,target=dstId)]   # nx.all_shortest_paths(G, srcId, dstId)
    print("shortestPathLst : ", srcId, " --> ", dstId, ": ", shortestPathLst)


#G = ""
#outJsonFile = "output/testOutput/test1.json"
#drawGraphOnline(G)
#drawtopKRelatedGraph(G,  outJsonFile)
#webbrowser.get('firefox').open_new_tab('index.html')    

def testFution():
    
    #ciscoNodeInfoFile = "../inputData/ciscoProductVulnerability/newCiscoGraphNodeInfo"
    #ciscoAdjacentListFile = "../inputData/ciscoProductVulnerability/newCiscoGraphAdjacencyList"
    
    #G = readCiscoDataGraph(ciscoAdjacentListFile, ciscoNodeInfoFile)
    #statistGraphInfo(G)
    
   # edgeListProductFile = "../inputData/ciscoDataGraphInfo1.0EdgeList/edgeListPart1.0"
   # nodeInfoProductFile = "../inputData/ciscoDataGraphInfo1.0EdgeList/nodeInfoPart1.0"
   # G = readEdgeListToGraph(edgeListProductFile, nodeInfoProductFile)
    
    edgeListProductFile = "../../GraphQuerySearchRelatedPractice/Data/ciscoDataGraph/ciscoDataGraphInfo1.0/edgeListPart1.0"
    nodeInfoProductFile = "../../GraphQuerySearchRelatedPractice/Data/ciscoDataGraph/ciscoDataGraphInfo1.0/nodeInfoPart1.0"
    newEdgeListFileOutput = "../../GraphQuerySearchRelatedPractice/Data/ciscoDataGraph/ciscoDataGraphInfo1.0/optimizedEdgeListPart1.0"
    
    optimizeCiscoGraphEdgeList(edgeListProductFile, nodeInfoProductFile, newEdgeListFileOutput)


if __name__ == "__main__":
    testShortedPath()
    #testFution()    

    