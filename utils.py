import networkx as nx
import numpy as np
import pandas as pd
import csv
import os

def save_on_csv(filename, variable_list, writing_operation): # valid for list of list of lists
    with open(filename, writing_operation) as csvfile:
        writer = csv.writer(csvfile)
        try:
            [writer.writerow(s) for s in variable_list]
        except:
            writer.writerow(variable_list)


def load_list_of_lists_csv(filename):
    with open(filename, 'r') as csvfile:
        loaded_file = []
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            float_row = [float(i) for i in row]
            loaded_file.append(float_row)
    return loaded_file


def load_list_of_lists_csv_int(filename):
    with open(filename, 'r') as csvfile:
        loaded_file = []
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            float_row = [int(i) for i in row]
            loaded_file.append(float_row)
    return loaded_file


def load_list_csv(filename):
    with open(filename, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            float_row = [float(i) for i in row]
    return float_row


def save_on_npy(vect,filename):
    if os.path.exists(filename):
        old = list(np.load(filename,allow_pickle=True))
        old.append(vect)
        np.save(filename,old)
    else:
        np.save(filename,vect)


def load_data(path,sep=" "):
    '''load the cvs file representing the temporal graph

    Parameters:
    path (string): path of the input dataset

    Returns:
    np.array: a np array with the loaded data
    '''
    data = pd.read_csv(path,sep,names=["t","i","j"])
    return(data)


def build_graphs(data,gap):
    '''
    Given data from function above builds a list of networkx graphs, one for
    each snapshot.
    '''
    G=nx.Graph()
    nodes = list(np.unique(data.i))
    nodes.extend(np.unique(data.j))
    nodes_u = np.unique(nodes)
    G.add_nodes_from(nodes_u)

    times = [int(x/gap) for x in data.t]
    data.t = times
    graphs = []
    for time in range(max(times)+1):
        g = G.copy()
        link = data[data.t == time].to_numpy()
        for _,i,j in link:
            if i != j:
                g.add_edge(i,j)
        graphs.append(g)
    return(graphs)
