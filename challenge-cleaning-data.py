# Life and Death of the Avengers

import pandas as pd
import matplotlib.pyplot as plt

avengers = pd.read_csv("avengers.csv", encoding = "ISO-8859-1")
print(avengers.head())
print(avengers.shape)

# Filtering out bad data
true_avengers = avengers[avengers["Year"] >= 1960]
print(true_avengers.head())
print(true_avengers.shape)

# Consolidating Deaths

print(true_avengers["Death1"].head())


def clean_deaths(row):
    num_deaths = 0
    columns = ['Death1', 'Death2', 'Death3', 'Death4', 'Death5']

    for c in columns:
        death = row[c]
        if pd.isnull(death) or death == 'NO':
            continue
        elif death == 'YES':
            num_deaths += 1
    return num_deaths


true_avengers.loc[:, 'Deaths'] = true_avengers.apply(clean_deaths, axis=1)

print(true_avengers.head())

# Verifying Years Since Joining

joined_accuracy_count = int()

correct_joined_years = true_avengers[true_avengers["Years since joining"] == (2015-true_avengers["Year"])]
joined_accuracy_count = len(correct_joined_years)


