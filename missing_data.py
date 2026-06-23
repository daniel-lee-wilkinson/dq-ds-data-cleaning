# Goals

# 1. learn how do handle missing data without dropping rows or columns

# Dataset
# data on New York City moto vehicle collisions, published on NYC OpenData Website
# extract of the full data which is updated continuously

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


mvc = pd.read_csv("nypd_mvc_2018.csv")

# preview raw data
print(mvc.head())
# column names
print(mvc.columns)

null_counts = mvc.isnull().sum() # series of counts of nulls

# percentage of nulls
null_counts_pct = null_counts / mvc.shape[0] * 100

# add both nulls and percentages to a new dataframe for comparison

null_mvc = pd.DataFrame({"null_counts":null_counts, "null_pct":null_counts_pct})
null_mvc = null_mvc.T.astype(int) # transpose the mvc
print(null_mvc)

# consider killed columns first
killed_cols = [col for col in mvc.columns if "killed" in col] # list comprehension
print(null_mvc[killed_cols])
"""
Findings:
there are 5 missing values for total_killed only
options for handling:
1. drop those rows - small portion of the data
2. imputation - total_killed is the sum of the other killed categories. What if it's not?
"""

# Create a killed dataframe and manually sum values
killed_cols = [col for col in mvc.columns if 'killed' in col]
killed = mvc[killed_cols].copy()
killed_manual_sum = killed.iloc[:, :3].sum(axis=1)

# fix the killed values
killed['total_killed'] = killed['total_killed'].mask(killed['total_killed'].isnull(), killed_manual_sum)
killed['total_killed'] = killed['total_killed'].mask(killed['total_killed'] != killed_manual_sum, np.nan)

# Create an injured dataframe and manually sum values

print("----starting with injured data------")
injured = mvc[[col for col in mvc.columns if 'injured' in col]].copy()
injured_manual_sum = injured.iloc[:, :3].sum(axis=1)
injured['total_injured'] = injured['total_injured'].mask(injured['total_injured'].isnull(), injured_manual_sum)
injured['total_injured'] = injured['total_injured'].mask(injured['total_injured'] != injured_manual_sum, np.nan)
print(injured)

# 4. Assigning the Corrected Data Back to the Main Dataframe

summary = {
    'injured': [
        mvc['total_injured'].isnull().sum(),
        injured['total_injured'].isnull().sum()
    ],
    'killed': [
        mvc['total_killed'].isnull().sum(),
        killed['total_killed'].isnull().sum()
    ]
}
print(pd.DataFrame(summary, index=['before','after']))

# assign total_injured back to the injured column of the mvc dataframe

mvc['total_injured'] = injured['total_injured']
mvc['total_killed'] = killed['total_killed']


# Visualizing Missing Data with Plots

def plot_null_matrix(mvc, figsize=(18,15)):
    # initiate the figure
    plt.figure(figsize=figsize)
    # create a boolean dataframe based on whether values are null
    mvc_null = mvc.isnull()
    # create a heatmap of the boolean dataframe
    sns.heatmap(~mvc_null, cbar=False, yticklabels=False)
    plt.xticks(rotation=90, size='large')
    plt.show()

#plot_null_matrix(mvc)

cols_with_missing_vals = mvc.columns[mvc.isnull().sum() > 0]
missing_corr = mvc[cols_with_missing_vals].isnull().corr()
print(f"-----printing missing_corr matrix: \n{missing_corr}")


def plot_null_correlations(mvc):

    # create a correlation matrix only for columns with at least
    # one missing value
    cols_with_missing_vals = mvc.columns[mvc.isnull().sum() > 0]
    missing_corr = mvc[cols_with_missing_vals].isnull().corr()

    # create a mask to avoid repeated values and make
    # the plot easier to read
    missing_corr = missing_corr.iloc[1:, :-1]
    mask = np.triu(np.ones_like(missing_corr), k=1)

    # plot a heatmap of the values
    plt.figure(figsize=(20, 14))
    ax = sns.heatmap(missing_corr, vmin=-1, vmax=1, cbar=False,
                     cmap='RdBu', mask=mask, annot=True)

    # format the text in the plot to make it easier to read
    for text in ax.texts:
        t = float(text.get_text())
        if -0.05 < t < 0.01:
            text.set_text('')
        else:
            text.set_text(round(t, 2))
        text.set_fontsize('x-large')
    plt.xticks(rotation=90, size='x-large')
    plt.yticks(rotation=0, size='x-large')

    plt.show()


vehicle_cols=[col for col in mvc.columns if "vehicle" in col] # list comprehension
print(f"-----Plotting null correlation matrix-----")
#plot_null_correlations(mvc[vehicle_cols])

# Analyzing Correlations in Missing Data

col_labels = ['v_number', 'vehicle_missing', 'cause_missing']

vc_null_data = []

for v in range(1, 6): # there are 5 vehicle causes
    v_col = f'vehicle_{v}'
    c_col = f'cause_vehicle_{v}'

    v_null = (mvc[v_col].isnull() & mvc[c_col].notnull()).sum()
    c_null = (mvc[c_col].isnull() & mvc[v_col].notnull()).sum()

    vc_null_data.append([v, v_null, c_null])

vc_null_mvc = pd.DataFrame(vc_null_data, columns=col_labels)
print(f"The dataframe showing the number of null vehicles and null causes: \n {vc_null_mvc}")


# Finding the Most Common Values Across Multiple Columns

# -> can use most common values for imputation


cause_cols = [c for c in mvc.columns if "cause_" in c]
cause = mvc[cause_cols]
print(f"head of the causes: \n{cause.head()}")
cause_1d = cause.stack()
print(f"head of the cause1d mvc: \n {cause_1d.head()}") # this omits null values
cause_counts = cause_1d.value_counts()
top10_causes = cause_counts.head(10)
print(f"The top ten causes are: \n {top10_causes}")


v_cols = [c for c in mvc.columns if c.startswith("vehicle")]
vs = mvc[v_cols]
print(f"head of the vehicle columns: \n {vs.head()}")
vs_1d = vs.stack()
print(f"head of the vs1d mvc: \n {vs_1d.head()}")
vs_1d_counts = vs_1d.value_counts()
top10_vehicles = vs_1d_counts.head(10)
print(f"The top ten vehicles are: \n {top10_vehicles}")

# Filling Unknown Values with a Placeholder

def summarize_missing(mvc):
    v_missing_data = []

    for v in range(1, 6):
        v_col = f'vehicle_{v}'
        c_col = f'cause_vehicle_{v}'

        v_missing = (mvc[v_col].isnull() & mvc[c_col].notnull()).sum()
        c_missing = (mvc[c_col].isnull() & mvc[v_col].notnull()).sum()

        v_missing_data.append([v, v_missing, c_missing])

    col_labels = ["vehicle_number", "vehicle_missing", "cause_missing"]
    return pd.DataFrame(v_missing_data, columns=col_labels)


summary_before = summarize_missing(mvc)

for v in range(1, 6):
    v_col = f"vehicle_{v}"
    c_col = f"cause_vehicle_{v}"

    v_missing_mask = mvc[v_col].isnull() & mvc[c_col].notnull()
    c_missing_mask = mvc[c_col].isnull() & mvc[v_col].notnull()

    mvc[v_col] = mvc[v_col].mask(v_missing_mask, "Unspecified")
    mvc[c_col] = mvc[c_col].mask(c_missing_mask, "Unspecified")

summary_after = summarize_missing(mvc)


#  Missing Data in the "Location" Columns

veh_cols = [c for c in mvc.columns if 'vehicle' in c]
#plot_null_correlations(mvc[veh_cols])

loc_cols = ['borough', 'location', 'on_street', 'off_street', 'cross_street']
location_data = mvc[loc_cols]
print(location_data.head())
print(location_data.isnull().sum())
#plot_null_correlations(location_data)
sorted_location_data = location_data.sort_values(loc_cols)
#plot_null_matrix(sorted_location_data)

## Impute location from geodata
sup_data = pd.read_csv('supplemental_data.csv')
sup_data.head()
#plot_null_matrix(sup_data)
# if the unique_key column in both the original dataset and the supplemental one has values int eh same order,
# we can use Series.mask() to add supplemental data to the original data

mvc_keys = mvc['unique_key']
sup_keys = sup_data['unique_key']

is_equal = mvc_keys.equals(sup_keys)
print(f"Are the unique keys in mvc and sup_key equal? {is_equal}")

location_cols = ['location', 'on_street', 'off_street', 'borough']
null_before = mvc[location_cols].isnull().sum()


for col in location_cols:
    mvc[col] = mvc[col].mask(mvc[col].isnull(), sup_data[col])

null_after = mvc[location_cols].isnull().sum()
print(f"After fixing the location column with supplementary geodata, there are the following empty location columns. \n {null_after}")
print(mvc.shape)

mask = mvc[location_cols].isna().all(axis=1)
rows_without_location_data = mask.sum()
print(f"After adding the geodata, there are still {rows_without_location_data} rows with no location data.")
mvc = mvc[~mask]
print(f"After removing rows without any location data, there are {mvc.shape[0]} rows")
