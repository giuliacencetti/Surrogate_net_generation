import networkx as nx
import numpy as np
from scipy import stats
import community as community_louvain



def compute_average_ks(metric,graphs_in,graphs_gen):
    metrics_in = metric(graphs_in)
    metrics_gen = metric(graphs_gen)

    res = [[],[]]
    if metrics_in == [] or metrics_gen == []:
        s = 0
        p = 0
    else:
        s,p = stats.ks_2samp(metrics_in,metrics_gen)
    res[0].append(s)
    res[1].append(p)

    s,p = np.mean(res,-1)
    return s,p




# <p>
def dist_number_of_interacting_individuals(graphs):
    nb_individuals = []
    for g in graphs:
        individuals = interacting_individuals(g)
        nb_individuals.append(len(individuals))
    return(nb_individuals)

# used for <p>
def interacting_individuals(g):
    individuals = []
    conn_comp = [x for x in list(nx.connected_components(g)) if len(x)>1]
    for comp in conn_comp:
        for node in comp:
            individuals.append(node)
    return individuals

def largest_cc(graphs):
    l_cc = []
    for g in graphs:
        cc = [len(x) for x in list(nx.connected_components(g)) if len(x)>1]
        if cc != []:
            l_cc.append(max(cc))
    return l_cc

# assortativity
def get_ass(graphs):
    ass = []
    for g in graphs:
        if len(g.edges)>0:
            assort = nx.degree_assortativity_coefficient(g)
            if not np.isnan(assort):
                ass.append(assort)
    return ass

# <f>
def dist_nb_of_interactions(graphs):
    nb_interactions = []
    for g in graphs:
        nb_interactions.append(len(g.edges))
    return(nb_interactions)


def dist_degree(graphs):
    d_list = []
    for g in graphs:
        for node in g:
            d = g.degree[node]
            #if d != 0:
            d_list.append(d)
    return d_list



# <n>
def dist_number_of_new_conversations(graphs):

    nb_new_convs = []
    for i in range(len(graphs)-1):
        a1 = nx.adjacency_matrix(graphs[i])
        a2 = nx.adjacency_matrix(graphs[i+1])

        unique, counts = np.unique(np.asarray((a2-a1).A).reshape(-1), return_counts=True)
        d = dict(zip(unique, counts))
        if 1 in d:
            nb_new_convs.append(d[1]/2)
    return(nb_new_convs)


def strength(graphs):
    G = get_weighted_graph(graphs)
    return list(dict(G.degree(weight="weight")).values())



def dist_weight_of_edges(graphs):
    G = get_weighted_graph(graphs)
    w = [e[2]["weight"] for e in G.edges(data=True)]
    return(w)

def get_weighted_graph(graphs):
    weights = {}
    for g in graphs:
        for edge in g.edges():
            edge = list(np.sort(edge))
            if tuple(edge) not in weights:
                weights[tuple(edge)] = 1
            elif tuple(edge) in weights:
                weights[tuple(edge)] += 1
    G = nx.Graph()
    G.add_nodes_from(graphs[0].nodes())
    for edge in weights:
        G.add_edge(edge[0], edge[1], weight=weights[edge])
    return G






def dist_duration(graphs):
    dict_edges = dict()
    for g in graphs:
        for e in g.edges():
            if not e in dict_edges:
                dict_edges[e] = []
    for g in graphs:
        edges = list(g.edges())
        for k in dict_edges:
            if k in edges:
                dict_edges[k].append(1)
            else:
                dict_edges[k].append(0)
    for k,v in dict_edges.items():
        old = v[0]
        if old == 1:
            array = [1]
        else:
            array = []
        for i in v[1:]:
            if not i == 0:
                if old == 0:
                    array.append(1)
                if old == 1:
                    array[-1] += 1
            old = i
        dict_edges[k] = array
    res = [np.mean(x)for x in list(dict_edges.values())]
    return res


def cont_and_inter_cont_duration(graphs):
    dict_edges = dict()
    for g in graphs:
        for e in g.edges():
            if not e in dict_edges:
                dict_edges[e] = [0]*len(graphs)
    for t in range(len(graphs)):
        edges = list(graphs[t].edges())
        for edge in edges:
            dict_edges[edge][t] = 1
    dur_list = []
    ic_dur_list = []
    for edge in dict_edges:
        dur = []
        ic_dur = []
        D_flag = np.abs(1-dict_edges[edge][0])
        save_ic_flag = False # inter-contact is saved only if there's been a contact before
        for el in dict_edges[edge]:
            if save_ic_flag == False:
                if el == 1:
                    save_ic_flag = True
                    dur.append(1)
                    D_flag = 1
            else:
                if el == 1 and D_flag == 1:
                    dur[-1] += 1
                elif el == 0 and D_flag == 1 and save_ic_flag == True:
                    ic_dur.append(1)
                    D_flag = 0
                elif el == 0 and D_flag == 0 and save_ic_flag == True:
                    ic_dur[-1] += 1
                elif el == 1 and D_flag == 0:
                    dur.append(1)
                    D_flag = 1
        # if the sequence doesn't end with a contact I remove the last inter-contact duration (it's not an inter-contact)
        if dict_edges[edge][-1] == 0:
            ic_dur = ic_dur[:-1]

        if len(dur) != len(ic_dur) + 1:
            print('errore',len(dur),len(ic_dur))
        dur_list.extend(dur)
        ic_dur_list.extend(ic_dur)
    return dur_list, ic_dur_list





# deg density
def density(graphs):
    res = []
    for g in graphs:
        res.append(nx.density(g))
    return res

# local clustering
def local_clustering(graphs):
    res = []
    for g in graphs:
        tmp = nx.clustering(g)
        res.append(np.mean(list(tmp.values())))
    return res

# global_clustering
def global_clustering(graphs):
    res = []
    for g in graphs:
        res.append(nx.transitivity(g))
    return res


def find_communities_Louvain(G):
    partition_o = community_louvain.best_partition(G, weight='weight')
    nb_part = len(np.unique(list(partition_o.values())))
    classes_part = [[] for i in range(nb_part)]
    for node in partition_o:
        classes_part[partition_o[node]].append(node)
    return classes_part


def HO_size(graphs):
    len_cl = []
    for g in graphs:
        len_cl.extend([(len(clique)-1) for clique in list(nx.find_cliques(g)) if len(clique) > 1])
    return len_cl



def obtain_times_for_edge(data_,gap):
    edge_times = {}

    for _, row in data_.iterrows():
        if row['i'] > row['j']:
            print('Problem: i > j')
        if tuple([row['i'],row['j']]) not in edge_times:
            edge_times[(row['i'],row['j'])] = [row['t']*gap]
        else:
            if row['t']*gap != edge_times[(row['i'],row['j'])][-1]:
                edge_times[(row['i'],row['j'])].append(row['t']*gap)
        #print(edge_times)
    return edge_times


def in_times_dur(edge_times,gap):
    # In_times_dict is a dictionary. Keys: edges (the 2 nodes in increasing order). Values: initial times of events.
    # Dur_dict is a dictionary. Keys: edges (the 2 nodes in increasing order). Values: durations of events.

    In_times_dict = {}
    Dur_dict = {}

    for edge in edge_times:

        times = edge_times[edge]

        In_times_dict[edge] = [times[0]]
        Dur_dict[edge] = [gap]
        for n in range(len(times)-1):
            if times[n+1] - times[n] == gap:
                Dur_dict[edge][-1] += gap
            elif times[n+1] - times[n] > gap:
                In_times_dict[edge].append(times[n+1])
                Dur_dict[edge].append(gap)
            elif times[n+1] - times[n] < gap:
                print('error')
    return In_times_dict,Dur_dict


def event_counting(delta_t,In_times_dict,Dur_dict):
    Ev_nb = []
    ie_times_list = []
    for edge in In_times_dict:
        Ev_nb.append(1)
        for n in range(len(In_times_dict[edge]) - 1):
            ie_time = In_times_dict[edge][n+1] - (In_times_dict[edge][n] + Dur_dict[edge][n])
            ie_times_list.append(ie_time)
            if ie_time <= delta_t:
                Ev_nb[-1] += 1
            elif ie_time > delta_t:
                Ev_nb.append(1)
    return Ev_nb,ie_times_list


def nb_ev_train(data,gap,deltat):
    times_for_edge = obtain_times_for_edge(data,gap)
    In_times_orig, Dur_orig = in_times_dur(times_for_edge,gap)
    Ev_nb,_ = event_counting(deltat,In_times_orig, Dur_orig)
    return Ev_nb


def clustering_every_layer(graphs_list):
    clust_list = []
    for n in range(len(graphs_list)):
        clust_tmp = []
        for G in graphs_list[n]:
            clust_tmp.append(nx.transitivity(G))
        clust_list.append(clust_tmp)
    clust_m = np.mean(clust_list,axis=0)
    clust_s = np.std(clust_list,axis=0)
    return clust_m,clust_s



def mod_every_layer(graphs_list):
    mod_list = []
    for n in range(len(graphs_list)):
        mod_tmp = []
        for G in graphs_list[n]:
            if list(G.edges()) == []:
                mod_tmp.append(0)
            else:
                classes_part = find_communities_Louvain(G)
                mod_tmp.append(nx.community.modularity(G, classes_part, weight='weight', resolution=1))
        mod_list.append(mod_tmp)
    mod_m = np.mean(mod_list,axis=0)
    mod_s = np.std(mod_list,axis=0)

    return mod_m,mod_s
