import numpy as np
import pandas as pd
import snap
import sys


##########################
###---Initialization---###
##########################

np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_columns', 30)
pd.options.mode.chained_assignment = None

path_data_og = "D:/..."
path_data_mp = "D:/..."

#pInfo   = pd.read_csv(path_data_og+"PatientInfo.csv")
pInfo   = pd.read_csv(path_data_mp+"pInfo_rich2.csv")

print(pInfo.shape)


##########################
###---Data Cleansing---###
##########################

#--- Cleaning Selfedges in pInfo (No theoretical explanation, malicious data assumed)

pInfo_no_self = pInfo[pInfo['infected_by'] != pInfo['patient_id']]
pInfo_self = pInfo[pInfo['infected_by'] == pInfo['patient_id']]
pInfo_self.loc[:,'infected_by'] = np.NaN
pInfo = pd.concat([pInfo_no_self,pInfo_self])

print(pInfo.shape)

#--- DataFrame with all valid nodes (including isolated)(pInfo_all)
# Cleansing malicious edges

pInfo_infect_valid = pInfo[pInfo['infected_by'].isin(pInfo['patient_id'])]
pInfo_infect_rest = pInfo[~pInfo['infected_by'].isin(pInfo['patient_id'])]

pInfo_infect_invalid = pInfo_infect_rest.dropna(subset=['infected_by'])
pInfo_infect_invalid.loc[:,'infected_by'] = np.NaN

pInfo_infect_no = pInfo_infect_rest[pInfo_infect_rest['infected_by'].isna()]

reconst = pd.concat([pInfo_infect_invalid,pInfo_infect_no])
pInfo_all = pd.concat([reconst,pInfo_infect_valid])

print(pInfo_all.shape)

#--- DataFrame with all explicit connected nodes (excluding isolated)(pInfo_dir)

u1 = pInfo_all[pInfo_all['infected_by'].notna()]
print(u1.shape)

join = pInfo_all.merge(pInfo_all, how='inner', left_on='infected_by', right_on='patient_id', suffixes=('_x', ''))
print(join.shape)
#u2 = join.iloc[:, 18:36]
u2 = join.iloc[:, 28:56]
print(u2.shape)

pInfo_dir = pd.concat([u1, u2]).drop_duplicates()
print(pInfo_dir.shape)
pInfo_dir = pInfo_dir.sort_values(by = 'patient_id',ignore_index = True)

print(pInfo_dir.shape)

#######################################
###---Preparing network extration---###
#######################################

shorten_id = lambda x: int(str(x)[0:5] + str(x)[6:10])  # Original Ids are larger then the integer max ///
original_id = lambda x: int(str(x)[0:5] + str(0) + str(x)[5:9])  # value. Snap.Addnode() only works with integer.

counter = 0
for i in pInfo_dir['patient_id']:
    pInfo_dir['patient_id'][counter] = shorten_id(i)
    counter = counter+1

counter = 0
for i in pInfo_dir['infected_by']:
    if pd.isna(i) == False:
        pInfo_dir['infected_by'][counter] = str(shorten_id(i))
    counter = counter+1



#--- Creating dictionary with pInfo_dir sliced by day

allDates = pInfo_dir['confirmed_date'].drop_duplicates()                                
allDates = allDates.sort_values(ignore_index = True)

dic_pInfo = {}

for i in allDates:
    dic_pInfo['{0}'.format(i)] = pInfo_dir[pInfo_dir['confirmed_date'] <= i]
    #print(len(dic_pInfo['{0}'.format(i)] ))
    #dic_pInfo['{0}'.format(i)] = dic_pInfo['{0}'.format(i)][dic_pInfo['{0}'.format(i)]['confirmed_date_min'] <= i]     // redundent
    #print(len(dic_pInfo['{0}'.format(i)]))
    dic_pInfo['{0}'.format(i)] = dic_pInfo['{0}'.format(i)][i <= dic_pInfo['{0}'.format(i)]['confirmed_date_max']]
    #print(len(dic_pInfo['{0}'.format(i)]))


#--- Initiallize graphs and subgraphs using snap

dic_dayGraphs = {}

for i in allDates:
    added_ids = []

    dic_dayGraphs['{0}'.format(i)] = snap.TNGraph.New()

    for j in dic_pInfo['{0}'.format(i)]['patient_id']:
        if j not in added_ids:
            dic_dayGraphs['{0}'.format(i)].AddNode(j)
        added_ids.append(j)

    for k in dic_pInfo['{0}'.format(i)]['infected_by']:
        if pd.isna(k) == False:
            if k not in added_ids:
                dic_dayGraphs['{0}'.format(i)].AddNode(int(k))
        added_ids.append(k)

    for p, q in dic_pInfo['{0}'.format(i)].loc[:, ['patient_id','infected_by']].itertuples(index=False):
        if pd.isna(q) == False:
            dic_dayGraphs['{0}'.format(i)].AddEdge(int(q), p)


#--- Extract component characteristics

# compVec is of length "number of components". Every position is a list of Node_ids that are present in the graph

dia_df = np.array([[], [], [], [], [], []])  # date / component id / diameter / size / diameter norm / size norm
''', [], []'''

for key in dic_dayGraphs:

    compVec = snap.TCnComV()
    snap.GetWccs(dic_dayGraphs[key], compVec)
    subgraphs = {}
    dia_list = []
    size_list = []

    for i in range(len(compVec)):
        subgraphs['subGraph_{0}'.format(i)] = snap.TNGraph.New()
        for k in compVec[i]:
            subgraphs['subGraph_{0}'.format(i)].AddNode(k)

        for k in compVec[i]:
            source_node = dic_pInfo['{0}'.format(key)][dic_pInfo['{0}'.format(key)]['patient_id'] == k][
                'infected_by'].values
            print(source_node)                                      # Dont comment out this print, it wont work without, whyever
            if pd.isna(source_node) == False:
                subgraphs['subGraph_{0}'.format(i)].AddEdge(int(source_node), k)

        dia_list.append(snap.GetBfsFullDiam(subgraphs['subGraph_{0}'.format(i)], 100, True))
        size_list.append(subgraphs['subGraph_{0}'.format(i)].GetNodes())

    dia_avg = sum(dia_list) / len(dia_list)
    #if len(list(filter(lambda a: a != 0, dia_list))) != 0:
        #dia_avg_norm = sum(dia_list) / len(list(filter(lambda a: a != 0, dia_list)))
    #else:
        #dia_avg_norm = 0

    dia_max = max(dia_list)

    dia_median = np.median(dia_list)

    size_avg = sum(size_list) / len(size_list)
    #if len(list(filter(lambda a: a != 0, size_list))) != 0:
        #size_avg_norm = sum(size_list) / len(list(filter(lambda a: a != 0, size_list)))
    #else:
        #size_avg_norm = 0


    dia_df = np.append(dia_df, [[key], [i], [dia_avg], [dia_max], [dia_median], [size_avg]], axis=1)
    ''', [dia_avg_norm], [size_avg_norm]'''


#--- Save Characteristics 

characteristics_df = pd.DataFrame({'day': dia_df[0, :], 'number_of_components': dia_df[1 , :], 'avg_diameter': dia_df[2 , :], 'max_diameter': dia_df[3 , :], 'median_diameter': dia_df[4 , :], 'avg_size': dia_df[5 , :] })
''', 'avg_diameter_norm': dia_df[4 , :], 'avg_size_norm': dia_df[5 , :]'''

pd.DataFrame(characteristics_df).to_csv(path_data_mp+ "characteristics_df.csv")