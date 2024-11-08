import numpy as np
import networkx as nx
import random
import json
import csv
import os


class Simplagion_model:


    def __init__(self, edgelist_t, nodes_list):
        '''
        Constructor.

        The method defines the setup for the simulations.

        Parameters
        ----------
        edgelist: dict
            all interactions
            keys: edges, values: strength
        nodes_list: list
            nodes
        '''

        self.nodes_list = nodes_list
        self.edgelist_t = edgelist_t



    def initialize_time0(self,pat0):
        '''
        Initialize the status of the initial infected people and set initial edges weigths at 0.

        '''
        # Initialize patient 0:
        self.pat0 = pat0
        self.Istate = np.full(len(self.nodes_list),0)
        self.Rstate = np.full(len(self.nodes_list),0)
        self.Istate[self.pat0] = 1
        self.R0 = 0





    def simulate(self, beta, mu, t0):
        '''
        Run the simulation.

        Returns
        ----------
        describe...
        '''
        #inf_thresh = 5
        #flag_nb_inf = False

        nb_pat0r = self.Istate.sum()
        nn = 0
        R0 = 0
        t = t0
        NN = 300
        computeR0 = True
        for times in range(10000):
            Sstate = 1 - self.Istate - self.Rstate
            if any(c == -1 for c in Sstate):
                print('error')
                break
            old_susc = list(np.where(Sstate==1)[0])
            old_inf = list(np.where(self.Istate==1)[0])

            for i in old_susc:
                set_old_inf = set(old_inf)
                neighs = [self.edgelist_t[t][ind][n] for ind, edge in enumerate(self.edgelist_t[t]) if i in edge for n in range(2) if self.edgelist_t[t][ind][n]!=i]
                Ineighs = [neigh for neigh in neighs if neigh in set_old_inf]
                p = 1 - (1-beta)**len(Ineighs) # infection probability
                r = np.random.uniform(0, 1)
                if r < p:
                    self.Istate[i] = 1 # infected
                    if computeR0:
                        if self.pat0 in Ineighs:
                            R0 += 1/len(Ineighs)

            if mu != 0:
                for i in old_inf:
                    r = np.random.uniform(0, 1)
                    if r < mu:
                        self.Istate[i] = 0
                        self.Rstate[i] = 1 # recovered
                if computeR0:
                    if self.Rstate[self.pat0] == 1:
                        computeR0 = False # patient 0 has recovered,
                                          # R0 already computed

            if self.Istate.sum() == 0: # all infected have recovered
                Rinf = self.Rstate.sum()
                break

            Sstate = 1 - self.Istate - self.Rstate
            if Sstate.sum() == 0: # no more susceptibles
                print('all infected at t=%d'%t)
                Rinf = len(self.nodes_list)
                break

            if list(np.where(self.Istate==1)[0]) == old_inf:
                nn += 1
            else:
                nn = 0
            if nn == NN: # the results didn't change in the last NN steps, we
                         # assume the process is stucked (usually with one
                         # infected with very few contacts and a low probability
                         # to infect them)
                Rinf = self.Istate.sum() + self.Rstate.sum()
                break

            t += 1
            if t > max(self.edgelist_t.keys()):
                t = 0
                
        return R0, Rinf
