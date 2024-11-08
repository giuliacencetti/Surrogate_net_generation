Code for the article "Generating surrogate temporal networks from mesoscale building blocks" by Giulia Cencetti and Alain Barrat.

To generate the surrogate networks:

1) Choose an original temporal network for which generating the surrogates and put it in shape "t i j", where "t" is the time in seconds at which an interaction takes place and "i,j" are the two nodes involved. Examples already usable are provided in folder `Datasets`.

2) Use *Detect_temporal_states_and_communities.ipynb*, indicating the name of the original network, to detect and save temporal states and communities in the original network. 

3) Use *Find_absent_nodes.ipynb* to find absent nodes in each day (optional).

4) Use *Generate_surrogates.ipynb*, choosing *abs_nodes_flag = True* if step 3) has been performed, *False* if not. 


To analyze the surrogate networks use *Modularity_clustering_nb_int.ipynb* and *Topological_measures.ipynb* to reproduce fig. 2(a) and 2(c) of the article respectively. 
The figures 3 and 4 are obtained by using the code provided by Refs.[17] and [46] respectively.

To simulate the dynamical processes and generate the figures use:

SIR: 
*Simulate_R0_Rinf_simple.ipynb* to simulate,
*Plot_R0_Rinf_distributions.ipynb* to plot the distribution of R0 and Rinfty (fig. 5),
*Plot_R0_Rinf_heatmap.ipynb* to plot the heatmaps (fig. 5).


Deffuant:
*Simulate_Deffuant.ipynb* to simulate,
*Plot_Deffuant.ipynb* to plot the quantities of fig. 6.

Naming game:
*Simulate_NG.ipynb* to simulate,
*Plot_t_conv.ipynb* to plot the convergence time (fig.7 top).
