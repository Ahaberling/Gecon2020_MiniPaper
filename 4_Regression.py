# import datetime as datetime
# import snap

import statsmodels.api as sm
import numpy as np
import pandas as pd
import datetime as datetime
import sys
import xlwt
import scipy.stats as stats

import matplotlib.pyplot as plt
import warnings


##########################
###---Initialization---###
##########################

warnings.simplefilter(action='ignore', category=FutureWarning)
np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 10000)
pd.options.mode.chained_assignment = None

path_data_og = "D:/..."
path_data_mp = "D:/..."
path_plot = "D:/..."
path_reg_result = "D:/..."


pInfo   = pd.read_csv(path_data_og+"PatientInfo.csv")
policy   = pd.read_csv(path_data_og+"Policy.csv")

characteristics_df = pd.read_csv(path_data_mp+"characteristics_df.csv")

'''
x = characteristics_df['day']                                  
y = characteristics_df['avg_diameter']
plt.plot_date(x, y, '-k')
plt.xticks(rotation=20)
plt.xticks(np.arange(0,90,10))
#plt.errorbar(x, y, e, linestyle='None', marker='^')
plt.xlabel('Time')
plt.ylabel('Average Chain Diameter')
#plt.title('Change of Average Chain Diameter over time')
plt.savefig(path_plot+"Overleaf_AvgDiameter.png")
plt.show()
plt.close()

print(characteristics_df['day'])

x = characteristics_df['day']                                  
y = characteristics_df['max_diameter']
plt.plot_date(x, y, '-k')
plt.xticks(rotation=20)
plt.xticks(np.arange(0,90,10))
#plt.errorbar(x, y, e, linestyle='None', marker='^')
plt.xlabel('Time')
plt.ylabel('Max Chain Diameter')
#plt.title('Change of Average Chain Diameter over time')
plt.savefig(path_plot+"Overleaf_MaxDiameter.png")
#plt.show()
plt.close()

x = characteristics_df['day']                                  
y = characteristics_df['median_diameter']
plt.plot_date(x, y, '-k')
plt.xticks(rotation=20)
plt.xticks(np.arange(0,90,10))
#plt.errorbar(x, y, e, linestyle='None', marker='^')
plt.xlabel('Time')
plt.ylabel('Median Chain Diameter')
#plt.title('Change of Average Chain Diameter over time')
plt.savefig(path_plot+"Overleaf_MedianDiameter.png")
#plt.show()
plt.close()

x = characteristics_df['day']                                  
y = characteristics_df['number_of_components']
plt.plot_date(x, y, '-k')
plt.xticks(rotation=20)
plt.xticks(np.arange(0,90,10))
plt.xlabel('Time')
plt.ylabel('Number of Components')
#plt.title('Change of Average Chain Diameter over time')
plt.savefig(path_plot+"Overleaf_no.Components_cor.png")
#plt.show()
plt.close()
'''

characteristics_df['number_of_components_norm'] = characteristics_df['number_of_components'] / max(characteristics_df['number_of_components'])
characteristics_df['avg_diameter_norm'] = characteristics_df['avg_diameter'] / max(characteristics_df['avg_diameter'])
characteristics_df['avg_diameter_normXnumber_of_components_norm'] = characteristics_df['number_of_components_norm'] * characteristics_df['avg_diameter_norm']

'''
x = characteristics_df['day']                                  # Plotting with line for expected diameter increase?
y = characteristics_df['avg_diameter_normXnumber_of_components_norm']
plt.plot_date(x, y, '-k')
plt.xticks(rotation=20)
plt.xticks(np.arange(0,90,10))
#plt.errorbar(x, y, e, linestyle='None', marker='^')
plt.xlabel('Time')
plt.ylabel('AvgDiameterNormXnumberComponentsNorm')
#plt.title('Change of Average Chain Diameter over time')
plt.savefig(path_plot+"Overleaf_AvgDiameterNormXnumberComponentsNorm.png")
#plt.show()
plt.close()

'''


##################################
###---Imputing missing Dates---###
##################################

characteristics_df['day_ord'] = pd.to_datetime(characteristics_df['day']).apply(lambda date: date.toordinal())

#print('Dates between first and last confirmed case: ', max(characteristics_df['day_ord'])-min(characteristics_df['day_ord']))
#print('Dates missing in data: ', (max(characteristics_df['day_ord'])-min(characteristics_df['day_ord']))-len(characteristics_df))

characteristics_df.index = pd.DatetimeIndex(characteristics_df['day']).floor('D')
characteristics_df = characteristics_df.loc[:, ~characteristics_df.columns.str.contains('^Unnamed')]
characteristics_df = characteristics_df.asfreq('D')

number_of_components_list = []
avg_diameter_list = []
avg_size_list = []
max_diameter_list = []
median_diameter_list = []
number_of_components_norm_list = []
avg_diameter_norm_list = []
avg_diameter_normXnumber_of_components_norm_list = []
#avg_diameter_norm_list = []
#avg_size_norm_list = []

for i, d in zip(range(len(characteristics_df)), characteristics_df.index):

    if pd.isna(characteristics_df['day'][d]) == True:
        characteristics_df['day'][d] = d.date()

    if pd.isna(characteristics_df['number_of_components'][i]) == False:
        number_of_components_list.append(characteristics_df['number_of_components'][i])
    else:
        characteristics_df['number_of_components'][i] = number_of_components_list[-1]


    if pd.isna(characteristics_df['avg_diameter'][i]) == False:
        avg_diameter_list.append(characteristics_df['avg_diameter'][i])
    else:
        characteristics_df['avg_diameter'][i] = avg_diameter_list[-1]

    if pd.isna(characteristics_df['max_diameter'][i]) == False:
        max_diameter_list.append(characteristics_df['max_diameter'][i])
    else:
        characteristics_df['max_diameter'][i] = max_diameter_list[-1]

    if pd.isna(characteristics_df['median_diameter'][i]) == False:
        median_diameter_list.append(characteristics_df['median_diameter'][i])
    else:
        characteristics_df['median_diameter'][i] = median_diameter_list[-1]


    if pd.isna(characteristics_df['avg_size'][i]) == False:
        avg_size_list.append(characteristics_df['avg_size'][i])
    else:
        characteristics_df['avg_size'][i] = avg_size_list[-1]

    if pd.isna(characteristics_df['number_of_components_norm'][i]) == False:
        number_of_components_norm_list.append(characteristics_df['number_of_components_norm'][i])
    else:
        characteristics_df['number_of_components_norm'][i] = number_of_components_norm_list[-1]

    if pd.isna(characteristics_df['avg_diameter_norm'][i]) == False:
        avg_diameter_norm_list.append(characteristics_df['avg_diameter_norm'][i])
    else:
        characteristics_df['avg_diameter_norm'][i] = avg_diameter_norm_list[-1]

    if pd.isna(characteristics_df['avg_diameter_normXnumber_of_components_norm'][i]) == False:
        avg_diameter_normXnumber_of_components_norm_list.append(characteristics_df['avg_diameter_normXnumber_of_components_norm'][i])
    else:
        characteristics_df['avg_diameter_normXnumber_of_components_norm'][i] = avg_diameter_normXnumber_of_components_norm_list[-1]


    '''
    if pd.isna(characteristics_df['avg_diameter_norm'][i]) == False:
        avg_diameter_norm_list.append(characteristics_df['avg_diameter_norm'][i])
    else:
        characteristics_df['avg_diameter_norm'][i] = avg_diameter_norm_list[-1]


    if pd.isna(characteristics_df['avg_size_norm'][i]) == False:
        avg_size_norm_list.append(characteristics_df['avg_size_norm'][i])
    else:
        characteristics_df['avg_size_norm'][i] = avg_size_norm_list[-1]
    '''


characteristics_df['day'] = pd.to_datetime(characteristics_df['day'], yearfirst=True)


'''
print('mean: ', characteristics_df['avg_diameter'].mean())
print('max: ', characteristics_df['avg_diameter'].max())
print('min: ', characteristics_df['avg_diameter'].min())
print('var: ', np.var(characteristics_df['avg_diameter']))
print('std: ', np.std(characteristics_df['avg_diameter']))
print('median: ', np.median(characteristics_df['avg_diameter']))
print('mode: ', stats.mode(characteristics_df['avg_diameter'])[0])
'''

x = characteristics_df['day']                                  
y = characteristics_df['avg_diameter']
fig, ax = plt.subplots()
ax.plot(x, y, '-k')
ax.xaxis_date()
#ax.set_title('Simple plot')
plt.xticks(rotation=20)
#plt.xticks(np.arange(0,90,10))
plt.xlabel('Time')
plt.ylabel('Average Chain Diameter')
plt.savefig(path_plot+"Overleaf_AvgDiameter_corr.png")
#plt.show()
plt.close()

x = characteristics_df['day']                                  
y = characteristics_df['number_of_components']
fig, ax = plt.subplots()
ax.plot(x, y, '-k')
ax.xaxis_date()
#ax.set_title('Simple plot')
plt.xticks(rotation=20)
#plt.xticks(np.arange(0,90,10))
plt.xlabel('Time')
plt.ylabel('Number of Components')
plt.savefig(path_plot+"Overleaf_noComponents_corr.png")
plt.show()
plt.close()

'''
x = characteristics_df['day']                                  
y = characteristics_df['number_of_components']
plt.plot_date(x, y, '-k')
plt.xticks(rotation=20)
plt.xticks(np.arange(0,90,10))
plt.xlabel('Time')
plt.ylabel('Number of Components')
#plt.title('Change of Average Chain Diameter over time')
plt.savefig(path_plot+"Overleaf_noComponents_corr.png")
#plt.show()
plt.close()
'''

#characteristics_df['day'] = pd.to_datetime(characteristics_df['day'], yearfirst=True)


# Regression cut after row 81 / day 2020-04-12

characteristics_df_cut = characteristics_df.iloc[0:78,:]

#################################
###---Preparing Policy data---###
#################################

#--- Imputing end date to today

policy['start_date'] = pd.to_datetime(policy['start_date'], yearfirst=True)
policy['end_date'] = policy['end_date'].fillna(datetime.date.today())
policy['end_date'] = pd.to_datetime(policy['end_date'], yearfirst=True)
policy['detail'] = policy['detail'].fillna(policy['gov_policy'])
policy['name'] = policy['gov_policy'] + policy['detail']

policy['name'][0] = 'alert_level_1'
policy['name'][1] = 'alert_level_2'
policy['name'][2] = 'alert_level_3'
policy['name'][3] = 'alert_level_4'
policy['name'][4] = 'immig_China'
policy['name'][5] = 'immig_HongKong'
policy['name'][6] = 'immig_Macau'
policy['name'][7] = 'immig_Japan'
policy['name'][8] = 'immig_Italy'
policy['name'][9] = 'immig_Iran'
policy['name'][10] = 'immig_France'
policy['name'][11] = 'immig_Germany'
policy['name'][12] = 'immig_Spain'
policy['name'][13] = 'immig_UK'
policy['name'][14] = 'immig_Netherlands'
policy['name'][15] = 'immig_Europe'
policy['name'][16] = 'immig_all'
policy['name'][17] = 'quarantine_14days_all'
policy['name'][18] = 'quarantine_and_test_US'
policy['name'][19] = 'kit_Authorization_1'
policy['name'][20] = 'kit_Authorization_2'
policy['name'][21] = 'kit_Authorization_3'
policy['name'][22] = 'kit_Authorization_4'
policy['name'][23] = 'kit_Authorization_5'
policy['name'][24] = 'DT_Screening_local'
policy['name'][25] = 'DT_Screening_standard'
policy['name'][26] = 'mask_public_sale'
policy['name'][27] = 'mask_public_rotation'
policy['name'][28] = 'distancing_strong_1'
policy['name'][29] = 'distancing_strong_2'
policy['name'][30] = 'distancing_weak'
policy['name'][31] = 'cheer_campaigne'
policy['name'][32] = 'school_closure_daycare'
policy['name'][33] = 'school_delay_kinder'
policy['name'][34] = 'school_delay_high'
policy['name'][35] = 'school_delay_middle'
policy['name'][36] = 'school_delay_elementary'
policy['name'][37] = 'school_online_high3'
policy['name'][38] = 'school_online_high2'
policy['name'][39] = 'school_online_high1'
policy['name'][40] = 'school_online_middle3'
policy['name'][41] = 'school_online_middle2'
policy['name'][42] = 'school_online_middle1'
policy['name'][43] = 'school_online_elementary5-6'
policy['name'][44] = 'school_online_elementary4'
policy['name'][45] = 'school_online_elementary3'
policy['name'][46] = 'school_online_elementary1-2'
policy['name'][47] = 'open_data_patient'
policy['name'][48] = 'open_api_mask'
policy['name'][49] = 'app_diagnosis'
policy['name'][50] = 'app_quarantine_protection'
policy['name'][51] = 'surveillance_violators'
policy['name'][52] = 'closure_bars_clubs'


###########################################
###---Preparing Policy Flags (beta S)---###
###########################################

dic_policy = {}
for i in range(len(policy['gov_policy'])):
    policy_name = policy['name'][i]
    dic_policy[policy_name] = (policy['start_date'][i],policy['end_date'][i])

for key, value in dic_policy.items():
    characteristics_df_cut[key] = 99

for i in range(len(characteristics_df_cut)):
    day = pd.to_datetime(characteristics_df_cut['day'][i], yearfirst=True)

    for key, tuple in dic_policy.items():

        if ((day >= tuple[0]) & (day <= tuple[1])):
            characteristics_df_cut[key][i] = 1
        else:
            characteristics_df_cut[key][i] = 0


###############################################
###---Preparing Lag of dependent Variable---###
###############################################


characteristics_df_cut = characteristics_df_cut.rename(columns={'day': 'day_col'})

characteristics_df_cut['day_col'] = pd.to_datetime(characteristics_df_cut['day_col'])
#characteristics_df_cut['day_delay'] = pd.to_datetime(characteristics_df_cut['day_col']) + datetime.timedelta(days=5)
characteristics_df_cut['day_delay'] = pd.to_datetime(characteristics_df_cut['day_col']) + datetime.timedelta(days=14)


merg_slice = characteristics_df_cut[['day_col', 'avg_diameter', 'max_diameter', 'avg_diameter_normXnumber_of_components_norm']]
#merg_slice = characteristics_df_cut[['day_col', 'avg_diameter']]

characteristics_df_cut = characteristics_df_cut.merge(merg_slice, how='left', left_on='day_delay', right_on='day_col', suffixes=('', '_delay'))

pd.DataFrame(characteristics_df_cut).to_csv(path_data_mp+ "final_df.csv")


######################
###---Beta not s---###
######################

characteristics_df_cut['policy_sum'] = 0


for i in range(len(characteristics_df_cut)):
    number_pol = 0
    #for j in characteristics_df.iloc[: , 7:60].columns:
    #for j in characteristics_df.iloc[: , 5:58].columns:
    for j in characteristics_df_cut.iloc[: , 10:63].columns: # All policies
        if characteristics_df_cut[j][i] == 1:
            number_pol = number_pol+1
    characteristics_df_cut['policy_sum'][i] = number_pol



fig, ax = plt.subplots()
plt.bar(characteristics_df_cut['policy_sum'].index, characteristics_df_cut['policy_sum'], color='grey')
plt.xlabel('day')
plt.ylabel('Number of active non-focal policies (beta_not_s)')
#plt.title('Histogram: Infection Chain Size (log)')
plt.savefig(path_plot+"Cut_distibution_Beta_not_s.png")
#plt.show()
plt.close()

# One vs All reg with sum and avg_diameter
#for i in range(5,57):
for i in range(10,63): # All policies
    #Y = characteristics_df.iloc[0:103, 60:61]
    Y = characteristics_df_cut.iloc[0:64, 65:66]  # avg_diameter_delay
    X = characteristics_df_cut.iloc[0:64, pd.np.r_[i:i+1, 68:69]] # policy_sum
    X = sm.add_constant(X)
    model = sm.OLS(Y, X)
    results = model.fit()
    print(results.summary())

    df = pd.concat((results.params, results.pvalues), axis=1)
    df.rename(columns={0: 'beta', 1: 't'}).to_excel(path_reg_result + 'Reg_result' + str(i) + '.xls', 'sheet1')


'''

# One vs All reg with sum and max_diameter
#for i in range(5,57):
for i in range(10,63):
    #Y = characteristics_df.iloc[0:103, 60:61] 
    Y = characteristics_df.iloc[0:103, 66:67]  # max_diameter_delay
    X = characteristics_df.iloc[0:103, pd.np.r_[i:i+1, 68:69]] # policy_sum
    X = sm.add_constant(X)
    model = sm.OLS(Y, X)
    results = model.fit()
    print(results.summary())
    
# One vs All reg with sum and avg_diameter_normXnumber_of_components_norm_delay
#for i in range(5,57):
for i in range(10,63):
    #Y = characteristics_df.iloc[0:103, 60:61]  
    Y = characteristics_df.iloc[0:103, 67:68]  # avg_diameter_normXnumber_of_components_norm_delay
    X = characteristics_df.iloc[0:103, pd.np.r_[i:i+1, 68:69]] # policy_sum
    X = sm.add_constant(X)
    model = sm.OLS(Y, X)
    results = model.fit()
    print(results.summary())
'''