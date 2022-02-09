# import os
# import math
# import snap
# import seaborn as sns
# import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
import sys




##########################
###---Initialization---###
##########################

np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 10000)
pd.options.mode.chained_assignment = None


path_og = "D:/..."
path_art = "D:/..."

pInfo_rich = pd.read_csv(path_art+"pInfo_rich.csv", index_col=0)


################################################
###---Enriching with time related features---###
################################################

pInfo_rich['confirmed_date'] = pd.to_datetime(pInfo_rich['confirmed_date'], yearfirst=True)

print('last confirmation: ', max(pInfo_rich['confirmed_date']))
print('first confirmation: ', min(pInfo_rich['confirmed_date']))
print('Total timespan: ', max(pInfo_rich['confirmed_date']) - min(pInfo_rich['confirmed_date']))


#--- Enrich with columns of first and last component specific confirmation

pInfo_rich_reduc = pInfo_rich[['confirmed_date', 'component_id']]
group_min = pInfo_rich_reduc.groupby(['component_id']).min()
group_max = pInfo_rich_reduc.groupby(['component_id']).max()
pInfo_rich2 = pInfo_rich.merge(group_min, how='inner', left_on='component_id', right_on='component_id',suffixes=('', '_min'))
pInfo_rich2 = pInfo_rich2.merge(group_max, how='inner', left_on='component_id', right_on='component_id',suffixes=('', '_max'))

#--- Enrich with columns of days between first and last confirmation component specific (and a normalized measure)

pInfo_rich2['time_span'] = (pInfo_rich2['confirmed_date_max'] - pInfo_rich2['confirmed_date_min']).dt.days  
pInfo_rich2['time_span_norm'] = pInfo_rich2['time_span'] / pInfo_rich2['component_diameter']

pInfo_rich2['time_span_h'] = pInfo_rich2['time_span'] * 24                                                              # Information release by the gouvernment changed at one point from ///
#pInfo_rich2['time_span_h_norm'] = pInfo_rich2['time_span_h'] / pInfo_rich2['component_diameter']                       # 16 to 0 o'clock.
pInfo_rich2['time_span_h_norm2'] = pInfo_rich2['time_span_norm'] * 24                                                   

#--- Plot Timespan distribution on camponent level
timeSpan = pInfo_rich2[['component_id','time_span']].drop_duplicates(subset=['component_id'])

pInfo_rich2.to_csv(path_art+'pInfo_rich2.csv')

plt.hist(timeSpan['time_span'], color='grey', bins=range(1,61))
plt.xlabel('Life Time of Components in days')
plt.ylabel('Frequency')
#plt.title('Histogram:')
plt.savefig("Overleaf_hist_compLife.png")
plt.show()
plt.close()

#print(len(timeSpan['time_span']))
print(timeSpan['time_span'].value_counts())


print('Average Timespan on Component level', sum(timeSpan['time_span'])/len(timeSpan['time_span']))
