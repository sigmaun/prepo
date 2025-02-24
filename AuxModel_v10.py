#!/usr/bin/env python
# coding: utf-8

# # Brief documentation notes
# This code computes the net marginal savings function for a set of candidate items for prepo. Input values are collected, marginal savings functions are computed and plotted, and results are saved to a file.
# ## Assumptions
# - Time between disasters is exponentially distributed (this can easily be changed to any other preferred distribution)
# - The ratio of local-to-prepo cost is a truncated normal random variable
# - Demand is a normal random variable with a mean that (linearly) depends on local-to-prepo cost
# - Local supply is a composite discrete/continuous random variable: takes on a value of 0 with a specified probability $Q_0$ and is a normal random variable with probability $1 - Q_0$. In the event that it is a normal random variable, its mean (linearly) depends on local-to-prepo cost. 
# 
# 
# ## Notation
# ### Data imported from Excel file that is saved in 'csv' format
# m_T = average time between disasters (exponential random variable) 
# 
# #### The following data are specific to each item
# h = inventory holding cost per dollar-period<br>
# v = ratio of shortage-to-prepo cost (v > 1)<br>
# c = prepo cost per unit of the item
# 
# $\tilde a$ = random ratio of local-to-prepo cost ratio (truncated normal random variable; realization is without tilde)<br>
# min_a = minimum local-to-prepo cost ratio<br>
# max_a = maximum local-to-prepo cost ratio<br>
# mean_a = mean local-to-prepo cost ratio<br>
# stdev_a = standard deviation of local-to-prepo cost ratio
# 
# #### The  demand and local supply parameters below are in the same unit as the unit cost parameter c (eg, if c is cost per kg, then demand and supply parameters are in kgs) 
# m_D = base mean demand<br>
# a_D = coefficient on  local-to-prepo cost ratio for demand<br>
# stdev_D = standard deviation of demand for fixed value of local-to-prepo cost ratio<br>
# $\tilde z_D$ = standard normal random variable associated with demand <br>
# $\tilde D$ = m_D + a_D$\tilde a$ + stdev_D$\tilde z_D$<br>
# 
# Q_0 = probability that local supply is zero<br>
# m_Q = base mean local supply (given not zero)<br>
# a_Q = coefficient on  local-to-prepo cost ratio for local supply (given not zero)<br>
# stdev_Q = standard deviation of local supply (given not zero) for fixed value of local-to-prepo cost ratio<br>
# $\tilde z_Q$ = standard normal random variable associated with local supply <br>
# $\tilde Q$ = 0 w.p. Q_0 (i.e., the probability there is no local supply is Q0) <br>
# $\tilde Q$ = m_Q + a_Q$\tilde a$ + stdev_Q$\tilde z_Q$ w.p. 1- Q_0 
# 
# rho = Pearson correlation coefficient for $(\tilde z_D,\tilde z_Q)$<br>
# 
# ### Data to control the plot functions
# 
# min_x = minimum value of prepo investment in an item (assumed integer)<br>
# max_x =  maximum value of prepo investment in an item (assumed integer)<br>
# incr_x = step size for prepo investment (assumed integer)<br>
# n =  sample size for computuations (assumed integer)<br>
# seed = True or False to indicate whether (True) or not (False) the same intial random number seed should be used for each sample
# 
# 
# # Computations
# 
# We compute the marginal savings, marginal cost, and net marginal savings as a function of prepo spend x. Toward this end, we will use 4 random variables:
# 
# P_a = $(\tilde{a} - 1)^+$<br>
# P_D = $\bar{F}_D(x | \tilde{a})$<br>
# P_S = $\bar{F}_{D-Q}(x | \tilde{a})$<br>
# P_cx =$\left[(\tilde{a} - 1)^+\right]  \times \left[\left(\bar{F}_D(x | \tilde{a})- \bar{F}_{D-Q}(x | \tilde{a})\right)\right]$
# 
# The relevant functions are computed as follows:
# 
# m_s(x) = (v - 1)E[P_a] + E[P_cx]<br>
# m_c = h $\times$ m_T<br>
# m(x) = m_s(x) - m_c

# # Input data
# ![image.png](data:image/png;base64,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)

# The above screenshot illustrates the format for the csv input file. The meaning of each column is described below:
# 
# Item: desired name for the item in question
# 
# m_T: average number of periods between relief events.<br>
# - The choice of period (eg, day, month, year) is arbitrary. All that is required is that the same period be used in the specification for all period-based parameters (i.e., m_T and h). Note that there is a single value of m_T (ie, m_T does not vary across items). The code only reads the value of m_T from the first items (WASH in the screenshot above). The values of m_T for the other items are ignored.
# 
# h: prepo inventory holding cost per unit-period.<br>
# - This includes are all relevant costs of holding inventory (eg, obsolencence, holding cost charges, opportunity cost of funds tied up in inventory, etc.). As noted above, the value of h must be based on the same period as the value of m_T.
# 
# v: shortage penalty.<br>
# - This is a measure of urgency or importance of the item during a relief event. It may be interpreted as the cost of human suffering if a unit of the product is not available for someone in need.
# 
# c: prepo cost per unit. The unit cost is an estimate of the total landed cost at the relief event.<br>
# - It includes the purchase cost, transportation cost into the depot (where prepo is stored), and transportation cost to the relief event.
# 
# mean_a: expected value of local-to-prepo cost per unit.<br>
# - For example, if mean_a = 1.01, it means that buying the item from the local market is, on average, 1% more expensive than buying the same item beforehand (i.e., prepo) and shipping it to the area of the relief event.
# 
# stdev_a: standard deviation in local-to-prepo cost per unit.<br>
# 
# min_a: minimum possible value of local-to-prepo cost per unit.<br>
# 
# max_a: maximum possible value of local-to-prepo cost per unit.
# - As noted above, local-to-prepo cost per unit is assumed to be a truncated normal random variable. This means that its value will be between min_a and max_a (i.e., truncation). The probability density function appears like the normal probability density function (with mean = mean_a and standard deviation = stdev_a) except the function takes on a value of zero outside the interval of \[min_a, max_a\] and is inflated (relative to a pure normal density ) on the interval \[min_a, max_a\] (so that the random variable takes on a value within this range with probability 1). As the value of stdev_a increases, the probability distribution becomes closer and closer to a uniform random variable on interval \[min_a, max_a\].
# - The following inquality must hold for the values: min_a $\le$ mean_a $\le$ max_a.
# - As a point of clarification, mean_a is the mean of the normal random variable prior to truncation. If min_a and max_a are the same distance away from mean_a, then mean_a is also the expected value of the truncated normal random value. If mean_a - min_a is more than max_a - mean_a, then the mean of the truncated normal random variable will be below mean_a. Similarly, mean of the truncated normal random variable will be above mean_a if mean_a - min_a is less than max_a - mean_a.
# 
# m_D: intercept of the expected value of demand (or need) for the item during a relief event.
# 
# a_D: coefficient on the realized value of local-to-prepo cost per unit.
# 
# stdev_D: standard deviation of demand (or need) for the item during a relief event.
# - As noted above, demand is assumed to be a normal random variable with mean dependent on the realized value of $\tilde a$ (i.e., the mean of the normal random variable is m_D + a_D $\times \tilde a$. 
# - The value of a_D is used to control the correlation between local-to-prepo cost and demand. Nominally, the value of a_D is either zero (demand and local supply cost are independent) or positive. A positive value of a_D introduces positive correlation between demand and local unit cost. This can arise in practice because local supply is likely to be tight when demand is high, putting upward pressure on local prices.  
# 
# Q_0: probability that there will be no supply of the item.
# - Local supply may be zero from several reasons. First, the item may not be sold in some geographical regions where a relief event could occur. Second, a major disaster could wipe out all local supply, even if available prior to the relief event. Third, management may prefer to not use local supply even when available so that local humanitarian organizations that do not have prepo inventory are able to purchase and distribute local supplies. 
# 
# m_Q: intercept of the expected value of local supply for the item during a relief event, given that it is available (with probability 1 - Q_0).
# 
# a_Q: coefficient on the realized value of local-to-prepo cost per unit.
# 
# stdev_Q: standard deviation of local supply of the item during a relief event.
# - As noted above, supply is assumed to be a normal random variable with mean dependent on the realized value of $\tilde a$ (i.e., the mean of the normal random variable is m_Q + a_Q $\times \tilde a$. 
# - The value of a_Q is used to control the correlation between local-to-prepo cost and local supply. Nominally, the value of a_Q is either zero (local supply and cost are independent) or ngative. A negative value of a_Q introduces negative correlation between local supply and local unit cost. This can arise in practice because limited local supply may tend to put upward pressure on local prices. 
# 
# rho: Pearson correlation coefficient for $(\tilde z_D,\tilde z_Q)$<br>
# - The values of a_D and a_Q also control correlation between demand and supply of an item (as well as correlation wtih local-to-prepo cost). If these values are not zero, then it may be suitable to set rho = 0. A nonzero value of rho is more likely to be used when a_D = a_Q = 0. This approach allows the model to treat local-to-prepo cost as independent of demand and supply but stil allow for correlation between demand and supply (e.g., as in the example calibration above).

# ## The next block imports necessary modules & defines the necessary functions

# In[3]:


# Import the necessary modules
import numpy as np
import scipy.stats as sp
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns  # this module contains plot functionality ... may decide to use later  

# Functions defined below
def Plot_fn(file_name,min_x,max_x,incr_x,n,seed='False',
            ind_plot_by_x='False',ind_plot_by_m='False',
            all_plot_by_x='False',all_plot_by_m='False'):
    '''Generate plots of prepo spend & net marginal savings for each item, 
       return a data frame containing the sample statistics '''
    ## Load in the calibration & control parameters
    inputs = pd.read_csv(file_name)
    ## With each of the following insert statements, the parameter value is inserted to the 1st column of the data frame
    inputs.insert(1,'seed',seed,False)
    inputs.insert(1,'n',n,False)
    inputs.insert(1,'incr_x',incr_x,False)
    inputs.insert(1,'max_x',max_x,False)
    inputs.insert(1,'min_x',min_x,False)
    #print(inputs.shape)
    ## Initialize a data object that will store the summary statistics for all items
    z = []
    ## Compute & plot the budget & net marginal savings functions for each item
    for i in range(inputs.shape[0]):
        ## Compute & store net marginal savings for the item
        data = MargVal_calc(tuple(inputs.iloc[i][0:]))
        z.append(data)
        ## Create a plot by prepo spend for each item if requested
        if ind_plot_by_x:
            plt.plot(data['x'],data['m'])
            plt.ylabel('net marginal savings')
            plt.xlabel('prepo spend')
            plt.grid()
            plt.title(inputs.iloc[i][0])
            plt.show()
        ## Create a plot by net marginal savings for each item if requested
        if ind_plot_by_m:
            plt.plot(data['m'],data['x'])
            plt.xlabel('net marginal savings')
            plt.ylabel('prepo spend')
            plt.grid()
            plt.title(inputs.iloc[i][0])
            plt.show()
    ## Create a plot by prepo spend for all items if requested
    if all_plot_by_x:
        curve_labels = []
        for i in range(len(z)):
            plt.plot(z[i]['x'],z[i]['m'])
            curve_labels = curve_labels +[z[i].iloc[0]['item']]
        plt.xlabel('prepo spend')
        plt.ylabel('marginal savings')
        plt.grid()
        plt.legend(labels=curve_labels)
        plt.show()
    ## Create a plot by net marginal savings for all items if requested
    if all_plot_by_m:
        curve_labels = []
        min_m,max_m = 0, 10**10                # outer limits of common margin range
        for i in range(len(z)):
            plt.plot(z[i]['m'],z[i]['x'])
            curve_labels = curve_labels +[z[i].iloc[0]['item']]
            min_m = max(min_m,z[i]['m'].min())  
            max_m = min(max_m,z[i]['m'].max())  
        plt.xlabel('marginal savings')
        plt.ylabel('prepo spend')
        if min_m < max_m:                       # Check m values overlap for all items; if so, plot over the range
            plt.xlim(min_m,max_m)               
        plt.grid()
        plt.legend(labels=curve_labels)
        plt.show()
    ## Plot total prepo spend by marginal savings, if m values overlap across all items
    if min_m < max_m:                       # Only plot sum if there is a common range of m across the items
        ## Store the data in a new data frame to be sorted by m
        z_df = z
        ## Sort by m & combine all of the m values in the range of [min_m, max_m] for interpolation
        for i in range(len(z_df)):
            z_df[i] = z_df[i].sort_values('m')
            if i == 0:
                list_m = z_df[i]['m']
            else:
                list_m = pd.concat([list_m,z_df[i]['m']])
        ## For m_list, drop values out outside of the range, eliminate duplicates
        list_m = list_m[(list_m>=min_m)&(list_m<=max_m)]
        list_m = list_m.drop_duplicates()
        ## For each item, interpolate to obtain x values for each m in list_m & add to sum
        for i in range(len(z_df)):
            if i == 0:
                y = np.interp(list_m, z_df[i]['m'], z_df[i]['x'])
            else:
                y = y + np.interp(list_m, z_df[i]['m'], z_df[i]['x'])
        ## Now plot total prepo spend by marginal savings
        plt.plot(list_m,y,'b.')
        plt.xlabel('marginal savings')
        plt.ylabel('total prepo spend')
        plt.grid()
        plt.show()
    return z

def MargVal_calc(params):
    '''Computes net marginal savings function (per currency unit) over a range of prepo levels for the item'''
    ## initialize variables
    min_x = int(params[1])          # Define as integer
    max_x = int(params[2])          # Define as integer
    incr_x = int(params[3])         # Define as integer
    n = int(params[4])              # Define as integer
    seed = params[5]
    m_T = params[6]
    h = params[7]
    v = params[8]
    c = params[9]
    mean_a = params[10]
    stdev_a = params[11]
    min_a = params[12]
    max_a = params[13]
    ## Demand & supply parameters are converted from the item natural unit to currency units of the item
    m_D = params[14]*c
    a_D = params[15]*c
    stdev_D = params[16]*c
    Q0 = min(max(0,params[17]),1)   # Make sure that Q0 is a valid probability
    m_Q = params[18]*c
    a_Q = params[19]*c
    stdev_Q = params[20]*c
    rho = params[21]
    m_c = h * m_T                   # Compute marginal cost for the item
    z = []                          # Initialize the data storage object to null
    for x in range(min_x,max_x+1,incr_x):
        sample = Sample_gen(x,n,seed,mean_a,stdev_a,min_a,max_a,m_D,a_D,stdev_D,Q0,m_Q,a_Q,stdev_Q,rho)
        means = sample[['x','P_a','P_D','P_S','P_cx']].mean()
        m_s = (v-1)*means['P_S'] + means['P_cx'] 
        m = m_s - m_c
        z.append([params[0]] + means.tolist() + [m_s,m_c,m])
        print(f'Item: {params[0]}, x = {x}, marginal savings = {m:.2f}')
    z = pd.DataFrame(z)
    z.columns = ['item','x','E[P_a]','E[P_D]','E[P_S]','E[P_cx]','m_s','m_c','m']
    return z

def Sample_gen(x,n,seed,mean_a,stdev_a,min_a,max_a,m_D,a_D,stdev_D,Q0,m_Q,a_Q,stdev_Q,rho):
    '''Generates a sample of size n containing the 4 elements needed to compute marginal
      savings for a given prepo investment x. A data frame containing the 4 elements is returned.'''
    ## Initialize random numnber seed if defined
    if seed:
        np.random.seed(100)                     # Can change the seed value; current at 100
    ## Initialize object to store the elements of the sample
    z = []
    ## Loop to generate the n elements of the sample
    for i in range(1,n+1):
        ## Generate random a (local-to-prepo cost ratio) & compute P_a = max{a-1,0}
        a = sp.truncnorm.rvs((min_a-mean_a)/stdev_a,
                             (max_a-mean_a)/stdev_a,
                             mean_a,stdev_a)
        P_a = max(a-1,0)
        ## Compute mean demand conditional on a
        mean_D = m_D + a_D*a
        ## Compute P_D = P[D > x]
        P_D = 1-sp.norm.cdf(x,mean_D,stdev_D)
        ## Compute P_S = P[S > x]; S = D-Q
        if sp.uniform.rvs() < Q0:      # if true, then Q = 0
            mean_S,stdev_S = 0,0
            P_S = P_D
        else: 
            mean_Q = m_Q + a_Q*a
            mean_S = mean_D - mean_Q
            stdev_S = (stdev_D**2 + stdev_Q**2 - 2*rho*stdev_D*stdev_Q)**0.5
            P_S = 1-sp.norm.cdf(x,mean_S,stdev_S)
        ## Compute P_cx =P_a * (P_D - P_S)
        P_cx = P_a * (P_D - P_S)
        ## Store the results
        z.append([x,i,a,P_a,mean_D,P_D,mean_S,stdev_S,P_S,P_cx])
    ## Convert the data object to a data frame and return
    z = pd.DataFrame(z)
    z.columns = ['x','trial','a','P_a','mean_D','P_D','mean_S','stdev_S','P_S','P_cx']
    return z


# # The code is executed in the next cell.
# - You will be asked to enter the csv file name of the input data, which needs to uploaded to the server (click on the file folder to the left, then click on the folder that appears above with the upward arrow to select a file to upload).
# - You will be asked to the minimimum and maximum prepo values for the computation of the marginal savings curves (applies to all items), as well as the step size. For example, setting min = 0, max = 1000, step size = 10 will compute marginal savings for each items at prepo investment of 0, 10, 20, ..., 990, 1000. The smaller the step size (must be an integer), the greater the precision, but the longer the computation time. Each point requires several seconds to compute. In the previous example, there are 101 points for each item, so at say 2 seconds per point (typical), it would take about 3-4 minutes to compute all points for the item. As one example, it takes about 12 minutes to compute the results and plots for 3 items with min = 0, max = 20000, step size = 100 (603 total points evaluated).
# - Note that if the range from the minimum to maximum prepo values is not sufficiently large, then the summary plot showing total prepo investment by marginal savings will not be created. This plot is created by inverting the marginal savings functions, when means there must be an interval of marginal savings values that are common across all items (not be possible if the range of prepo value is too small). <b>The main takeaway:</b> if the summary plot of total prepo by marginal savings does not appear, then increase the range and run again.
# - Note that if the summary plot of total prepo by marginal savings (plot appears as a collection of dots with large spaces between), then you may run again with a smaller stepsize. 
# - You will be ased to the the name of the csv file where the computed results will be stored.
# 
# ## When ready to execute, click the circle with the triangle in the center to execute the code (alternatively, ctrl + enter when the block is selected).

# In[ ]:


# The following 5 inputs are currently set (no user prompt). This can be changed later is user control viewed as worthwhile
seed = True                             # True if same seed used for each simulation (default is False); set to 'True' to reduce confounding of results across items
ind_plot_by_x = False                   # True if plots by spend for each item are created (default is False)
ind_plot_by_m = False                   # True if plots by marginal savings for each item are created (default is False)
all_plot_by_x = True                    # True if plot by spend for all items is created (default is False)
all_plot_by_m = True                    # True if plot by marginal savings for all items is created (default is False)

# Code to collect user inputs for computing, storing, and displaying results
print('INPUT FILE NAME')
print ('The calibration is stored in a csv file with data beginning in row 2 (see template file for data in each column)')
i_file_name = input('Input file name (eg, enter "Calibration_75a" for input file "Calibration_75a.csv"): ') + '.csv'

print('\nRANGE OF MARGINAL SAVINGS CURVES (minimum and maximum prepo investment per item)')
print('Marginal savings is computed for each item at levels of prepo over the specified range')
min_x = input('Minumum prepo value used in marginal savings function calc: ')
max_x = input('Maxumum prepo value used in marginal savings function calc: ')

print('\nGRANULARITY OF MARGINAL SAVINGS CURVES')
print('Enter the difference between two consecutive prepo values (ie, integer step size used for computing the curves)')
print('Note: As step size decreases (min value of 1), the accuracy of the functions increases (more points) and CPU time increases')
incr_x = input('Step size of marginal savings functions: ')

print('\nSAMPLE SIZE USED IN MARGINAL SAVINGS COMPUTATIONS')
print('Note: As sample size decreases, the accuracy of the functions increases (more precision) and CPU time increases')
print('The default sample size is set to 1000, which will apply if the answer to the next questions is anything other than "Y"')
n = 1000                                 # default sample size
if 'Y'== input('Sample size set to a value other than 1000?'):
    n = input('Sample size: ')

print('OUTPUT FILE NAME')
print ('The computed marginal savings functions are written to a csv file with the name entered below.')
o_file_name = input('Output file name (eg, enter "Results_75a" for output file "Results_75a.csv"): ') + '.csv'
    
#print('\n',i_file_name,min_x,max_x,incr_x,n,o_file_name)

# Plot the marginal savings and prepo spend functions for each item
data = Plot_fn(i_file_name,min_x,max_x,incr_x,n,seed,ind_plot_by_x,ind_plot_by_m,all_plot_by_x,all_plot_by_m)

# Consolidate the multidimensional data frame into a single data frame to be written to the user-specified file
results=data[0]
for i in range(1,len(data)):
    results=pd.concat([results,data[i]])

# Write the consolidated data frame to a csv file
results.to_csv(o_file_name,index=False)

