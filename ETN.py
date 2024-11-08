from copy import deepcopy
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import itertools
import json
import os

def store_etns(S,file_name,gap,d,label):

    if label:
        name="gap_"+str(gap-1)+"_d_"+str(d)+"_LABEL.json"
    else:
        name="gap_"+str(gap-1)+"_d_"+str(d)+".json"

    directory = "res/"+file_name+"/ETNS/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    a_file = open(directory+name, "w")
    json.dump(S, a_file,indent=1)
    a_file.close()

    print("file stored in: \t"+directory+name)


def load_etns(file_name,gap,d,label):
    directory = "res/"+file_name+"/ETNS/"
    if label:
        name="gap_"+str(gap-1)+"_d_"+str(d)+"_LABEL.json"
    else:
        name="gap_"+str(gap-1)+"_d_"+str(d)+".json"

    with open(directory+name) as json_file:
        S = json.load(json_file)

    return S



def count_ETN(graphs,d):
    S = dict()
    for t in range(len(graphs)-d):
        for v in graphs[t].nodes():
            if v in graphs[0].nodes():
                #print('v',v)
                etn = obtain_ETN_subgraph(graphs[t:t+d+1],v)
                if not etn == None:
                    etns,_ = get_ETNS(etn)
                    if etns in S.keys():
                        S[etns] = S[etns] + 1
                    else:
                        S[etns] = 1
    return(S)









def from_ETNS_to_ETN(s,d):

    n = d + 1
    node_encoding = [s[2:][i:i+1] for i in range(0, len(s[2:]))]

    egos = [("0*_"+str(i),"0*_"+str(i+1)) for i in range(n-1)]



    ETN = nx.Graph()
    ETN.add_edges_from(egos)

    new_node_encoding = []

    for j in node_encoding:
        if("1" in j):
            new_node_encoding.append(1)
        else:
            new_node_encoding.append(0)

    node_encoding = new_node_encoding

    for i in range(0,len(node_encoding),n):
        same_person = []
        for j in range(n):
            if not(node_encoding[i+j] == 0):
                ETN.add_edge("0*_"+(str(j)),str(i+1)+"_"+str(j))
                same_person.append(str(i+1)+"_"+str(j))

        if len(same_person) > 1:
            for d in range(len(same_person)-1):
                ETN.add_edge(same_person[d],same_person[d+1])



    return(ETN)



def get_ETNS(ETN):
    '''
    It translates the ETN (a nx.graph) in signature. It return the signature etns and
    node_encoding, which tells at which node the signature is referring.
    For instance:
    ETNS,node_encoding = 1011 {'65': '10', '56': '11'}
    means that node n has had an interaction 10 with node 65 and
    an interaction 11 with node 56.
    '''
    nodes = list(ETN.nodes())
    nodes_no_ego = []
    ids_no_ego = []
    length_ETNS = 0
    for n in nodes:
        if not ("*" in n):
            nodes_no_ego.append(n)
            if not(n.split("_")[0] in ids_no_ego):
                ids_no_ego.append(n.split("_")[0])
        else:
            ego = int(n.split("*")[0])
            length_ETNS = length_ETNS + 1

    node_encoding = get_node_encoding(ids_no_ego,nodes_no_ego,length_ETNS)
    #print('node_encoding 0',node_encoding)

    ETNS = ''
    neighETN_list = []
    for neigh in node_encoding:
        neighETN = ''.join(str(s) for s in node_encoding[neigh])
        neighETN_list.append(neighETN)
        neighETN_list.sort()

    ETNS = ''.join(neighETN_list)
    #print('ETNS',ETNS)
    return(ETNS,node_encoding)


def sort_labeled_ETNS(ETN_list):
    ETN_list_i = [s for s in ETN_list if 'i' in s]
    ETN_list_e = [s for s in ETN_list if 'e' in s]
    ETN_list_i.sort()
    ETN_list_e.sort()
    ETN_list = ETN_list_i + ETN_list_e
    return ETN_list


def get_node_encoding(ids_no_ego,nodes_no_ego,length_ETNS):

    node_encoding = dict()
    for n in ids_no_ego:
        enc = ''
        for d in range(length_ETNS):
            if (str(n)+"_"+str(d) in nodes_no_ego):
                enc += '1'
            else:
                enc += '0'
        node_encoding[n]=enc

    return(node_encoding)



def obtain_ETN_subgraph(d_graphs,v):
    '''It returns a nx.graph representing the ETN with node v as ego'''
    ETN_edges = []
    ETN_neighs = []
    for t in range(len(d_graphs)):
        g = d_graphs[t]
        neighs = list(g.neighbors(v))
        for neigh in neighs:
            ETN_edges.append((str(v)+'*_'+str(t),str(neigh)+'_'+str(t)))
        ETN_neighs.append(neighs)

    for t in range(len(d_graphs) - 1):
        ETN_edges.append((str(v)+'*_'+str(t),str(v)+'*_'+str(t+1)))
        for neigh in ETN_neighs[t]:
            if neigh in ETN_neighs[t+1]:
                ETN_edges.append((str(neigh)+'_'+str(t),str(neigh)+'_'+str(t+1)))
    ETN = nx.Graph()
    for edge in ETN_edges:
        ETN.add_edge(edge[0],edge[1])
    return(ETN)



def draw_ETN(ETN,multiple=False):
    ids,d = get_ids_and_d(ETN)
    pos = dict()
    id_ego = []
    for t in range(d+1):
        for i in ids:
            if "*" in i:
                id_ego.append(str(i)+"_"+str(t))
                pos[str(i)+"_"+str(t)] = [t,int(i[0])]
            else:
                pos[str(i)+"_"+str(t)] = [t,int(i)]

    node_label = dict()
    nodes_data = dict(ETN.nodes(data=True))
    for i in list(ETN.nodes()):
        if not(nodes_data[i] == {}):
            node_label[i] = nodes_data[i]["label"]


    if (node_label == {}):
        nx.draw(ETN,pos=pos,node_size=100,alpha=0.9,with_labels=True)
        nx.draw_networkx_nodes(ETN, pos, nodelist=id_ego, node_size=300, node_color='red',alpha=0.5)
    else:
        nx.draw(ETN,pos=pos,node_size=100,alpha=0.5)
        nx.draw_networkx_nodes(ETN, pos, nodelist=id_ego, node_size=300, node_color='red',alpha=0.5)
        nx.draw_networkx_labels(ETN, pos, labels=node_label, font_size=12)

    if not multiple:
        plt.show()


# get unique ids (no time consideration)
def get_ids_and_d(ETN):
    nodes = list(ETN.nodes())
    ids = []
    d = 0
    for n in nodes:
        id_n = (n.split("_")[0])
        d_tmp = (n.split("_")[1])
        if not (id_n in ids):
            ids.append(id_n)
        if int(d_tmp) > d:
            d = int(d_tmp)
    return(ids,d)




def split_etns(etns,d):
    '''
    given: "001001001"
    return ["001","001","001"]
    '''
    splitted_etns = []
    for i in range(0,len(etns),d):
        splitted_etns.append(etns[i:i+d])

    return(splitted_etns)


def get_dict(ETNS,d):
    '''It generates the dictionary. It takes as input d and ETNS, which is a
    dictionary (referring for instance to one hour of the day, or better to
    local_split) with keys the signatures of the original graph and for values
    their nb of occurrences. The dictionary that it creates puts together the
    ETNSs that have the same key. Then it transforms frequencies into
    probabilities.
    New dictionary example:
    key: 11x
    value: [[110,111],[0.7,0.3]]
    '''
    new_node = ["0"*d+"1"]
    diz = dict()
    for etns in list(ETNS.keys()):
        if len(etns) % (d+1) == 0: # don't store the etns with length not multiple of d (they are those appearing at the end of the network)
            splitted_etns = split_etns(etns,d+1)
            key = ""
            for etn in splitted_etns:
                if not etn in new_node: # for 001 no need to create key, which is simply ""
                    key = key + etn[0:d]+"x"
            if key in diz: # append to diz the new pruned signature with its nb. of occurrences
                diz[key][0].append(etns)
                diz[key][1].append(ETNS[etns])
            else:
                diz[key] = [[etns],[ETNS[etns]]]

    for key,value in diz.items():
        summ = sum(diz[key][1]) # from frequences to probabilities
        c = 0
        for val in value[1]:
            diz[key][1][c] = diz[key][1][c]/summ
            c = c + 1

    return diz
