from ETN import *
import itertools
import random

Mem = np.full((10,10),0) # random size, I need it to define matrix Mem as a global variable, the correct size will be defined in generate_seed_graph
mem_all = []
for s in range(30):
    mem_all.append(np.full((1,1),0))

def find_neighbours(node,edges):
    neighs = [] # neighbors of node
    for edge in edges:
        if node in edge:
            if edge[0] != node:
                neighs.append(edge[0])
            else:
                neighs.append(edge[1])
    return neighs


def choose_dir_edges_ES(unidir_edges,edges_to_keep,nb_edges_to_add,Params,nb_past_common_neighs):
    '''
    First we sort edges according to nb of common neighbors, then we add them to
    edges_to_keep according to classes (using chi and c)
    '''
    classes = Params['classes']
    chi = Params['chi']
    if 'c' in Params:
        c = Params['c']
    else:
        c = 1
    T = {}
    for edge in unidir_edges:
        node0 = edge[0]
        node1 = edge[1]
        possible_edges = unidir_edges + edges_to_keep
        neighs0 = find_neighbours(node0,possible_edges)
        neighs1 = find_neighbours(node1,possible_edges)
        T[edge] = len([x for x in neighs0 if x in neighs1]) # common_neighs
    sorted_edges = []
    for m in np.sort(np.unique(list(T.values()))):
        edges_this_value = [k for k,v in T.items() if v == m]
        if len(edges_this_value) == 1:
            sorted_edges.extend(edges_this_value)
        else:
            Tpast = {}
            for edge in edges_this_value:
                if edge in nb_past_common_neighs:
                    Tpast[edge] = nb_past_common_neighs[edge]
                elif edge[::-1] in nb_past_common_neighs:
                    Tpast[edge] = nb_past_common_neighs[edge[::-1]]
                else:
                    Tpast[edge] = 0
            sorted_edges_this_value = [x for _,x in sorted(zip(Tpast.values(),edges_this_value))]
            sorted_edges.extend(sorted_edges_this_value)
    sorted_edges.reverse()
    remaining_sorted_edges = sorted_edges.copy()
    nb_added_edges = 0
    for edge in sorted_edges: # consider every edge once
        if nb_added_edges < nb_edges_to_add:
            if classes[edge[0]] == classes[edge[1]]:
                pp = (1 - chi)*c
            elif classes[edge[0]] != classes[edge[1]]:
                pp = chi*c
            r = random.random()
            if r < pp:
                edges_to_keep.append(edge)
                remaining_sorted_edges.remove(edge)
                nb_added_edges += 1
        else:
            break
    if nb_added_edges < nb_edges_to_add: # if did not find enough take the remaining ones at random
        np.random.shuffle(remaining_sorted_edges)
        edges_to_keep.extend(remaining_sorted_edges[0:(nb_edges_to_add-nb_added_edges)])

    return edges_to_keep


def choose_dir_edges_EST(unidir_edges,edges_to_keep,nb_edges_to_add,Params,nb_past_common_neighs,rho):
    if 'c' in Params:
        c = Params['c']
    else:
        c = 1
    if unidir_edges == []:
        edges_to_keep = []
    else:
        gamma = {} # Clustering
        for edge in unidir_edges:
            node0 = edge[0]
            node1 = edge[1]
            possible_edges = unidir_edges + edges_to_keep
            neighs0 = find_neighbours(node0,possible_edges)
            neighs1 = find_neighbours(node1,possible_edges)
            gamma[edge] = len([x for x in neighs0 if x in neighs1]) # common_neighs
        Order = {} # Sort edges according to memory and clustering
        for edge in unidir_edges:
            Order[edge] = (1 + gamma[edge]*c)*(1 + rho[edge]) # rho already normalized
        sorted_edges = []
        for m in np.sort(np.unique(list(Order.values()))):
            edges_this_value = [k for k,v in Order.items() if v == m]
            if len(edges_this_value) == 1:
                sorted_edges.extend(edges_this_value)
            else:
                Order_past = {}
                for edge in edges_this_value:
                    if edge in nb_past_common_neighs:
                        Order_past[edge] = nb_past_common_neighs[edge]
                    elif edge[::-1] in nb_past_common_neighs:
                        Order_past[edge] = nb_past_common_neighs[edge[::-1]]
                    else:
                        Order_past[edge] = 0
                sorted_edges_this_value = [x for _,x in sorted(zip(Order_past.values(),edges_this_value))]
                sorted_edges.extend(sorted_edges_this_value)
        sorted_edges.reverse()
        classes = Params['classes'] # choose them using chi too
        chi = Params['chi']
        #
        remaining_sorted_edges = sorted_edges.copy()
        nb_added_edges = 0
        for edge in sorted_edges: # consider every edge once
            if nb_added_edges < nb_edges_to_add:
                if classes[edge[0]] == classes[edge[1]]:
                    pp = 1 - chi
                elif classes[edge[0]] != classes[edge[1]]:
                    pp = chi
                r = random.random()
                if r < pp:
                    edges_to_keep.append(edge)
                    remaining_sorted_edges.remove(edge)
                    nb_added_edges += 1
            else:
                break
        if nb_added_edges < nb_edges_to_add:  # if did not find enough take the remaining ones at random
            np.random.shuffle(remaining_sorted_edges)
            edges_to_keep.extend(remaining_sorted_edges[0:(nb_edges_to_add-nb_added_edges)])
    return edges_to_keep


def choose_dir_edges(dir_edges,Params,nb_past_common_neighs,rho):
    '''Given the list of directed edges, it returns only the bidirectional ones
    + half of the others.
    '''
    edges_to_keep = []
    unidir_edges = []
    for (i,j) in dir_edges:
        if (j,i) in dir_edges:
            if (i,j) not in edges_to_keep and (j,i) not in edges_to_keep:
                edges_to_keep.append((i,j))
        else:
            unidir_edges.append((i,j))
    nb_edges_to_add = len(unidir_edges)*0.5
    if nb_edges_to_add.is_integer():
        nb_edges_to_add = int(nb_edges_to_add)
    else: # half points are rounded up half of the times and down half of the times
        r = random.random()
        if r < 0.5:
            nb_edges_to_add = int(nb_edges_to_add)
        else:
            nb_edges_to_add = int(nb_edges_to_add) + 1
    np.random.shuffle(unidir_edges)
    if Params['clust_modul'] == True and Params['memory'] == True: # EST
        edges_to_keep = choose_dir_edges_EST(unidir_edges,edges_to_keep,nb_edges_to_add,Params,nb_past_common_neighs,rho)
    if Params['clust_modul'] == True and Params['memory'] == False: # ES
        edges_to_keep = choose_dir_edges_ES(unidir_edges,edges_to_keep,nb_edges_to_add,Params,nb_past_common_neighs)
    elif Params['clust_modul'] == False and Params['memory'] == False: # E
        edges_to_keep.extend(unidir_edges[0:nb_edges_to_add])
    return edges_to_keep


def couple_stubs_ES(stub_nodes,edges_g2,Params,nb_past_common_neighs,past_edges):
    classes = Params['classes']
    chi = Params['chi']
    if 'c' in Params:
        c = Params['c']
    else:
        c = 1
    stubs_0cn = []
    flag = True
    stub_nodes_unique = np.unique(stub_nodes)
    while len(stub_nodes_unique) > 1:
        T = {}
        node = stub_nodes[0] # stub_nodes already shuffled
        neighs = find_neighbours(node,edges_g2)
        match = -1
        nb_common_neighs = 0
        candidate_backup = []
        for candidate in stub_nodes_unique:
            if candidate != node and candidate not in neighs:
                if tuple((candidate,node)) not in past_edges and tuple((node,candidate)) not in past_edges:
                    candidate_neighs = find_neighbours(candidate,edges_g2)
                    T[candidate] = len([x for x in neighs if x in candidate_neighs]) #nb of common neighbors
                else:
                    candidate_backup.append(candidate)
        sorted_candidates = []
        for m in np.sort(np.unique(list(T.values()))):
            cand_this_value = [k for k,v in T.items() if v == m]
            if len(cand_this_value) == 1:
                sorted_candidates.extend(cand_this_value)
            else:
                Tpast = {}
                for cand in cand_this_value:
                    if (node,cand) in nb_past_common_neighs:
                        Tpast[cand] = nb_past_common_neighs[(node,cand)]
                    elif (cand,node) in nb_past_common_neighs:
                        Tpast[cand] = nb_past_common_neighs[(cand,node)]
                    else:
                        Tpast[cand] = 0
                sorted_cand_this_value = [x for _,x in sorted(zip(Tpast.values(),cand_this_value))]
                sorted_candidates.extend(sorted_cand_this_value)
        sorted_candidates.reverse()
        #
        if sorted_candidates==[]:
            if candidate_backup==[]:
                stub_nodes = [i for i in stub_nodes if i != node]  # lo rimuovo perché tutti gli altri stub sono o lui stesso o suoi vicini
                stub_nodes_unique = np.unique(stub_nodes)
            else:
                edges_g2.append(tuple([node,candidate_backup[0]]))
                stub_nodes.remove(node)
                stub_nodes.remove(candidate_backup[0])
                stub_nodes_unique = np.unique(stub_nodes)
        else:
            flag_stub = True
            for cand in sorted_candidates:
                if flag_stub:
                    if classes[node] == classes[cand]:
                        pp = (1 - chi)*c
                    elif classes[node] != classes[cand]:
                        pp = chi*c
                    r = random.random()
                    if r < pp:
                        edges_g2.append(tuple([node,cand]))
                        stub_nodes.remove(node)
                        stub_nodes.remove(cand)
                        stub_nodes_unique = np.unique(stub_nodes)
                        flag_stub = False
                        break
            if flag_stub and sorted_candidates!=[]:
                edges_g2.append(tuple([node,sorted_candidates[0]]))
                stub_nodes.remove(node)
                stub_nodes.remove(sorted_candidates[0])
                stub_nodes_unique = np.unique(stub_nodes)
    return edges_g2


def pop_random(lst):
    idx = random.randrange(0, len(lst))
    return lst.pop(idx)



def couple_stubs_EST(stub_nodes,edges_g2,Params,nb_past_common_neighs,past_edges,rho):
    classes = Params['classes']
    chi = Params['chi']
    if 'c' in Params:
        c = Params['c']
    else:
        c = 1
    stubs_0cn = []
    flag = True
    stub_nodes_unique = np.unique(stub_nodes)
    while len(stub_nodes_unique) > 1:
        T = {}
        node = stub_nodes[0] # stub_nodes already shuffled
        neighs = find_neighbours(node,edges_g2)
        match = -1
        nb_common_neighs = 0
        candidate_backup = []
        for candidate in stub_nodes_unique:
            if candidate != node and candidate not in neighs:
                if tuple((candidate,node)) not in past_edges and tuple((node,candidate)) not in past_edges:
                    candidate_neighs = find_neighbours(candidate,edges_g2)
                    gamma = len([x for x in neighs if x in candidate_neighs]) #nb of common neighbors
                    T[candidate] = (1 + gamma*c)*(1 + rho[node,candidate])
                else:
                    candidate_backup.append(candidate)
        sorted_candidates = []
        for m in np.sort(np.unique(list(T.values()))):
            cand_this_value = [k for k,v in T.items() if v == m]
            if len(cand_this_value) == 1:
                sorted_candidates.extend(cand_this_value)
            else:
                Tpast = {}
                for cand in cand_this_value:
                    if (node,cand) in nb_past_common_neighs:
                        Tpast[cand] = nb_past_common_neighs[(node,cand)]
                    elif (cand,node) in nb_past_common_neighs:
                        Tpast[cand] = nb_past_common_neighs[(cand,node)]
                    else:
                        Tpast[cand] = 0
                sorted_cand_this_value = [x for _,x in sorted(zip(Tpast.values(),cand_this_value))]
                sorted_candidates.extend(sorted_cand_this_value)
        sorted_candidates.reverse()
        #
        if sorted_candidates==[]:
            if candidate_backup==[]:
                stub_nodes = [i for i in stub_nodes if i != node]  # remove i because all the other stubs are i itself or its neighbors
                stub_nodes_unique = np.unique(stub_nodes)
            else:
                edges_g2.append(tuple([node,candidate_backup[0]]))
                stub_nodes.remove(node)
                stub_nodes.remove(candidate_backup[0])
                stub_nodes_unique = np.unique(stub_nodes)
        else:
            flag_stub = True
            for cand in sorted_candidates:
                if flag_stub:
                    if classes[node] == classes[cand]:
                        pp = 1 - chi
                    elif classes[node] != classes[cand]:
                        pp = chi
                    r = random.random()
                    if r < pp:
                        edges_g2.append(tuple([node,cand]))
                        stub_nodes.remove(node)
                        stub_nodes.remove(cand)
                        stub_nodes_unique = np.unique(stub_nodes)
                        flag_stub = False
                        break
            if flag_stub and sorted_candidates!=[]:
                edges_g2.append(tuple([node,sorted_candidates[0]]))
                stub_nodes.remove(node)
                stub_nodes.remove(sorted_candidates[0])
                stub_nodes_unique = np.unique(stub_nodes)
    return edges_g2



def couple_stubs(stubs,edges_g2,Params,nb_past_common_neighs,past_edges,rho):
    '''
    take in input [(91, 'x'), (42, 'x'), (60, 'x'), (78, 'x'), (77, 'x'), (21, 'x')]
    return (91,42),(60,21) etc
    '''
    np.random.shuffle(stubs)

    stub_nodes = [stub[0] for stub in stubs]
    if len(np.unique(stub_nodes)) > 1:
        while stub_nodes[-1] == stub_nodes[-2]: # avoid to remain with a unique node at the end that I can only couple with itself
            np.random.shuffle(stub_nodes)
        if Params['clust_modul'] == True and Params['memory'] == True:
            edges_g2 = couple_stubs_EST(stub_nodes,edges_g2,Params,nb_past_common_neighs,past_edges,rho)
        if Params['clust_modul'] == True and Params['memory'] == False:
            edges_g2 = couple_stubs_ES(stub_nodes,edges_g2,Params,nb_past_common_neighs,past_edges)
        elif Params['clust_modul'] == False and Params['memory'] == False:
            while len(np.unique(stub_nodes)) > 1:
                node = stub_nodes[0]
                stub_nodes.remove(node)
                neighs = find_neighbours(node,edges_g2)
                match = -1
                candidate_backup = []
                for candidate in stub_nodes:
                    if candidate != node and candidate not in neighs:
                        if tuple((candidate,node)) not in past_edges and tuple((node,candidate)) not in past_edges:
                            match = candidate
                            break
                        else:
                            candidate_backup.append(candidate)
                if match != -1:
                    edges_g2.append((node,match))
                    stub_nodes.remove(match)
                elif match == -1 and candidate_backup != []:
                    edges_g2.append((node,candidate_backup[0]))
                    stub_nodes.remove(candidate_backup[0])

    return edges_g2



def split_stubs_and_edges(all_edges):
    '''Given a list of edges, it discerns between directed edges and stubs'''
    dir_edges = []
    stubs = []
    for edge in all_edges:
        if 'x' in edge:
            stubs.append(edge)
        else:
            dir_edges.append(edge)

    return dir_edges,stubs


def validate_edges_g2(edges,Params,nb_past_common_neighs,past_edges):
    dir_edges,stubs = split_stubs_and_edges(edges)
    if Params['memory'] == True:
        rho = mem_all[Params['state']]
        rho_max = rho.max()
        if rho_max == 0:
            rho_max = 1
        rho = rho/rho_max
    elif Params['memory'] == False:
        rho = 0
    edges_g2 = choose_dir_edges(dir_edges,Params,nb_past_common_neighs,rho)
    edges_g2 = couple_stubs(stubs,edges_g2,Params,nb_past_common_neighs,past_edges,rho)
    return edges_g2



def possible_next_edges_for_node(n,etns3,node_encoding,d):
    '''
    It returns the list of edges to add at the (d+1)-th layer, given node n and the
    egocentric neighborhood etns3.
    Example:
    n = 36
    etns3 = '100100100111'
    node_enc = {'99': '10', '56': '10', '65': '11', '32': '10'}
    Returns [(36, 65)]
    '''
    edges = []
    for split in split_etns(etns3,d+1):
        if split == "0"*d+"1":
            edges.append((n,"x")) # stub
        elif split[-1] == "1":
            possible_neigh = [key for key,value in node_encoding.items() if value == split[:d]] #look for the nodes that correspond to this key
            random.shuffle(possible_neigh)
            neigh = possible_neigh[0]
            edges.append((n,int(neigh))) # it becomes a candidate link in the temporary layer
            del node_encoding[neigh] # remove it from node_encoding
    return edges



def ETNS_lastd(graphs,d,node):
    '''It returns all the etns (at each timestamp) of a given node'''
    v = node
    if len(graphs) > d: # verify that the input graph has only d layers
        print('error')
    ETN = obtain_ETN_subgraph(graphs,v) # ETN is a nx.graph representing the motif with node v as ego
    if not ETN == None:
        ETNS,node_encoding = get_ETNS(ETN) # ETNS is the corresponding signature and node_encoding tells the node identity
    if len(ETNS) == 0:
        ETNS_key = ''
    else:
        ETNS_key = "x".join(split_etns(ETNS,d))+"x"
    return (ETNS_key,node_encoding)




def sample_from_diz(diz,key,d):
    '''
    It returns a new etns (like 101), given a key (like 10x), according to the probability stored in the dictionary.
    '''
    if (key in diz):
        etns = diz[key][0]
        prob = diz[key][1]
        cumulative = [sum(prob[0:i+1]) for i in range(len(prob))]
        cumulative = [0]+cumulative
        r = random.random()
        for i in range(len(cumulative)-1):
            if r >= cumulative[i]  and r < cumulative[i+1]:
                return etns[i]
    else: # if key is not in dictionary need to approximate it (removing one node)
        s_key = split_etns(key,d+1)
        for n in range(len(s_key)):
            appr_key = ''
            for m in range(len(s_key)):
                if m != n:
                    appr_key += s_key[m]
            if (appr_key in diz):
                etns = diz[appr_key][0]
                prob = diz[appr_key][1]
                cumulative = [sum(prob[0:i+1]) for i in range(len(prob))]
                cumulative = [0]+cumulative
                r = random.random()
                for i in range(len(cumulative)-1):
                    if r >= cumulative[i]  and r < cumulative[i+1]:
                        return etns[i] # exit from function
        for n in range(len(s_key) - 1): #second approximation: remove another node (it enters here only if didn't find anything with 1st approx)
            for l in range(n + 1,len(s_key)):
                appr_key = ''
                for m in range(len(s_key)):
                    if m != n and m != l:
                        appr_key += s_key[m]
                if (appr_key in diz):
                    etns = diz[appr_key][0]
                    prob = diz[appr_key][1]
                    cumulative = [sum(prob[0:i+1]) for i in range(len(prob))]
                    cumulative = [0]+cumulative
                    r = random.random()
                    for i in range(len(cumulative)-1):
                        if r >= cumulative[i]  and r < cumulative[i+1]:
                            return etns[i]
         # third approx: random key (it arrives here only if didn't find anything with 1st and 2nd approx)
        key_new = ''
        for el in key:
            if el == 'x':
                r = random.random()
                if r < 0.8:
                    key_new += '0'
                else:
                    key_new += '1'
            else:
                key_new += el
        return key_new






def generate_next_layer(nodes,graphs,diz,d,Params):
    '''It generates a new temporal layer (a nx graph), given the previous d layers, the dictionary and the nodes list'''

    edges = []
    for node in graphs[0].nodes(): #build provisional layer
        if node in Params['absent_nodes']:
            ETNS_new = ''
            node_enc = {}
        else:
            ETNS_key,node_enc = ETNS_lastd(graphs,d,node) # etns of the last d layers for node n e.g.: node=14 ETNS_key=01x11x node_enc={'30': '01', '21': '11'}
            ETNS_new = sample_from_diz(diz,ETNS_key,d)
            #print(ETNS_key,node_enc,ETNS_new)
        if not ETNS_new == None:
            edges.extend(possible_next_edges_for_node(node,ETNS_new,node_enc,d))
    past_edges_all = []
    for G in graphs:
        past_edges_all += list(G.edges())
    past_edges = [x for x in set(tuple(x) for x in past_edges_all)] # delete duplicated edges
    past_nodes = np.unique(past_edges) # nb nodes active in the last 2 layers
    nb_past_common_neighs = {}
    for i in range(len(past_nodes)-1):
        for j in range(i+1,len(past_nodes)):
            neighs_i = find_neighbours(past_nodes[i],past_edges)
            neighs_j = find_neighbours(past_nodes[j],past_edges)
            nb_past_common_neighs[(past_nodes[i],past_nodes[j])] = len([x for x in neighs_i if x in neighs_j])
    edges_g2 = validate_edges_g2(edges,Params,nb_past_common_neighs,past_edges)
    if Params['memory'] == True:
        global mem_all
        for edge in edges_g2:
            mem_all[Params['state']][edge] += 1
            mem_all[Params['state']][edge[::-1]] += 1
    g2 = nx.Graph()
    g2.add_nodes_from(nodes)
    g2.add_edges_from(edges_g2)
    return g2





def generate_1_seed_layer(orig_graph,graphs_seed,dd,Params):
    '''
    generate a single graph_seed given the previous graphs
    '''
    nodes = list(graphs_seed[0].nodes())
    ETNS = count_ETN(orig_graph,dd) # extract ETNS from the entire original graph
    diz = get_dict(ETNS,dd)
    new_g = generate_next_layer(nodes,graphs_seed,diz,dd,Params) 
    graphs_seed.append(new_g)
    return graphs_seed


def generate_seed_graph(orig_graph,g0,d,Params):
    '''
    generate d graph seed given g0
    '''
    graphs_seed = [g0]
    global nb_nodes
    nb_nodes = len(list(g0.nodes()))
    if Params['memory'] == True:
        global mem_all
        for s in range(len(mem_all)):
            mem_all[s] = np.full((nb_nodes,nb_nodes),0) # set the correct size of memory matrices
        for edge in g0.edges(data=False): # start to fill first matrix
            mem_all[Params['state']][edge] += 1
            mem_all[Params['state']][edge[::-1]] += 1
    for i in range(d-1):
        graphs_seed = generate_1_seed_layer(orig_graph,graphs_seed,i+1,Params)
    return graphs_seed
