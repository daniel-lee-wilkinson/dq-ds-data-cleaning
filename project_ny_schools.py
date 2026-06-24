# Config
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import scipy.stats

"""
# Project Goal

The goal of this project is to identify correlations between demographics (gender, race),
 district, survey responses and class sizes, and schools' sat_scores at New York schools.

# Data

The data is sourced from NYC open Data and provided by DQ. 
There are 6 files which must be read in and combined for analysis.


"""



# Read in the data
data_files = [
    "ap_2010.csv",
    "class_size.csv",
    "demographics.csv",
    "graduation.csv",
    "hs_directory.csv",
    "sat_results.csv"
]
data = {}

for f in data_files:
    key_name = f.replace(".csv", "")
    d = pd.read_csv(f)
    data[key_name] = d

print(f"Head of combined dataset: {data}")

# Read in the Surveys

all_survey = pd.read_csv("survey_all.txt", delimiter="\t", encoding='windows-1252')
d75_survey = pd.read_csv("survey_d75.txt", delimiter="\t", encoding='windows-1252')
survey = pd.concat([all_survey, d75_survey], axis=0)

survey = survey.copy()
survey["DBN"] = survey["dbn"]

survey_fields = [
    "DBN",
    "rr_s",
    "rr_t",
    "rr_p",
    "N_s",
    "N_t",
    "N_p",
    "saf_p_11",
    "com_p_11",
    "eng_p_11",
    "aca_p_11",
    "saf_t_11",
    "com_t_11",
    "eng_t_11",
    "aca_t_11",
    "saf_s_11",
    "com_s_11",
    "eng_s_11",
    "aca_s_11",
    "saf_tot_11",
    "com_tot_11",
    "eng_tot_11",
    "aca_tot_11",
]
survey = survey[survey_fields]
data["survey"] = survey

# Add DBN Columns

data["hs_directory"]["DBN"] = data["hs_directory"]["dbn"]


def pad_csd(num):
    """
    Pads a number to ensure it has at least 2 characters, adding a leading 0 if needed.
    :param: num: int
        A number or numeric string representing a CSD code
    :rtype: str
        The input number as a string, padded with a leading zero if it originally had only 1 character.

    Examples
    --------
    >>> pad_csd(3)
    '03'
    >>> pad_csd(12)
    '12'
    """

    string_representation = str(num)
    if len(string_representation) > 1:
        return string_representation
    else:
        return "0" + string_representation


data["class_size"]["padded_csd"] = data["class_size"]["CSD"].apply(pad_csd)
data["class_size"]["DBN"] = data["class_size"]["padded_csd"] + data["class_size"]["SCHOOL CODE"]


# Convert columns to numeric

cols = ['SAT Math Avg. Score', 'SAT Critical Reading Avg. Score', 'SAT Writing Avg. Score']
for c in cols:
    data["sat_results"][c] = pd.to_numeric(data["sat_results"][c], errors="coerce")

data['sat_results']['sat_score'] = data['sat_results'][cols[0]] + data['sat_results'][cols[1]] + data['sat_results'][cols[2]]

def find_lat(loc):
    """
    Extracts the latitude from a location string containing coordinates

    :param loc: string
         A string containing coordinates in the format '(latitude, longitude)', usually part of a location description.
    :return: string
        The latitude extracted as a string, without parentheses or extra spaces.

    Example
    -------
    >>> find_lat("123 Main St (40.7128, -74.0060)")
    '40.7128'

    """
    coords = re.findall("\(.+, .+\)", loc)
    lat = coords[0].split(",")[0].replace("(", "")
    return lat

def find_lon(loc):
    """
     Extracts the longitude from a location string containing coordinates

     :param loc: string
          A string containing coordinates in the format '(latitude, longitude)', usually part of a location description.
     :return: string
         The longitude extracted as a string, without parentheses or extra spaces.

     Example
     -------
     >>> find_lon("123 Main St (40.7128, -74.0060)")
     '-74.0060'

     """
    coords = re.findall("\(.+, .+\)", loc)
    lon = coords[0].split(",")[1].replace(")", "").strip()
    return lon

data["hs_directory"]["lat"] = data["hs_directory"]["Location 1"].apply(find_lat)
data["hs_directory"]["lon"] = data["hs_directory"]["Location 1"].apply(find_lon)

data["hs_directory"]["lat"] = pd.to_numeric(data["hs_directory"]["lat"], errors="coerce")
data["hs_directory"]["lon"] = pd.to_numeric(data["hs_directory"]["lon"], errors="coerce")


# Condense datasets

class_size = data["class_size"]
class_size = class_size[class_size["GRADE "] == "09-12"]
class_size = class_size[class_size["PROGRAM TYPE"] == "GEN ED"]

class_size = class_size.groupby("DBN").agg('mean', numeric_only=True)
class_size.reset_index(inplace=True)
data["class_size"] = class_size

data["demographics"] = data["demographics"][data["demographics"]["schoolyear"] == 20112012]

data["graduation"] = data["graduation"][data["graduation"]["Cohort"] == "2006"]
data["graduation"] = data["graduation"][data["graduation"]["Demographic"] == "Total Cohort"]


# Convert AP scores to numeric

cols = ['AP Test Takers ', 'Total Exams Taken', 'Number of Exams with scores 3 4 or 5']

for col in cols:
    data["ap_2010"][col] = pd.to_numeric(data["ap_2010"][col], errors="coerce")


# Combine the datasets

combined = data["sat_results"]

combined = combined.merge(data["ap_2010"], on="DBN", how="left")
combined = combined.merge(data["graduation"], on="DBN", how="left")

to_merge = ["class_size", "demographics", "survey", "hs_directory"]

# merge datasets on DBN
for m in to_merge:
    combined = combined.merge(data[m], on="DBN", how="inner")

# fill NAs with mean values
combined = combined.fillna(combined.mean(numeric_only=True))
combined = combined.infer_objects(copy=False).fillna(0)

# Add a school district column for mapping

def get_first_two_chars(dbn):
    """
    Returns the first two characters of a DBN string.

    Parameters
    ----------
    dbn : str
        A string representing a DBN code (District Borough Number).

    Returns
    -------
    str
        The first two characters of the input DBN string, representing the school district code.
    Example
    -------
    >>> get_first_two_chars("01M292")
    '01'
    """
    return dbn[0:2]

combined = combined.copy()
combined["school_dist"] = combined["DBN"].apply(get_first_two_chars)

# Find correlations

correlations = combined.corr(numeric_only=True)
correlations = correlations["sat_score"]
print(correlations)


# Plotting the correlations

## Remove DBN since it's a unique identifier, not a useful numerical value for correlation.
survey_fields.remove("DBN")

combined.corr(numeric_only=True)["sat_score"][survey_fields].plot.bar()

"""

The strongest correlations with sat_score are:

- N_s and N_p (correlation coefficient > 0.4. 
- aca_s_11, saf_s_11, saf_tot_11 and saf_t_11 are then around 0.3
- rr_s, eng_s_11, com_s_11 and aca_tot_11 are around 0.2
- the remaining variables (except com_p_11 and rr_t) are less than 0.15
- com_p_11 and rr_t are the only negatively correlated variables, each with a strength of approximately -0.1 to less than -0.5

The percentage of students who completed the survey (rr_s) correlates with the sat_score.
Students who fill out the surveys are more likely to be doing well academically.

Students and teachers with higher perceived safety (saf_t_11 and saf_s_11) had higher sat_score (positve correlation).
In an unsafe environment, it is difficult to teach or learn.

"""

# Exploring Safety and SAT Scores
# Hypothesis: in schools where students surveyed reported higher safety scores, SAT scores will be higher.
combined.plot.scatter("saf_s_11", "sat_score")

# there appears to be a positive correlation between saf_s_11 and sat_score, though it is not strong. Confirming hypothesis.
# Some schools have very high scores and high safety scores.
# Only a few schools have low scores and high safety scores.


# Hypothesis: traditionally wealthier boroughs will have higher safety scores e.g. Manhattan
boros = combined.groupby("boro").agg("mean", numeric_only=True)["saf_s_11"]
print(boros)
# Manhattan and Queens have the highest student-rated safety scores whereas Brooklyn has the lowest. Hypothesis confirmed.


# Exploring Race and SAT Scores
# Hypothesis: marginalised groups (especially non-native English speakers) will have lower SAT scores.
race_vars = ["white_per","asian_per","black_per","hispanic_per"]
combined.corr(numeric_only=True)["sat_score"][race_vars].plot.bar()
"""

The percentage of white and asian students is positively correlated with sat_score.
The percentage of hispanic and black students negatively correlate.
Since asian students get higher scores, and hispanic students get lower scores, the hypothesis can be rejected.
The relationships may instead be explained by the financial means in certain areas which are likely to have more hispanic or black students.

"""

combined.plot.scatter("hispanic_per","sat_score")

# The negative correlation is clear.
# There are a number of schools with around 100% hispanic students and the lowest sat_scores

print(combined[combined["hispanic_per"] > 95]["SCHOOL NAME"]) # schools with more than 95% hispanic students
# MANHATTAN BRIDGES HIGH SCHOOL caters to recently-arrived immigrants from Spanish speaking countries.
# WASHINGTON HEIGHTS EXPEDITIONARY LEARNING SCHOOL is a n expeditionary learning/outward bound school.
# Gregorio Luperón High School for Math and Science is for newly arrived Spanish speaking migrants

print(combined[(combined["hispanic_per"] < 10) & (combined["sat_score"] > 1800)]["SCHOOL NAME"])
# STUYVESANT HIGH SCHOOL is a college-prep high school. It offers advanced classes tuition-free. There is an admission exam.
# BRONX HIGH SCHOOL OF SCIENCE is a specialised public high school for which entrants have to pass a Specialized High Schools Admissions Test


# Exploring Gender and SAT Scores

gender_vars = ["male_per","female_per"]
combined.corr(numeric_only=True)["sat_score"][gender_vars].plot.bar()

# sat scores are weakly positively correlated with female percentage
# sat scores are weakly negatively correlated with male percentage

combined.plot.scatter("female_per", "sat_score")

# the scatterplot does not show an obvious correlation, expected from the correlation scores
# the female percentage is most often around 50% and the SAT scores typically arrange around 1000 to 1400.
# There is a cluster around 60-80% female which have high sat scores.
# There are  afew schools with 100% females and scores from 1100-1400

print(combined[(combined["female_per"] > 60) & (combined["sat_score"] > 1700)]["SCHOOL NAME"])
#  BARD HIGH SCHOOL EARLY COLLEGE is an early college series of schools where students can begin college 2 years early.
# ELEANOR ROOSEVELT HIGH SCHOOL is highly selective of its students (125-140 out of 6000 applicants accepted)


# Exploring AP Scores vs. SAT Scores

combined["ap_per"] = combined["AP Test Takers "]/combined["total_enrollment"]

combined.plot.scatter(x="ap_per",y="sat_score")
# There appears to be a weak correlation between the percentage of AP test takers and their average SAT scores.

col_names = list(combined.columns)
print(col_names)

combined.plot.scatter(x="AVERAGE CLASS SIZE", y="sat_score")
plt.show()
# there appears to be a weak, positive correlation between class size and sat_score.
# This is counterintuitive, since smaller classes usually mean more teacher attention per student.



# are the identified correlations significant --> pearson correlation coefficient. r is from -1 to 1, and p < 0.05 is significant
for var in ["saf_s_11", "white_per", "hispanic_per", "female_per","AVERAGE CLASS SIZE"]:
    subset = combined[[var, "sat_score"]].dropna()
    r, p = scipy.stats.pearsonr(subset[var], subset["sat_score"])
    sig = "✓" if p < 0.05 else "✗"
    r2 = round((r ** 2),4)*100
    print(f"{var:20s}  r={r:+.3f}  p={p:.8f}  {sig}")
    print(f"The variable {var} explains {r2} % of the variance")

"""
In each of these variables, the relationships are statistically significant (p < 0.05)

The relationship between white_per and sat_score is strong (0.621 > 0.5)
The relationship between saf_s_11, hispanic_per, AVERAGE CLASS SIZE and sat_score is moderate (0.3-0.5)
The relationship between female_per and sat_score is weak at 0.112. Therefore, the positive relationship is real but probably does not explain much.

Since there are 363 schools in the combined dataset, nearly all correlations are statistically significant.

But what proportion of variance is explained? --> r2 values

Strong predictors:
- white_per
Moderate predictors:
-  hispanic_per
- AVERAGE CLASS SIZE
- saf_s_11
Weak/negligible predictors:
- female_per

The moderate class size predictive effect is surprising. It may be that larger, more resourced schools have more students per class. Higher performing schools in densely populated areas may be oversubscribed. Some small schools may be created specifically to cater to underperforming students, pulling down the small-class end artificially.

Conclusions:
- race composition explains most variance (approx. 15-39%)
- school environment (perceived safety and class sizes) explain a moderate amount (approx. 11-15%)
- gender explains very little (1.3%)

"""