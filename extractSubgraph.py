#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 14:20:09 2017

@author: fubao
"""

import sys
import csv
import os
from random import sample
from random import choice
from random import shuffle

import copy

#sys.path.append("../")

from hierarchicalQueryPython.CommonFiles.commons  import mycsv_reader
from hierarchicalQueryPython.CommonFiles.commons  import writeListRowToFileWriterTsv
from hierarchicalQueryPython.CommonFiles.commons  import  appendStringRowToFileWriterTsv


from hierarchicalQueryPython.graphCommon import readCiscoDataGraph
from hierarchicalQueryPython.graphCommon import readEdgeListToGraph
from hierarchicalQueryPython.graphCommon import PRODUCTDATATYPE
from hierarchicalQueryPython.graphCommon import SYNTHETICGRAPHNODETYPE
from hierarchicalQueryPython.graphCommon import DBLPDATATYPE

from subGraphCommon import getTypeNodeSet
from subGraphCommon import getFixedHopsNodes

from collections import defaultdict

import networkx as nx
#extractSubGraph from data graph

from math import floor
import signal
import multiprocessing


'''
0	product
1	vulnerability
2	bug_Id
3	workaround
4	technology
5	workgroup
6	product site
'''
#extract ratio of subgraph from data graph

class TimeLimitExpired(Exception): 
    pass

def timelimit(timeout, func, args=(), kwargs={}):
    """ Run func with the given timeout. If func didn't finish running
        within the timeout, raise TimeLimitExpired
    """
    import threading
    class FuncThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            self.result = func(*args, **kwargs)

        def _stop(self):
            if self.isAlive():
                threading.Thread._Thread__stop(self)

    it = FuncThread()
    it.start()
    it.join(timeout)
    if it.isAlive():
        print ("78 timeout here: ")
        #it._stop()
        raise TimeLimitExpired()
    else:
        return it.result
    
class ClsSubgraphExtraction(object):

    def __init__(self):
      pass
    
    '''
    def funcExtractSubGraph(self, G, startNodeSet, endNodeSet, specNodeNum, queryNodeNum, dstTypeLst):
    
        #extract query graph for experiments.
        #query graph size definition: specific node number-spn,  unknown query nodes- qn;      (spn, qn)
        #startNodeSet indicates the set with the node type of query node starting; endNodeSet indicates the node type of query node ending
        
        #find path of 
        #get the specNodeNum
        divider = floor(specNodeNum/queryNodeNum)
        residual = specNodeNum % queryNodeNum
        
        divideSpecNodeNum = []
        for i in range(queryNodeNum):              #assign specNodeNum size for each queryNodeNum (i.e. each star query size)
            if residual != 0:
                divideSpecNodeNum.append(divider + 1)           
                residual -= 1
            else:
                divideSpecNodeNum.append(divider)
        
        #print ("divideSpecNodeNum, : ", divideSpecNodeNum)
        
        queryGraphLst = []            # every element is a list [(nodeId, nodeId type)...]
        dstTypeIndex = 0              #which query node type
        for src in startNodeSet:
            #breakFlag = False
            for dst in endNodeSet:
                print(" xxxx ", src, dst)
                if src != dst:
                    #get all path
                    #print(" xxxx dddddd", src, dst)
                    #print ("nx.all_simple_paths: ")
                    #print (" ", list(nx.all_simple_paths(G, src, dst, cutoff= 100)))
                    #timeBegin = time.time()
                    
                    for path in nx.all_simple_paths(G, src, dst, cutoff= 11):
                        #check how many product inside the path
                        #check how many has product type in the path
                        #print(" path aaaaa", len(path))
                        prodNodes = []
                        tmpTargetIndex = 0
                        for nodeId in path:
                            if G.node[nodeId]['labelType'] == dstTypeLst[tmpTargetIndex]:
                                #print ("xxxxxxx: ", node)
                                prodNodes.append(nodeId)
                                tmpTargetIndex += 1
                                if len(prodNodes) >= queryNodeNum:
                                    break
                        if len(prodNodes) >= queryNodeNum:
                           # breakFlag = True
                            #get the 
                            #print(" resNodesPath ", path)
                            #cntQueryNum = 0
                            prevj = 0
                            for nd in path:
                                innerLst = []
                                #print(" len dstTypeLst ", len(dstTypeLst), dstTypeIndex, specNodeNum, queryNodeNum)
                                dstType = dstTypeLst[dstTypeIndex]               #get query node type
                                if G.node[nd]['labelType'] == dstType:
                                    #get node neighbor for specific number
                                    nbs = G[nd]  
                                    tmpCnt = 0
                                    j = prevj
                                    nbsLst= list(nbs.keys())
                                    #print ("type: ", type(nbs), len(nbsLst))
                                    while (j < len(nbsLst)):
                                        nb = nbsLst[j]
                                        if G.node[nb]['labelType'] != dstType and (nb, G.node[nb]['labelType']) not in innerLst:
                                            innerLst.append((nb, G.node[nb]['labelType']))
                                            tmpCnt += 1
                                            if innerLst in queryGraphLst:
                                                innerLst.pop()
                                            elif innerLst not in queryGraphLst and tmpCnt >= divideSpecNodeNum[dstTypeIndex]:  #safisfy specific number
                                                #cntQueryNum += 1
                                                queryGraphLst.append(innerLst)
                                                #print(" dstTypeIndex aa ", dstTypeIndex)
                                                dstTypeIndex += 1    #change next dstType index 
                                                if dstTypeIndex >= queryNodeNum:
                                                    #print(" queryGraphLst ", queryGraphLst)
                                                    return path, queryGraphLst
                                                break
                                        j += 1
                                    prevj = j
    
    '''
    
    
    def getRequiredPaths(self, G, src, levelLengthCutoff, numberDegree, dstTypeLst):
        '''
        from src to dst
        levelLengthCutoff: the level of node visited along the path  >= len(dstTypeLst)
        numberDegree: the maximum degree of each node visited
        cutoff: limited length of path
        get the simple paths with limited number and the required node type
        '''
        if src not in G:
            raise nx.NetworkXError('source node %s not in graph'%src)
        #if dst not in G:
        #    raise nx.NetworkXError('target node %s not in graph'%dst)
        if levelLengthCutoff is None:
            levelLengthCutoff = len(G)-1
        if levelLengthCutoff < 1:
            return []
        que = [(src, 0)]         # (nodeId, level)
        dstTypeTmpIndex = 0
        resQueryNodesEachStarQuery = []             #get each star query query node  
        explored = defaultdict()
        currentLevelWithdstTypeNode = -1
        while (len(que) != 0):
            #print ("198 enter here", que[-1])
            #pop queue
            ndIdInfo = que.pop()
            ndId = ndIdInfo[0]
            level = ndIdInfo[1]
            
            if G.node[ndId]['labelType'] == dstTypeLst[dstTypeTmpIndex] and level != currentLevelWithdstTypeNode != level:
                resQueryNodesEachStarQuery.append(ndId)
                dstTypeTmpIndex += 1
                currentLevelWithdstTypeNode = level
                if dstTypeTmpIndex >= len(dstTypeLst):
                    return resQueryNodesEachStarQuery
                
            if ndId not in explored:
                explored[ndId] = True              #added into explored list;  level arrived
                #get neighbor
                nbs = G[ndId]   #get neighbors
                que += [(nb, level+1) for nb in list(nbs)[:numberDegree]]
            if  level >= levelLengthCutoff:         #terminate
                return None
    


    def  funcExtractSubGraphHopped(self, G, startNodeLst, endNodeLst, specNodeNum, queryNodeNum, specificNdTypeLst, dstTypeLst, wholeTypeLst, hopsVisited):
        '''
        #extract query graph for experiments.
        #query graph size definition: specific node number-spn,  unknown query nodes- qn;      (spn, qn)
        #startNodeSet indicates the set with the node type of query node starting; endNodeSet indicates the node type of query node ending
        # hopVisited: how many hops at least from specific node to query node
        specNodeNum: total specific node number for general query graph
        queryNodeNum: total query node number for general query graph
        '''
         #get the specNodeNum
        divider = floor(specNodeNum/queryNodeNum)
        residual = specNodeNum % queryNodeNum
        
        StarQuerySpecNodes = []            #each star query Specific node
        for i in range(queryNodeNum):              #assign specNodeNum size for each queryNodeNum (i.e. each star query size)
            if residual != 0:
                StarQuerySpecNodes.append(divider + 1)           
                residual -= 1
            else:
                StarQuerySpecNodes.append(divider)
        
        queryGraphLst = []            # every element is a list [(nodeId, nodeId type)...]
        dstTypeIndex = 0              #which query node type
        
        
        shuffle(startNodeLst)
        shuffle(endNodeLst)
        for src in startNodeLst:
            #print(" xxxx ", src)

        #breakFlag = False
        #for dst in endNodeLst:
            #print(" xxxx ", src)
            #if src != dst:
            #get all path
            #print(" xxxx dddddd", src, dst)
            #print ("nx.all_simple_paths: ")
            #print (" ", list(nx.all_simple_paths(G, src, dst, cutoff= 100)))
            #timeBegin = time.time()
           
            #allPaths =  nx.all_simple_paths(G, src, dst, cutoff= 20)     #list(nx.all_pairs_shortest_path(G))        #        nx.all_simple_paths(G, src, dst, cutoff= 20))
            queryNodesStarQuery = self.getRequiredPaths(G, src, 600, 600, dstTypeLst)
            
            #allPaths = timelimit(60, nx.all_simple_paths, (G, src, dst, 50))
            if queryNodesStarQuery is None:
                continue
            #print(" 176 paths ",  len(list(queryNodesStarQuery)))
           
            #for path in paths:
            dstTypeIndex = 0
            if len(queryNodesStarQuery) >= queryNodeNum:        #make sure the path has enough node number satifying query nodeNum
               # breakFlag = True
                #get the 
                #print(" resNodesPath queryNodeNum ", queryNodeNum)
                #cntQueryNum = 0
                prevj = 0
                for nd in queryNodesStarQuery:
                    innerLst = []
                    #print(" len dstTypeLst ", len(dstTypeLst), dstTypeIndex, specNodeNum, queryNodeNum)
                    dstType = dstTypeLst[dstTypeIndex]               #get query node type
                    if G.node[nd]['labelType'] == dstType:
                        
                        #get hopvisited length list of set
                        sourceNode = nd
                        lastNodeTypes = copy.deepcopy(wholeTypeLst)
                        lastNodeTypes.remove(dstType)         #last level node types in hopvisited level
                        
                        answerNodes = getFixedHopsNodes(G, sourceNode, lastNodeTypes, hopsVisited)
                        
                        j = prevj
                        tmpCnt = 0       #check specific node number
                        while (j < len(answerNodes)):
                            newNd = answerNodes[j]
                            if G.node[newNd]['labelType'] != dstType and (newNd, G.node[newNd]['labelType']) not in innerLst:
                                if len(queryGraphLst) == 0:
                                    if G.node[newNd]['labelType'] in specificNdTypeLst:
                                        innerLst.append((newNd, G.node[newNd]['labelType']))
                                        tmpCnt += 1
                                        print(" 300 src = ", src)

                                else:
                                    innerLst.append((newNd, G.node[newNd]['labelType']))
                                    tmpCnt += 1
                                        
                            if innerLst in queryGraphLst:
                                innerLst.pop()
                            elif innerLst not in queryGraphLst and tmpCnt >= StarQuerySpecNodes[dstTypeIndex]:  #safisfy specific number
                                queryGraphLst.append(innerLst)
                                 #print(" dstTypeIndex aa ", dstTypeIndex)
                                dstTypeIndex += 1          #change next dstType index
                                if dstTypeIndex >= queryNodeNum:
                                    #print(" queryGraphLst ", queryGraphLst)
                                    return queryGraphLst
                                break            # break because tmpCnt >= StarQuerySpecNodes[dstTypeIndex]
                            j += 1
                        
                        prevj = j
                                                                 
        return []
        

                       
        
    def funcExecuteExtractQuerySynthetic(self, G, outFile):
        '''
        extract synthetic data query graph for decomposed star queries   
        '''
        os.remove(outFile) if os.path.exists(outFile) else None

        #get
        specNodesGeneralQueryNodesLst = [(2, 1),(4, 2), (6,3)]   #  [(2, 1),(4, 2), (4,3), (5,4), (6,3), (6,5), (7,7), (8, 8), (10,10)]  #    [(2, 1),(4, 2), (6,3)]   # [(2, 1),(4, 2), (4,3), (5,4), (6,5), (7,6), (8, 8), (10,10)]   
        #clear output file first
        hopsVisited = 1
    
        wholeTypeLst =  [SYNTHETICGRAPHNODETYPE.TYPE0HIER.value, SYNTHETICGRAPHNODETYPE.TYPE1HIER.value, SYNTHETICGRAPHNODETYPE.TYPE0INHERIT.value, 
                         SYNTHETICGRAPHNODETYPE.TYPE1INHERIT.value, SYNTHETICGRAPHNODETYPE.TYPE0GENERIC.value, SYNTHETICGRAPHNODETYPE.TYPE1GENERIC.value, SYNTHETICGRAPHNODETYPE.TYPE2GENERIC.value]
        specificNdTypeLst = [SYNTHETICGRAPHNODETYPE.TYPE0INHERIT.value]
        
        fd = open(outFile,'w')
        for tpls in specNodesGeneralQueryNodesLst:
            specNodeNum = tpls[0]
            queryNodeNum = tpls[1]
            #generated dstTypeLst randomly
            dstTypeLst = [SYNTHETICGRAPHNODETYPE.TYPE0HIER.value]             #first fixed at 0: TYPE0HIER
            randomLst = [SYNTHETICGRAPHNODETYPE.TYPE0HIER.value, SYNTHETICGRAPHNODETYPE.TYPE1HIER.value, SYNTHETICGRAPHNODETYPE.TYPE0INHERIT.value, SYNTHETICGRAPHNODETYPE.TYPE1INHERIT.value]        #TYPE1HIER	1; TYPE0INHERIT	2; TYPE1INHERIT	3  
            
            for i in range(0, queryNodeNum-1):
                dstTypeLst.append(choice(randomLst))       #[0]*queryNodeNum
            
            startNodeLst = list(getTypeNodeSet(G, dstTypeLst[0]))
            endNodeLst = list(getTypeNodeSet(G, dstTypeLst[-1]))
             
            queryGraphLst = self.funcExtractSubGraphHopped(G, startNodeLst, endNodeLst, specNodeNum, queryNodeNum, specificNdTypeLst, dstTypeLst, wholeTypeLst, hopsVisited)

            print("356 len queryGraphLst ", len(dstTypeLst), len(queryGraphLst))
            
            if queryGraphLst is not None:
                writeLst = []               #format: node11, node11Type;node12, node12Type;dsttype1    node21, node21Type;node22, node22Type;dsttype2....
                for i, specNumLst in enumerate(queryGraphLst[:(len(dstTypeLst))]):
                    inputStr = ""
                    for tpl in specNumLst[:-1]:         #except last element
                        inputStr += str(tpl[0]) + "," + str(tpl[1]) + ";"
                    
                    inputStr += str(specNumLst[-1][0]) + "," + str(specNumLst[-1][1])  + ";" + str(dstTypeLst[i])         #add last element
                    writeLst.append(inputStr)  
                
                writeListRowToFileWriterTsv(fd, writeLst, '\t')
        fd.close()

    def funcExecuteExtractQueryProduct(self, G, outFile):
        '''
        extract cisco product data query graph for decomposed star queries   
        '''
        #nodeLst = G.nodes()
        #print ("node number: ", len(nodeLst), G.node[1]['labelType'])
        os.remove(outFile) if os.path.exists(outFile) else None
        
       # specNodeNum = 13
       # queryNodeNum = 10
        wholeTypeLst =  [PRODUCTDATATYPE.PRODUCT.value, PRODUCTDATATYPE.VULNERABILITY.value, PRODUCTDATATYPE.BUGID.value, 
                         PRODUCTDATATYPE.WORKAROUND.value, PRODUCTDATATYPE.TECHNOLOGY.value, PRODUCTDATATYPE.WORKGROUP.value, PRODUCTDATATYPE.PRODUCTSITE.value]
        
        specNodesQueryNodesLst =  [(2, 1),(4, 2), (6,3)]  # [(2, 1),(4, 2), (4,3), (5,4), (6,3), (6,5), (7,7), (8, 8), (10,10)] #[(4,3), (6,3)]   #[(2, 1),(4, 2), (4,3), (6,3)]    #[(2, 1),(4, 2), (6,3)]    # [(2, 1),(4, 2), (4,3), (5,4), (6,5), (7,6), (8, 8), (10,10)]
        hopsVisited = 1
        
        fd = open(outFile,'w')
        for tpls in specNodesQueryNodesLst:
            specNodeNum = tpls[0]
            queryNodeNum = tpls[1]
            #generated dstTypeLst randomly
             
            dstTypeLst = [PRODUCTDATATYPE.PRODUCT.value]           # first one  [0]*queryNodeNum
            randomLst = [PRODUCTDATATYPE.PRODUCT.value, PRODUCTDATATYPE.VULNERABILITY.value, PRODUCTDATATYPE.TECHNOLOGY.value]

            specificNdTypeLst = [PRODUCTDATATYPE.VULNERABILITY.value]
            
            for i in range(0, queryNodeNum-1):
                dstTypeLst.append(choice(randomLst))       #[0]*queryNodeNum
            
            startNodeLst = list(getTypeNodeSet(G, dstTypeLst[0]))
            endNodeLst = list(getTypeNodeSet(G, dstTypeLst[-1]))
            print ("funcExecuteExtractQueryProduct startNodeSet endNodeSet: ",dstTypeLst[0], dstTypeLst[-1], len(startNodeLst), len(endNodeLst))
        
            queryGraphLst = self.funcExtractSubGraphHopped(G, startNodeLst, endNodeLst, specNodeNum, queryNodeNum, specificNdTypeLst, dstTypeLst, wholeTypeLst, hopsVisited)
    
            print("395 len queryGraphLst ", len(queryGraphLst), len(dstTypeLst))
            if queryGraphLst is not None:
                writeLst = []              #format: node11, node11Type;node12, node12Type;dsttype1    node21, node21Type;node22, node22Type;dsttype2....
                for i, specNumLst in enumerate(queryGraphLst[:(len(dstTypeLst))]):
                    inputStr = ""
                    for tpl in specNumLst[:-1]:
                        inputStr += str(tpl[0]) + "," + str(tpl[1]) + ";"
                        
                    inputStr += str(specNumLst[-1][0]) + "," + str(specNumLst[-1][1])  + ";" + str(dstTypeLst[i])
                    writeLst.append(inputStr)  
                    
                writeListRowToFileWriterTsv(fd, writeLst, '\t')
        fd.close()
        
    def funcExecuteExtractQueryDblp(self, G, outFile):
        '''
        extract dblp data query graph for decomposed star queries 
        '''
        os.remove(outFile) if os.path.exists(outFile) else None
        
        wholeTypeLst =  [DBLPDATATYPE.PEOPLE.value, DBLPDATATYPE.PAPER.value, DBLPDATATYPE.TOPIC.value, DBLPDATATYPE.TIME.value, DBLPDATATYPE.ARTICLE.value,
                         DBLPDATATYPE.BOOK.value, DBLPDATATYPE.INCOLLECTION.value, DBLPDATATYPE.INPROCEEDINGS.value, DBLPDATATYPE.MASTERSTHESIS.value,
                         DBLPDATATYPE.PHDTHESIS.value, DBLPDATATYPE.PROCEEDINGS.value, DBLPDATATYPE.WWW.value]
        
                        #[DBLPDATATYPE.PEOPLE.value, DBLPDATATYPE.PAPER.value, DBLPDATATYPE.TOPIC.value, DBLPDATATYPE.ARTICLE.value,
                        # DBLPDATATYPE.INPROCEEDINGS.value, DBLPDATATYPE.PROCEEDINGS.value] 
        
        specNodesQueryNodesLst = [(2, 1), (4, 2), (6,3)]  # [(5,4), (6,5), (7,7), (8, 8), (10,10)]  # [(2, 1),(4, 2), (4,3), (5,4), (6,5), (7,7), (8, 8), (10,10)]  # [(4,3), (6,3)] #[(2, 1),(4, 2), (6,3)]   #        [(2, 1),(4, 2), (4,3), (5,4), (6,5), (7,6), (8, 8), (10,10)]
    
        hopsVisited = 5

        fd = open(outFile,'w')
        for tpls in specNodesQueryNodesLst:
            specNodeNum = tpls[0]
            queryNodeNum = tpls[1]
            dstTypeLst = [] #  [DBLPDATATYPE.PEOPLE.value]          # [] [1]*queryNodeNum
            randomLst = [DBLPDATATYPE.PEOPLE.value, DBLPDATATYPE.PAPER.value, DBLPDATATYPE.TOPIC.value, DBLPDATATYPE.ARTICLE.value]
             
            specificNdTypeLst = [choice(randomLst)]       #[DBLPDATATYPE.TOPIC.value]
                   
            #for i in range(0, queryNodeNum-1):
            for i in range(0, queryNodeNum):
                dstTypeLst.append((DBLPDATATYPE.PEOPLE.value))       #  (DBLPDATATYPE.PEOPLE.value)    #(choice(randomLst))                         #choice(randomLst))       #[0]*queryNodeNum
            
            startNodeLst = list(getTypeNodeSet(G, dstTypeLst[0]))
            endNodeLst = list(getTypeNodeSet(G, dstTypeLst[-1]))
            print ("funcExecuteExtractQueryDblp startNodeSet endNodeSet: ", dstTypeLst[0], dstTypeLst[-1], len(startNodeLst), len(endNodeLst))
        
            queryGraphLst = self.funcExtractSubGraphHopped(G, startNodeLst, endNodeLst, specNodeNum, queryNodeNum, specificNdTypeLst, dstTypeLst, wholeTypeLst, hopsVisited)
            
            print("395 len queryGraphLst ", queryGraphLst, dstTypeLst)
            if queryGraphLst is not None:
                writeLst = []              #format: x,x;x,x;    x,x;,x,x....
                for i, specNumLst in enumerate(queryGraphLst[:(len(dstTypeLst))]): # if generated queryGraphLst more than the dstTypeLst
                    inputStr = ""
                    for tpl in specNumLst[:-1]:
                        inputStr += str(tpl[0]) + "," + str(tpl[1]) + ";"
                        
                    inputStr += str(specNumLst[-1][0]) + "," + str(specNumLst[-1][1])  + ";" + str(dstTypeLst[i])
                    writeLst.append(inputStr)  
                    
                writeListRowToFileWriterTsv(fd, writeLst, '\t')   
        fd.close()


    def subgraphFromDatagraph(self, G, rationofNodes, prevNodeSet):
        '''
        get subgraph from datagraph,  get 10% of data; 10%, 20%, 50, 80%, 100% 
        accumulate rationode, including previous node set
        '''
        #get random number of nodes
        numberIncreaseNodes = int(len(G)*rationofNodes) - len(prevNodeSet)
        print ("G numberNodes: ", len(prevNodeSet) + numberIncreaseNodes)
        
        leftNodes = set(G.nodes()) - set(prevNodeSet)
        numberNodesLst = prevNodeSet + sample(leftNodes, numberIncreaseNodes)
        #get subgraph
        subGraph = G.subgraph(numberNodesLst)    
        return subGraph, numberNodesLst


    
    def executeSubgraphExtractFromDatagraph(self, G, outputDir):
        '''
        #extract subgraph from any data graph
        # then write into file  with edge list format
        '''
        #10%, 20%, 50%, 80%, 100
      
        print ("G: ", len(G))
        rationofNodesLst= [0.1, 0.2, 0.5, 0.8, 1.0]
        prevNodeSet = []
        for rationofNodes in rationofNodesLst: 
            subG, numberNodesLst = self.subgraphFromDatagraph(G, rationofNodes, prevNodeSet)
            prevNodeSet = numberNodesLst
            #write out file
            directoryPath = outputDir + "dataGraphInfo" + str(rationofNodes)
            if not os.path.exists(directoryPath):
                os.makedirs(directoryPath)
            outFileEdgeLst =  directoryPath + "/edgeListPart" + str(rationofNodes)
            outFileNodeInfo = directoryPath + "/nodeInfoPart" + str(rationofNodes)
            os.remove(outFileEdgeLst) if os.path.exists(outFileEdgeLst) else None
            os.remove(outFileNodeInfo) if os.path.exists(outFileNodeInfo) else None

            #fh=open(outFile,'wb')
            #nx.write_edgelist(G, fh)
            #os.remove(outFileEdgeLst) if os.path.exists(outFileEdgeLst) else None
            
            fdEdge = open(outFileEdgeLst,'a')
            fdInfo = open(outFileNodeInfo,'a')
            nodeInfoLstCheckMap = {}
            for edge in subG.edges_iter(data='edgeHierDistance', default=1):
                #print ("edge: ", edge)
                nodeId1 = int(edge[0])
                node1LabelType = G.node[nodeId1]['labelType']       #G[nolabelType(0)
                node1LabelName = G.node[nodeId1]['labelName']  
                
                nodeInfoLst1 = [node1LabelName + "+++" + str(node1LabelType), nodeId1]
                
                if nodeId1 not in nodeInfoLstCheckMap:
                    writeListRowToFileWriterTsv(fdInfo, nodeInfoLst1, '\t')
                    nodeInfoLstCheckMap[nodeId1] = 1
                    
                nodeId2 = int(edge[1])
                node2LabelType = G.node[nodeId2]['labelType']       #G[nolabelType(0)
                node2LabelName = G.node[nodeId2]['labelName']
                nodeInfoLst2 = [node2LabelName + "+++" + str(node2LabelType), nodeId2]
                if nodeId2 not in nodeInfoLstCheckMap:
                    writeListRowToFileWriterTsv(fdInfo, nodeInfoLst2, '\t')
                    nodeInfoLstCheckMap[nodeId2] = 1

                if edge[2] == 0:
                    edgeStr = "same"
                    writeListRowToFileWriterTsv(fdEdge, [edge[0], edge[1], edgeStr], '\t')
                elif edge[2] == 1:
                    edgeStr = "higher"
                    writeListRowToFileWriterTsv(fdEdge, [edge[0], edge[1], edgeStr], '\t')
                elif edge[2] == -1:
                    edgeStr = "lower"
                    writeListRowToFileWriterTsv(fdEdge, [edge[0], edge[1], edgeStr], '\t')                    
            fdEdge.close()
            fdInfo.close()

    
    def funcMainStarQueryExatractDblpProduct(self):
        '''
        #extract subgraph as star query here from dblp data graph
        '''
        totalExpectedExtractedHierarchicalNodes = 4             #how many specific nodes expected to extract
        totalHierarchicalNodesTypeLst = [DBLPDATATYPE.TOPIC.value]
        
        totalNonHierarchicalNodes = 0
        nonHierarchicalNodeTypesLst = [DBLPDATATYPE.PEOPLE.value, DBLPDATATYPE.PAPER.value, DBLPDATATYPE.TIME.value, DBLPDATATYPE.ARTICLE.value,
                                 DBLPDATATYPE.BOOK.value, DBLPDATATYPE.INCOLLECTION.value, DBLPDATATYPE.INPROCEEDINGS.value, DBLPDATATYPE.MASTERSTHESIS.value,
                                 DBLPDATATYPE.PHDTHESIS.value, DBLPDATATYPE.PROCEEDINGS.value, DBLPDATATYPE.WWW.value]
    
        hopsVisited = 2
        hierarchicalLevelTypes = [DBLPDATATYPE.PAPER.value, DBLPDATATYPE.ARTICLE.value, DBLPDATATYPE.BOOK.value, DBLPDATATYPE.INCOLLECTION.value, 
                                  DBLPDATATYPE.INPROCEEDINGS.value, DBLPDATATYPE.MASTERSTHESIS.value, DBLPDATATYPE.PHDTHESIS.value, DBLPDATATYPE.PROCEEDINGS.value, DBLPDATATYPE.WWW.value]
        
        
        dblpGraphEdgeListFile = "../../GraphQuerySearchRelatedPractice/Data/dblpParserGraph/output/finalOutput/newOutEdgeListFile.tsv"
        dblpGraphNodeInfo = "../../GraphQuerySearchRelatedPractice/Data/dblpParserGraph/output/finalOutput/newOutNodeNameToIdFile.tsv"
        G = readEdgeListToGraph(dblpGraphEdgeListFile, dblpGraphNodeInfo)
        
        self.subFunctionStarQueryExtract(G, hierarchicalLevelTypes, totalExpectedExtractedHierarchicalNodes, totalHierarchicalNodesTypeLst, nonHierarchicalNodeTypesLst, totalNonHierarchicalNodes, hopsVisited)
    
    
    def funcMainStarQueryExatractCiscoProduct(self):
        '''
        extract star query graph from cisco data graph;   specific nodes number
        '''
        
        totalExpectedExtractedHierarchicalNodes = 4             #how many specific nodes expected to extract
        totalHierarchicalNodesTypeLst = [PRODUCTDATATYPE.VULNERABILITY.value, PRODUCTDATATYPE.TECHNOLOGY.value]
        
        totalNonHierarchicalNodes = 0
        nonHierarchicalNodeTypesLst = [PRODUCTDATATYPE.BUGID.value, PRODUCTDATATYPE.WORKAROUND.value, PRODUCTDATATYPE.WORKGROUP.value, PRODUCTDATATYPE.PRODUCTSITE.value]
        hopsVisited = 2
        hierarchicalLevelType = [PRODUCTDATATYPE.PRODUCT.value]
    
        ciscoNodeInfoFile = "../inputData/ciscoProductVulnerability/newCiscoGraphNodeInfo"
        ciscoAdjacentListFile = "../inputData/ciscoProductVulnerability/newCiscoGraphAdjacencyList"
        
        G = readCiscoDataGraph(ciscoAdjacentListFile, ciscoNodeInfoFile)
        
        self.subFunctionStarQueryExtract(G, hierarchicalLevelType, totalExpectedExtractedHierarchicalNodes, totalHierarchicalNodesTypeLst, nonHierarchicalNodeTypesLst, totalNonHierarchicalNodes, hopsVisited)
          
        
    #extract subgraph as star query here from synthetic data graph
    def funcMainStarQueryExatractSyntheticGraph(self):
        '''
        extract star query graph from synthetic data graph;   specific nodes number
        '''
        totalExpectedExtractedHierarchicalNodes = 10             #how many specific nodes expected to extract
        totalHierarchicalNodesTypeLst = [SYNTHETICGRAPHNODETYPE.TYPE0INHERIT.value, SYNTHETICGRAPHNODETYPE.TYPE1INHERIT.value]
        
        totalNonHierarchicalNodes = 0
        nonHierarchicalNodeTypesLst = [SYNTHETICGRAPHNODETYPE.TYPE0GENERIC.value, SYNTHETICGRAPHNODETYPE.TYPE1GENERIC.value, SYNTHETICGRAPHNODETYPE.TYPE2GENERIC.value]
        hopsVisited = 1
        hierarchicalLevelTypes = [SYNTHETICGRAPHNODETYPE.TYPE0HIER.value]
        
        syntheticGraphEdgeListFile = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraph_hierarchiRandom/syntheticGraphEdgeListInfo.tsv"
        syntheticGraphNodeInfo = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraph_hierarchiRandom/syntheticGraphNodeInfo.tsv"
        G = readEdgeListToGraph(syntheticGraphEdgeListFile, syntheticGraphNodeInfo)
        
        self.subFunctionStarQueryExtract(G, hierarchicalLevelTypes, totalExpectedExtractedHierarchicalNodes, totalHierarchicalNodesTypeLst, nonHierarchicalNodeTypesLst, totalNonHierarchicalNodes, hopsVisited)
        

        
    def subFunctionStarQueryExtract(self, G, hierarchicalLevelTypes, totalExpectedExtractedHierarchicalNodes, totalHierarchicalNodesTypeLst, nonHierarchicalNodeTypesLst, totalNonHierarchicalNodes, hopsVisited):
        '''
        1)specific node number in total
        2)hierarchical inheritance node number in total
        3)non-hierarchical inheritance node number in total
        4)hops of hierarchical node from query node to specific node
        '''
        
        #get nodes with hierarchical levels; e.g. product type
        hierNodeSet = set()
        for hierarchicalLevelType in hierarchicalLevelTypes:
           hierNodeSet |= getTypeNodeSet(G, hierarchicalLevelType)
        print ("funcMainStarQueryExatract: , G len ", len(G), hierarchicalLevelTypes, len(hierNodeSet))
        
        answerNodes = []
        
        i = 0
        #random visit a node
        flagCurrentNode = True
        resNodeQueryLst = []
        while (i < len(hierNodeSet)):
            #random get node
            node = choice(list(hierNodeSet))
            hierNodeSet.remove(node)
            
            #print ("funcMainStarQueryExatract node:  ", node)
            #find non-hierarchical inherited nodes first
            #check node neighbor
            for nb in G[node]:
                if G.node[nb]['labelType'] in nonHierarchicalNodeTypesLst:
                    if len(resNodeQueryLst) >= totalNonHierarchicalNodes:
                        break
                    resNodeQueryLst.append(nb)
    
            if len(resNodeQueryLst) < totalNonHierarchicalNodes:         #no neighbor nodes of node satifying requirement                     
                flagCurrentNode = True
            if not flagCurrentNode:
                flagCurrentNode = True
                continue                 #continue 
            else:
                # continue to search the hierarchical inheritance nodes; search the neighbor nodes again.
                #nodesLst = single_source_shortest_path(G, node, hopsVisited)          #time complexity is high
                answerNodes = getFixedHopsNodes(G, node, hierarchicalLevelTypes, totalHierarchicalNodesTypeLst[0] , hopsVisited)
                if len(set(answerNodes)) > totalExpectedExtractedHierarchicalNodes:           #find all the answers
                    resNodeQueryLst += list(set(answerNodes))
                    break
            i += 1
            
        resSpecificNodesLst = []                      #final result list (specific node, nodeType)
        for nodeId in resNodeQueryLst:
             resSpecificNodesLst.append((nodeId, G.node[nodeId]['labelType']))
             
        print ("funcMainStarQueryExatract specific query nodes: ", resSpecificNodesLst)
        return resSpecificNodesLst
    
    
        '''
    def funcMainEntryExecuteExtract(self):
        '''
        #main function extract subgraph as generic query graph
        '''
        ciscoNodeInfoFile = "../inputData/ciscoProductVulnerability/newCiscoGraphNodeInfo"
        ciscoAdjacentListFile = "../inputData/ciscoProductVulnerability/newCiscoGraphAdjacencyList"
        
        G = readCiscoDataGraph(ciscoAdjacentListFile, ciscoNodeInfoFile)
        
        #nodeLst = G.nodes()
        #print ("node number: ", len(nodeLst), G.node[1]['labelType'])
        
        productNodeSet = set()
        vulnerNodeSet = set()
        for n, d in G.nodes_iter(data=True):
            if d['labelType'] == 0:
                productNodeSet.add(n)
            if d['labelType'] == 1:
                vulnerNodeSet.add(n)
    
        print ("productNodeSet: ", len(productNodeSet))
        #workgroup = ((u,v) for u,v,d in G.nodes_iter(data=True) if d['labelType']==5)
        
       # specNodeNum = 13
       # queryNodeNum = 10
    
        specNodesQueryNodesLst = [(2, 1),(4, 2), (4,3), (5,4), (6,5), (7,6), (8, 8), (10,10)]
        
        outFile = "../hierarchicalQueryPython/output/extractSubgraphOutput/ciscoDataExtractQueryGraph"
        os.remove(outFile) if os.path.exists(outFile) else None
    
        fd = open(outFile,'a')
        
        for tpls in specNodesQueryNodesLst:
            specNodeNum = tpls[0]
            queryNodeNum = tpls[1]
            path, queryGraphLst = self.funcExtractSubGraph(G, productNodeSet, specNodeNum, queryNodeNum)
    
            writeLst = []              #format: x,x;x,x;    x,x;,x,x....
            for specNumLst in queryGraphLst:
                inputStr = ""
                for tpl in specNumLst[:-1]:
                
                    inputStr += str(tpl[0]) + "," + str(tpl[1]) + ";"
                inputStr += str(specNumLst[-1][0]) + "," + str(specNumLst[-1][1])
                writeLst.append(inputStr)  
                
            writeListRowToFileWriterTsv(fd, writeLst, '\t')
        '''
    
    
    def subgraphForQueryExecute(self):
        '''
        query graph subtraction      nonstar query including star query graph
        '''
        
        '''
        # extract query graph syntehtic data
        inputEdgeListfilePath = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraph_hierarchiRandom/syntheticGraphEdgeListInfo.tsv"
        inputNodeInfoFilePath = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraph_hierarchiRandom/syntheticGraphNodeInfo.tsv"
        
        G = readEdgeListToGraph(inputEdgeListfilePath, inputNodeInfoFilePath)
        outFile = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/inputQueryGraph/generalQueryGraph/generateQuerygraphInput"
        
        self.funcExecuteExtractQuerySynthetic(G, outFile)
        '''
        
        '''
        ciscoNodeInfoFile = "../../GraphQuerySearchRelatedPractice/Data/ciscoDataGraph/ciscoDataGraphInfo1.0/nodeInfoPart1.0"
        ciscoEdgeListFile = "../../GraphQuerySearchRelatedPractice/Data/ciscoDataGraph/ciscoDataGraphInfo1.0/edgeListPart1.0"
        outFile = "../../GraphQuerySearchRelatedPractice/Data/ciscoDataGraph/inputQueryGraph/generalQueryGraph/generateQuerygraphInput"
        
        G = readEdgeListToGraph(ciscoEdgeListFile, ciscoNodeInfoFile)
        self.funcExecuteExtractQueryProduct(G, outFile)             #extract query graph from data graph

        '''
        
        '''
        dblpNodeInfoFile = "../../GraphQuerySearchRelatedPractice/Data/dblpParserGraph/output/finalOutput/newOutNodeNameToIdFile.tsv"
        dblpEdgeListFile = "../../GraphQuerySearchRelatedPractice/Data/dblpParserGraph/output/finalOutput/newOutEdgeListFile.tsv"
        G = readEdgeListToGraph(dblpEdgeListFile, dblpNodeInfoFile)

        outFile = "../../GraphQuerySearchRelatedPractice/Data/dblpParserGraph/output/inputDblpQueryGraph/generalQueryGraph/generateQuerygraphInput"
        self.funcExecuteExtractQueryDblp(G, outFile)
        '''
       
        '''
        #data graph subtraction for synthetic  data 10% data graphdataPartPrefixs
        dataPartPrefixs = ["0.1", "0.2", "0.5", "0.8", "1.0"]
        for prefix in dataPartPrefixs:
            
            syntheticDataEdgeListFileTmp = "output/syntheticDataGraphExtractOut/dataGraphInfo" + prefix+ "/edgeListPart" + prefix
            syntheticDataNodeInfoFileTmp = "output/syntheticDataGraphExtractOut/dataGraphInfo" + prefix +"/nodeInfoPart" + prefix
            G = readEdgeListToGraph(syntheticDataEdgeListFileTmp, syntheticDataNodeInfoFileTmp)

            outputDir = "output/syntheticDataGraphExtractOut/inputGeneralQueryGraph/" + "queryGraphInput"+prefix      # output directory
        
            self.funcExecuteExtractQuerySynthetic(G, outputDir)
        '''
        
        '''
        #data graph subtraction for synthetic  data 10% data graphdataPartPrefixs
        dataPartPrefixs = ["0.1", "0.2", "0.5", "0.8", "1.0"]
        for prefix in dataPartPrefixs:
            
            syntheticDataEdgeListFileTmp = "output/ciscoDataGraphExtractOut/dataGraphInfo" + prefix+ "/edgeListPart" + prefix
            syntheticDataNodeInfoFileTmp = "output/ciscoDataGraphExtractOut/dataGraphInfo" + prefix +"/nodeInfoPart" + prefix
            G = readEdgeListToGraph(syntheticDataEdgeListFileTmp, syntheticDataNodeInfoFileTmp)

            outputDir = "output/ciscoDataGraphExtractOut/inputGeneralQueryGraph/" + "queryGraphInput"+prefix         # output directory
        
            self.funcExecuteExtractQueryProduct(G, outputDir)
        
        '''
        
        #data graph subtraction for synthetic  data 10% data graphdataPartPrefixs
        dataPartPrefixs = ["0.1", "0.2"]         #   , "0.5", "0.8", "1.0"]             # ["0.1", "0.2", "0.5", "0.8", "1.0"]
        for prefix in dataPartPrefixs:
            
            syntheticDataEdgeListFileTmp = "output/dblpDataGraphExtractOut/dataGraphInfo" + prefix+ "/edgeListPart" + prefix
            syntheticDataNodeInfoFileTmp = "output/dblpDataGraphExtractOut/dataGraphInfo" + prefix +"/nodeInfoPart" + prefix
            G = readEdgeListToGraph(syntheticDataEdgeListFileTmp, syntheticDataNodeInfoFileTmp)

            outputDir = "output/dblpDataGraphExtractOut/inputGeneralQueryGraph/" + "queryGraphInput"+prefix         # output directory
        
            self.funcExecuteExtractQueryDblp(G, outputDir)
            
    def subgraphExtractRatiosExecute(self):
        '''
        data graph subtraction for dblp data
        '''
        
        #data graph subtraction for synthetic  data
        syntheticDataEdgeListFile = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraph_hierarchiRandom/syntheticGraphEdgeListInfo.tsv"
        syntheticDataNodeInfoFile = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraph_hierarchiRandom/syntheticGraphNodeInfo.tsv"
        
        #G = readEdgeListToGraph(syntheticDataEdgeListFile, syntheticDataNodeInfoFile)

        #outputDir = "output/syntheticDataGraphExtractOut/"         # output directory
        #self.executeSubgraphExtractFromDatagraph(G, outputDir)
        #G = readEdgeListToGraph(syntheticDataEdgeListFile, syntheticDataNodeInfoFile)
        
        
        '''
        # extract subgraph of data graph  10%, 20,... 80% subgraph
        inputDataGraphfileDir = "output/syntheticDataGraphExtractOut/dataGraphInfo"
        
        ratios = ["0.1", "0.2", "0.5", "0.8"]     #1.0 is also there
        for r in ratios:
            G = readEdgeListToGraph(inputDataGraphfileDir  + r + "/edgeListPart" + r, inputDataGraphfileDir + r + "/nodeInfoPart" + r)
            outFile = inputDataGraphfileDir + "inputGeneralQueryGraph/generateQuerygraphInput" + r
            
            self.funcExecuteExtractQuerySynthetic(G, outFile)
        '''
        
            
        inputEdgeListFile = "../dblpParserGraph/output/finalOutput/newOutEdgeListFile.tsv"
        inputDblpNodeInfoFile = "../dblpParserGraph/output/finalOutput/newOutNodeNameToIdFile.tsv"
        #outputDir = "output/dblpDataGraphExtractOut/"       #output directory
        #G = readdblpDataGraph(inputEdgeListFile, inputDblpNodeInfoFile)
        #self.executeSubgraphExtractFromDatagraph(G, outputDir)
        
        
        #query graph subtraction from data subgraph
        inputDblpNodeInfo01File = "output/dblpDataGraphExtractOut/dataGraphInfo0.1/nodeInfoPart0.1"   
        inputEdgeList01File = "output/dblpDataGraphExtractOut/dataGraphInfo0.1/edgeListPart0.1"   
        #outFile = "output/extractDblpQuerySizeGraph/subDatagraphExtract/dblpData01ExtractQueryGraph.tsv"
        #self.funcExecuteExtractQueryDblp(inputDblpNodeInfo01File, inputEdgeList01File, outFile)             #extract query graph from data graph
        
        
        #data graph subtraction for cisco data
        ciscoEdgeListFile = "../../GraphQuerySearchRelatedPractice/Data/ciscoDataGraph/ciscoDataGraphInfo1.0/edgeListPart1.0"
        ciscoNodeInfoFile  = "../../GraphQuerySearchRelatedPractice/Data/ciscoDataGraph/ciscoDataGraphInfo1.0/nodeInfoPart1.0"
        
        #G = readEdgeListToGraph(ciscoEdgeListFile, ciscoNodeInfoFile)
        #outputDir = "output/ciscoDataGraphExtractOut/"         # output directory
        #self.executeSubgraphExtractFromDatagraph(G, outputDir)
            
    
        #query graph extraction from cisco data graph ( all ratios of data graph)
        inputProductNodeInfo01File = "../../../hierarchicalNetworkQuery/hierarchicalQueryPython/output/ciscoProductDataGraphExtractOut/dataGraphInfo0.1/nodeInfoPart0.1"   
        inputProductEdgeList01File = "../../../hierarchicalNetworkQuery/hierarchicalQueryPython/output/ciscoProductDataGraphExtractOut/dataGraphInfo0.1/edgeListPart0.1"   
        outFile = "../../../hierarchicalNetworkQuery/hierarchicalQueryPython/output/extractSubgraphQueryOutput/subDatagraphExtract/ciscoProductsData01ExtractQueryGraph.tsv"
        #G = readdblpDataGraph(inputProductEdgeList01File, inputProductNodeInfo01File)       #here use readdblpdatagraph, because it's edge list file, not adjcency list file
    
       # subgraphExtractionObj.funcExecuteExtractQueryProduct(G, outFile)             #extract query graph from data graph
        
       
        
#main 
def main():
    subgraphExtractionObj = ClsSubgraphExtraction()
    #subgraphExtractionObj.subgraphExtractRatiosExecute()
    

    #funcMainStarQueryExatractCiscoProduct()            
    #funcMainStarQueryExatractSyntheticGraph()
    #funcMainStarQueryExatractDblpProduct()

    subgraphExtractionObj.subgraphForQueryExecute()
    
    
if __name__== "__main__":
  main()
  
