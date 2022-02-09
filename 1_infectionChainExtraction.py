import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import snap
import sys

from collections import Counter

##########################
###---Initialization---###
##########################

np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 1000)
pd.options.mode.chained_assignment = None

path_og = "D:/..."
path_art = "D:/..."

pInfo   = pd.read_csv(path_og+"PatientInfo.csv")              


############################
###---Data Preparation---###
############################

#--- Cleaning Selfedges in pInfo (No theoretical explanation, malicious data assumed)

pInfo_no_self = pInfo[pInfo['infected_by'] != pInfo['patient_id']]
pInfo_self = pInfo[pInfo['infected_by'] == pInfo['patient_id']]                                                         
pInfo_self.loc[:,'infected_by'] = np.NaN

pInfo = pd.concat([pInfo_no_self,pInfo_self])


#--- DataFrame with all valid nodes (pInfo_all)

pInfo_infect_valid = pInfo[pInfo['infected_by'].isin(pInfo['patient_id'])]
pInfo_infect_rest = pInfo[~pInfo['infected_by'].isin(pInfo['patient_id'])]

pInfo_infect_invalid = pInfo_infect_rest.dropna(subset=['infected_by'])                                                 
pInfo_infect_invalid.loc[:,'infected_by'] = np.NaN                                                                      # Replacing invalid infections with NaNs

pInfo_infect_no = pInfo_infect_rest[pInfo_infect_rest['infected_by'].isna()]

reconst = pd.concat([pInfo_infect_invalid,pInfo_infect_no])                                                             # Reconstructing the original dataFrame
pInfo_all = pd.concat([reconst,pInfo_infect_valid])


#--- DataFrame with all explicit connected nodes (pInfo_dir)

u1 = pInfo_all[pInfo_all['infected_by'].notna()]                                                                        # Create first part of the union
join = pInfo_all.merge(pInfo_all, how='inner', left_on='infected_by', right_on='patient_id', suffixes=('_x', ''))       # Merge command to create second part of the union
u2 = join.iloc[:, 18:36]                                                                                                # Reduce merge to relevant columns

pInfo_dir = pd.concat([u1, u2]).drop_duplicates()                                                                       # Dropping duplicates

print(pInfo['province'].value_counts())


################################
###---Graph Initialization---###
################################


shorten_id = lambda x: int(str(x)[0:5]+str(x)[6:10])                                                                    # Original Ids are larger then the integer max ///
original_id = lambda x: int(str(x)[0:5] + str(0) + str(x)[5:9])                                                         # value. Snap.Addnode() only works with integer.
                                                                                                                        # Solution for now: simply reducing the integer by ///
                                                                                                                        # factor 10 (no relevant id information in this ///
                                                                                                                        # neglected position, all 0)
'''
#--- Graph with all valid nodes (G_all)

pInfo_all_reduced = pInfo_all.loc[:, ['patient_id','infected_by']]                                                      # Reduced DataFrame sufficient for Graph creation
pInfo_all_reduced = pInfo_all_reduced.sort_values(by='patient_id')

G_all = snap.TNGraph.New()

for i in pInfo_all_reduced['patient_id']:
    G_all.AddNode(shorten_id(i))                                                                                        
print('number of nodes added to G_all: \n', G_all.GetNodes())

for i, j in pInfo_all_reduced.itertuples(index=False):
    if pd.isna(j) == False:
        G_all.AddEdge(shorten_id(j), shorten_id(i))
print('number of edges added to G_all: \n', G_all.GetEdges())
'''

#--- Graph with all explicit connected nodes (G_dir)

pInfo_dir_reduced = pInfo_dir.loc[:, ['patient_id','infected_by']]                                                      # Reduced DataFrame sufficient for Graph creation
pInfo_dir_reduced = pInfo_dir_reduced.sort_values(by='patient_id')

G_dir = snap.TNGraph.New()
x = 0

for i in pInfo_dir_reduced['patient_id']:
    G_dir.AddNode(shorten_id(i))
    x = x + 1

print('number of nodes added to G_dir: \n', G_dir.GetNodes())

for i, j in pInfo_dir_reduced.itertuples(index=False):
    if pd.isna(j) == False:
        G_dir.AddEdge(shorten_id(j), shorten_id(i))
        #print(shorten_id(j), shorten_id(i))
print('number of edges added to G_dir: \n', G_dir.GetEdges())

###############################
###---Graph Visualization---###
###############################

'''
#--- Visualization of G_all
snap.DrawGViz(G_all, snap.gvlDot, "G-all.png", "Graph with all \'valid\' nodes (G_all)")
snap.PlotInDegDistr(G_all, "G_all", "G-all - in-degree Distribution")
snap.PlotOutDegDistr(G_all, "G_all", "G-all - out-degree Distribution")
'''
#--- Visualization of G_dir
snap.DrawGViz(G_dir, snap.gvlDot, "G_dir.png", "Graph with explicit all connected nodes (G_dir)")

'''
snap.PlotOutDegDistr(G_dir, "G_dir", "G-dir - out-degree Distribution", False, False)
snap.PlotOutDegDistr(G_dir, "G_dir_ccdf", "G-dir - out-degree Distribution (Complementary Cummulative distribution function)", True, False)                       # Plots Complementary Cummulative distribution function
snap.PlotOutDegDistr(G_dir, "G_dir_pl", "G-dir - out-degree Distribution (Power-Law)", False, True)                       # Plots with fitted power law
snap.PlotOutDegDistr(G_dir, "G_dir_ccdf_pl", "G-dir - out-degree Distribution", True, True)                               # Plots both
'''

'''
#--- Visualization of G_deg
snap.DrawGViz(G_deg, snap.gvlDot, "G_deg.png", "Graph ... (G-deg)")
snap.PlotInDegDistr(G_deg, "G_deg", "G-deg - in-degree Distribution")
snap.PlotOutDegDistr(G_deg, "G_deg", "G-deg - out-degree Distribution")
'''


############################
###---Network Measures---###
############################

#--- avg outdegree

list_outDegree = []
outDegVec = snap.TIntPrV()
snap.GetNodeOutDegV(G_dir, outDegVec)

for p in outDegVec:
    list_outDegree.append(p.GetVal2())

print('Nde outdegrees \t', list_outDegree)
print('Avg OutDegree \t', sum(list_outDegree)/G_dir.GetNodes())


#--- density

# density for directed
density_dir = (G_dir.GetEdges())/(G_dir.GetNodes() * (G_dir.GetNodes() - 1))
print('density directed: ', density_dir)

# density for undirected
density_undir = (2 * G_dir.GetEdges())/(G_dir.GetNodes() * (G_dir.GetNodes() - 1))
print('density undirected: ',density_undir)



###############################################
###---Extracting componen characteristics---###
###############################################

#--- Number of components, their size distribution and avg component size

compSize_cat = []                                                           # Categories of component size
compSize_catCount = []                                                      # Component size distribution
intIntVec = snap.TIntPrV()                                                  # TIntPrV = vector of (integer, integer) pairs
snap.GetWccSzCnt(G_dir, intIntVec)                                          # GetWccSzCnt = extract distribution of connected components (component size, count)

for p in intIntVec:
    compSize_cat.append(p.GetVal1())
    compSize_catCount.append(p.GetVal2())

print('Size categories  of components \t\t\t', compSize_cat)
print('Size categories count  of components \t', compSize_catCount)
print('Number of components: ', sum(compSize_catCount))
print('Avg components size: ', G_dir.GetNodes() / sum(compSize_catCount))


#--- Extract components as (sub)graphs to extract component characteristics

compVec = snap.TCnComV()                                                                            # Vector of all weakly-connected components. Each component consists of a TIntV vector of node ids
snap.GetWccs(G_dir, compVec)                                                                        # Returns all weakly connected components in Graph
subgraphs={}

for i in range(len(compVec)):
    subgraphs['G_dir_sub_{0}'.format(i)] = snap.TNGraph.New()
    for k in compVec[i]:
        subgraphs['G_dir_sub_{0}'.format(i)].AddNode(k)
    for x, y in pInfo_dir_reduced.itertuples(index=False):
        if pd.isna(y) == False:
            if shorten_id(y) in (compVec[i]):
                if shorten_id(x) in (compVec[i]):
                    subgraphs['G_dir_sub_{0}'.format(i)].AddEdge(shorten_id(y), shorten_id(x))

#--- Extract component characteristics: diameter, size

compDia = []
compSize= []

for key in subgraphs:
    compDia.append(snap.GetBfsFullDiam(subgraphs[key], 100, True))                                                     
    compSize.append(subgraphs[key].GetNodes())
print('Diameter of components', compDia)
print('Avg. diameter: ', sum(compDia) / len(compDia))
print('Component size: ', compSize)

#--- Transform subgraphs dictionary of components to an array (To later enrich it with component characteristics, convert it and append it to original dataFrame pInfo_dir)

comp_array = np.array([[],[]])                                                                  # First position is a list of all component IDs. Second position is a list of nodes present in the component with the respective ID
compID = 0                                                                                      # Initialization of the counter
nodeID_list = []

for component in compVec:                                                                       # 'compVec = snap.TCnComV()' consists of a TIntV vector of node ids
    for nodeID in component:
        nodeID_list = np.append(nodeID_list, nodeID)
    comp_array = np.append(comp_array, [[compID], [nodeID_list]], axis=1)
    nodeID_list = []
    compID = compID + 1

#--- Enriching the array with component characteristics
                                                                                                                # compRich_array[0] component id
compRich_array = np.append([comp_array[0]], [compSize], axis=0)                                                 # compRich_array[1] component size
compRich_array = np.append(compRich_array, [compDia], axis=0)                                                   # compRich_array[2] component diameter
compRich_array = np.append(compRich_array, [comp_array[1]], axis=0)                                             # compRich_array[3] id list of all component
#print(compRich_array)                                                                                          # compRich_array[3][x] id list of x-st component
                                                                                                                # compRich_array[3][x][y]if of y-st node in x-component

#--- Transforming the enriched component array (compRich_array) (indexed by component id), to an array indexed by node id (preparation to later append it to pInfo_dir)

nodeRich_array = np.array([[],[],[],[]])                                                                                
counter = 0

for component in compRich_array[3]:
    for nodeID in component:
        nodeRich_array = np.append(nodeRich_array, [[nodeID],[compRich_array[0][counter]],[compRich_array[1][counter]],[compRich_array[2][counter]]], axis=1)
    counter = counter + 1

#--- Reconstructig the pruned 'patient_id' integer

for i in range(len(nodeRich_array[0])):
    nodeRich_array[0][i] = original_id(nodeRich_array[0][i])

#--- Merging component characteristics to pInfo_dir

preMergeFrame = pd.DataFrame({'node_id': nodeRich_array[0, :], 'component_id': nodeRich_array[1, :], 'component_size': nodeRich_array[2, :], 'component_diameter': nodeRich_array[3, :]})
pInfo_dir_rich = pInfo_dir.merge(preMergeFrame, how='inner', left_on='patient_id', right_on='node_id')
pInfo_dir_rich = pInfo_dir_rich.drop(['node_id'], axis=1)

pInfo_dir_rich.to_csv(path_art+'pInfo_rich.csv')

#Todo enrich with more component characteristics


#--- Visualization of component size distribution and characteristics

print('Size categories  of components \t\t\t', compSize_cat)
print('Size categories count  of components \t', compSize_catCount)

print('Diameter of components list ', compDia)

print('max diameter', max(compDia))
print('min diameter', min(compDia))
print('mean diameter', sum(compDia)/len(compDia))
print('variance diameter', np.var(compDia))
print('standard deviation diameter', np.std(compDia))
print('median diameter', np.median(compDia))
print('mode diameter', max(set(compDia), key=compDia.count))


print('Diameter distribution', Counter(compDia))


plt.hist(compDia, color='grey')
plt.xlabel('Infection Chain Diameter')
plt.ylabel('Frequency')
#plt.title('Histogram: Infection Chain Diameter')
plt.savefig("Overleaf_hist_compDia.png")
#plt.show()
plt.close()

fig, ax = plt.subplots()
plt.bar(compSize_catCount, compSize_cat, color='grey')
ax.set_yscale('log')
ax.set_xscale('log')
plt.xlabel('Infection Chain Size (log)')
plt.ylabel('Frequency (log)')
#plt.title('Histogram: Infection Chain Size (log)')
plt.savefig("Overleaf_hist_compsize_log.png")
#plt.show()
plt.close()
