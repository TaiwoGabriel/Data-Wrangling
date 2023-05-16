#!/usr/bin/env python
# coding: utf-8

# # Fuzzy Matching
# 
# This notebook compares "official" organization names from two databases: the Orbis company name database, and the GDelt knowledge graph of news articles. "Official" Orbis company names are reconciled with alternative organization identifiers, taking in an Orbis company name and returning all alternative names mentioned in the GDelt dataset, such as alternative spellings and naming variations that refer to the same organization.

# In[ ]:


import warnings
warnings.filterwarnings('ignore')


# ## Execution settings
# 
# Set the input sources, number of Orbis company names, and the number of GDelt press articles to process.

# In[ ]:


# Inputs
ORBIS_INPUT = './input/orbis_test_small.xlsx' # Excel
GDELT_INPUT = './input/gdelt_test.csv' # CSV

# Number of Orbis records.
NUM_ROWS_ORBIS = 3000

# Range/number of GDelt records.
NUM_ROWS_GDELT_START = 0 
NUM_ROWS_GDELT_END = 1000


# #### Orbis test datasets:
# - List of Orbis companies in Sierra Leone: orbis_sierra_leone.xlsx
# - Large list of Orbis companies in Sierra Leone: orbis_test_large.xlsx
# - Small list of Orbis companies for testing: orbis_test_small.xlsx
# 
# #### GDelt test datasets:
# - List of GDelt articless in Sierra Leone in 2020: gdelt_test.csv
# 
# #### Test inputs:
# - https://drive.google.com/drive/folders/15QiHluI3dIIWPW6VLMXcxmeM2KuYD0JL?usp=sharing

# # Input

# In[ ]:


import pandas as pd


# ### Orbis Data
# 
# Load a CSV file of "official" company names, which can be obtained by querying the Orbis company database. You can limit search results by adding filter criteria, such as the country of registration.

# In[ ]:


get_ipython().system('pip install openpyxl')

indata_orbis = pd.read_excel(ORBIS_INPUT)


# In[ ]:


len(indata_orbis)


# In[ ]:


indata_orbis = indata_orbis[:NUM_ROWS_ORBIS]


# In[ ]:


indata_orbis = indata_orbis[['Company name Latin alphabet']].dropna()


# In[ ]:


indata_orbis['name_original'] = indata_orbis['Company name Latin alphabet']
indata_orbis['name'] = pd.DataFrame(indata_orbis['Company name Latin alphabet'].apply(str.lower))
outdata_orbis = indata_orbis[['name_original', 'name']]
outdata_orbis.sort_values(by='name', inplace=True)


# #### Clean company names
# 
# We need to clean company names to get rid of odd artifacts and other wrinkles. Remove anything in parenthesis, all punctuation, and any extra whitespaces.

# In[ ]:


import string

# Helper methods for name cleaning.

def remove_parenthesis(name):
    import regex as re
    return re.sub(r'\(.*\)', '', name)

def remove_punctuation(name):
    return name.translate(str.maketrans('', '', string.punctuation))

def remove_double_space(name):
    name = ' '.join(name.split())
    return name


# The "cleanco" package removes company suffixes such as "inc." and "limited".

# In[ ]:


get_ipython().system('pip install cleanco')
from cleanco import basename

outdata_orbis['name_clean'] = outdata_orbis['name'].apply(str.strip)
outdata_orbis['name_clean'] = outdata_orbis['name_clean'].apply(remove_parenthesis)
outdata_orbis['name_clean'] = outdata_orbis['name_clean'].apply(remove_punctuation)
outdata_orbis['name_clean'] = outdata_orbis['name_clean'].apply(basename)
outdata_orbis['name_clean'] = outdata_orbis['name_clean'].apply(basename) # run basename() twice because of multiple suffixes
outdata_orbis['name_clean'] = outdata_orbis['name_clean'].apply(remove_double_space)


# In[ ]:


outdata_orbis.sample(5)


# In[ ]:


outdata_orbis.to_csv('./output/orbis_list.csv')


# ### GDelt Data
# 
# Load a CSV file of press mentions, which can be obtained by querying the GDelt global knowledge database. You can limit search results by adding filter criteria, such as press mentions by country.

# In[ ]:


indata_gdelt = pd.read_csv(GDELT_INPUT)


# In[ ]:


len(indata_gdelt)


# In[ ]:


indata_gdelt = indata_gdelt[['organizations']].dropna()


# In[ ]:


orgs_unextracted_gdelt = []

for index, row in indata_gdelt.iterrows():
    # row is a single-item list with a string surrounded
    # by curly braces. Extract the single item and remove
    # the surrounding curly braces.
    orgs_unextracted_gdelt.append(row[0][1:-1])


# In[ ]:


import regex as re
orgs_extracted_gdelt = []

# The rows are json-like formatted strings that contain non-quoted
# information which includes company names, each of which can be extracted 
# via regex and be treated as a subrow.
for row in orgs_unextracted_gdelt:
    row = row.split('},')
    for subrow in row:
        match = re.findall(r'(?:n=)(.*)(?:,)', subrow)
        orgs_extracted_gdelt.append(match[0])


# In[ ]:


orgs_extracted_gdelt = pd.DataFrame(orgs_extracted_gdelt)


# In[ ]:


outdata_gdelt = pd.DataFrame(orgs_extracted_gdelt.value_counts())
outdata_gdelt.rename(columns={0: 'freq_gdelt'}, inplace=True)
outdata_gdelt.reset_index(inplace=True)
outdata_gdelt.rename(columns={0: 'name_gdelt'}, inplace=True)


# In[ ]:


outdata_gdelt = outdata_gdelt[NUM_ROWS_GDELT_START:NUM_ROWS_GDELT_END]


# In[ ]:


len(outdata_gdelt)


# In[ ]:


outdata_gdelt['name_original'] = outdata_gdelt['name_gdelt']
outdata_gdelt['name_gdelt'] = pd.DataFrame(outdata_gdelt['name_gdelt'].apply(str.lower))
outdata_gdelt['name_gdelt'] = outdata_gdelt['name_gdelt'].apply(str.strip)
outdata_gdelt['name_gdelt'] = outdata_gdelt['name_gdelt'].apply(remove_parenthesis)
outdata_gdelt['name_gdelt'] = outdata_gdelt['name_gdelt'].apply(remove_punctuation)
outdata_gdelt['name_gdelt'] = outdata_gdelt['name_gdelt'].apply(basename)
outdata_gdelt['name_gdelt'] = outdata_gdelt['name_gdelt'].apply(basename) # run basename() twice because of multiple suffixes
outdata_gdelt['name_gdelt'] = outdata_gdelt['name_gdelt'].apply(remove_double_space)


# In[ ]:


outdata_gdelt.sample(5)


# #### Acronyms
# 
# Although it's possible to compare company acronyms, there's not enough information embedded in an acronym to confidently match to full company names. For example, "US" could refer to "United States" or "United Steel" or "Universal Studios".

# In[ ]:


# Does not account for "company" or "inc" at the end of the full name.
# def create_acronym(name):
#     words = name.split() 
#     output = ''
#     for word in words: 
#         output += word[0] 
#     return output 


# In[ ]:


# Not really used at the moment.
# outdata_gdelt['acronym_gdelt'] = outdata_gdelt['name_gdelt'].apply(create_acronym)


# In[ ]:


outdata_gdelt.to_csv('./output/gdelt_list.csv')


# # Scoring
# 
# Several scoring methods are implemented below, including those from py_stringsimjoin, py_stringmatching, FuzzyWuzzy, and Jellyfish.

# ### py_stringsimjoin
# 
# Given two tables A and B, this package provides commands to perform string similarity joins between two columns of these tables, such as A.name and B.name, or A.city and B.city.
# 
# http://anhaidgroup.github.io/py_stringsimjoin/v0.1.x/overview.html

# In[ ]:


get_ipython().system('pip install py_stringsimjoin')

import py_stringsimjoin as ssj


# In[ ]:


outdata_orbis.reset_index(inplace=True)
outdata_gdelt.reset_index(inplace=True)


# #### Distance join
# 
# Join two tables using edit distance measure.

# In[ ]:


output_pairs_distance_join = ssj.edit_distance_join(outdata_orbis, outdata_gdelt,
                                      'index', 'index', 
                                      'name_clean', 'name_gdelt', 
                                      50,
                                      l_out_attrs=['name_clean'], 
                                      r_out_attrs=['name_gdelt'])


# #### py_stringmatching

# In[ ]:


get_ipython().system('pip install py_stringmatching')

import py_stringmatching as sm

ws = sm.WhitespaceTokenizer(return_set=True)


# #### Jaccard join
# 
# Join two tables using Jaccard similarity measure.

# In[ ]:


output_pairs_jaccard_join = ssj.jaccard_join(outdata_orbis, outdata_gdelt, 
                                             'index', 'index', 
                                             'name_clean', 'name_gdelt', 
                                             ws, 0.1, 
                                             l_out_attrs=['name_clean'], 
                                             r_out_attrs=['name_gdelt'])


# #### Cosine join
# 
# Join two tables using a variant of cosine similarity known as Ochiai coefficient.

# In[ ]:


output_pairs_cosine_join = ssj.cosine_join(outdata_orbis, outdata_gdelt, 
                                             'index', 'index', 
                                             'name_clean', 'name_gdelt', 
                                             ws, 0.1, 
                                             l_out_attrs=['name_clean'], 
                                             r_out_attrs=['name_gdelt'])


# #### Dice join
# 
# Join two tables using Dice similarity measure.

# In[ ]:


output_pairs_dice_join = ssj.dice_join(outdata_orbis, outdata_gdelt, 
                                             'index', 'index', 
                                             'name_clean', 'name_gdelt', 
                                             ws, 0.1, 
                                             l_out_attrs=['name_clean'], 
                                             r_out_attrs=['name_gdelt'])


# #### Overlap join
# 
# Join two tables using overlap measure.

# In[ ]:


output_pairs_overlap_join = ssj.overlap_join(outdata_orbis, outdata_gdelt, 
                                             'index', 'index', 
                                             'name_clean', 'name_gdelt', 
                                             ws, 0.1, 
                                             l_out_attrs=['name_clean'], 
                                             r_out_attrs=['name_gdelt'])


# #### Overlap coefficient join
# 
# Join two tables using overlap coefficient.

# In[ ]:


output_pairs_overlap_coefficient_join = ssj.overlap_coefficient_join(outdata_orbis, outdata_gdelt, 
                                             'index', 'index', 
                                             'name_clean', 'name_gdelt', 
                                             ws, 0.1, 
                                             l_out_attrs=['name_clean'], 
                                             r_out_attrs=['name_gdelt'])


# #### Master list
# 
# We take the dataframe of Orbis organization names and cross-join it with the dataframe of GDelt organization names, so that every Orbis company name has a record associating it with every GDelt organization mention. For example, if there are 2 Orbis company names and 3 GDelt article mentions, then there will be six comparisons: 3 comparisons for each of the two Orbis company names.

# In[ ]:


# To cross join, merge on a temporary key and then drop it.
outdata_gdelt['key'] = 1
outdata_orbis['key'] = 1

master_list = pd.merge(outdata_gdelt, outdata_orbis, on='key').drop('key', 1)
master_list.rename(columns={'name_x': 'name_gdelt', 
                             'name_original_x': 'name_original_gdelt', 
                             'name': 'name_orbis', 
                             'name_clean': 'name_clean_orbis', 
                             'name_original_y': 'name_original_orbis'}, 
                    inplace=True)


# In[ ]:


master_list.head(5)


# In[ ]:


master_list.to_csv('./output/master_list.csv')


# #### FuzzyWuzzy and Jellyfish
# 
# 1) Fuzzy string matching like a boss. It uses Levenshtein Distance to calculate the differences between sequences in a simple-to-use package: https://pypi.org/project/fuzzywuzzy/
# 
# 2) A library for doing approximate and phonetic matching of strings: https://pypi.org/project/jellyfish/

# In[ ]:


get_ipython().system('pip install fuzzywuzzy')
get_ipython().system('pip install jellyfish')

import pandas as pd
from fuzzywuzzy import fuzz
import jellyfish


# In[ ]:


try:
    data = master_list
except:
    data = pd.read_csv('./output/master_list.csv')
    data.drop(columns='Unnamed: 0', inplace=True)

data = data.dropna() # To prevent errors processing matches.


# #### Calculate fuzz ratios and jaro-wrinkler distances.
# 
# This cell calculates fuzz ratios and jaro-wrinkler distances for both spelled-out organization names and their phonetic metaphone variants. A progress bar is included to track execution of large datasets.

# In[ ]:


# Get matches of names as well as meta information.
# This is where the heavy lifting happens.

display('Match processing will take some time...')
display(str(len(data)) + ' rows...')

get_ipython().system('pip install tqdm')
from tqdm import tqdm
tqdm.pandas() # Introduces pd.apply_progress() for progress bars.

# Name comparisons. Run an apply() on two columns.
display('Calculating fuzz ratio for names...')
data['fuzz_ratio'] = data.progress_apply(lambda x: fuzz.ratio(x.name_gdelt, x.name_clean_orbis), axis=1)
display('Calculating fuzz partial ratio for names...')
data['fuzz_partial_ratio'] = data.progress_apply(lambda x: fuzz.partial_ratio(x.name_gdelt, x.name_clean_orbis), axis=1)
display('Calculating token sort ratio for names...')
data['fuzz_token_sort_ratio'] = data.progress_apply(lambda x: fuzz.token_sort_ratio(x.name_gdelt, x.name_clean_orbis), axis=1)
display('Calculating jaro distance for names...')
data['jaro_distance'] = data.progress_apply(lambda x: jellyfish.jaro_distance(x.name_gdelt, x.name_clean_orbis), axis=1)

# Metaphone generation.
display('Generating metaphones for uncleaned orbis names...')
data['metaphone_unclean_orbis'] = data['name_orbis'].progress_apply(jellyfish.metaphone)
display('Generating metaphones for cleaned orbis names...')
data['metaphone_clean_orbis'] = data['name_clean_orbis'].progress_apply(jellyfish.metaphone)
display('Generating metaphones for gdelt names...')
data['metaphone_gdelt'] = data['name_gdelt'].progress_apply(jellyfish.metaphone)

# Metaphone comparisons. Run an apply() on two columns.
display('Calculating fuzz ratio for metaphones...')
data['metaphone_fuzz_ratio'] = data.progress_apply(lambda x: fuzz.ratio(x.metaphone_gdelt, x.metaphone_clean_orbis), axis=1)
display('Calculating fuzz partial ratio for metaphones...')
data['metaphone_fuzz_partial_ratio'] = data.progress_apply(lambda x: fuzz.partial_ratio(x.metaphone_gdelt, x.metaphone_clean_orbis), axis=1)
display('Calculating token sort ratio for metaphones...')
data['metaphone_fuzz_token_sort_ratio'] = data.progress_apply(lambda x: fuzz.token_sort_ratio(x.metaphone_gdelt, x.metaphone_clean_orbis), axis=1)
display('Calculating jaro distance for metaphones...')
data['metaphone_jaro_distance'] = data.progress_apply(lambda x: jellyfish.jaro_distance(x.metaphone_gdelt, x.metaphone_clean_orbis), axis=1)

display('Done.')


# In[ ]:


data.sample(5)


# #### py_stringsimjoin
# 
# Edit distance join

# In[ ]:


data = pd.merge(data, 
                output_pairs_distance_join, 
                how='outer', 
                left_on=['index_x', 'index_y'], 
                right_on=['r_index', 'l_index'])

data.rename(columns={'_sim_score': 'sim_score_distance'}, inplace=True)


# #### py_stringmatching
# 
# Jaccard join

# In[ ]:


data = pd.merge(data, 
                output_pairs_jaccard_join, 
                how='outer', 
                left_on=['index_x', 'index_y'], 
                right_on=['r_index', 'l_index'])

data.rename(columns={'_sim_score': 'sim_score_jaccard'}, inplace=True)


# Cosine join

# In[ ]:


data = pd.merge(data, 
                output_pairs_cosine_join, 
                how='outer', 
                left_on=['index_x', 'index_y'], 
                right_on=['r_index', 'l_index'])

data.rename(columns={'_sim_score': 'sim_score_cosine'}, inplace=True)


# Dice join

# In[ ]:


data = pd.merge(data, 
                output_pairs_dice_join, 
                how='outer', 
                left_on=['index_x', 'index_y'], 
                right_on=['r_index', 'l_index'])

data.rename(columns={'_sim_score': 'sim_score_dice'}, inplace=True)


# Overlap join

# In[ ]:


data = pd.merge(data, output_pairs_overlap_join, 
                how='outer', 
                left_on=['index_x', 'index_y'], 
                right_on=['r_index', 'l_index'])

data.rename(columns={'_sim_score': 'sim_score_overlap'}, inplace=True)


# Overlap coefficient join

# In[ ]:


data = pd.merge(data, 
                output_pairs_overlap_coefficient_join, 
                how='outer', 
                left_on=['index_x', 'index_y'], 
                right_on=['r_index', 'l_index'])

data.rename(columns={'_sim_score': 'sim_score_overlap_coefficient'}, inplace=True)


# In[ ]:


data.to_csv('./output/matches_raw.csv')


# # Sorting
# 
# Sort by "official" Orbis name, then by the various scores that can be easily changed for testing purposes.

# In[ ]:


import pandas as pd


# In[ ]:


try:
    indata = data
except:
    indata = pd.read_csv('./output/matches_raw.csv')
    indata.drop(columns=['Unnamed: 0'], inplace=True)


# In[ ]:


# Sort match data in a multindex and sort by name and score.
df_sorted = indata.set_index(['name_original_orbis', 'name_original_gdelt'])
df_sorted = df_sorted.sort_values(by=['name_original_orbis', 
                                      'fuzz_ratio', 
                                      'fuzz_partial_ratio', 
                                      'fuzz_token_sort_ratio'], 
                                  ascending=False)
df_sorted = df_sorted.sort_index()


# In[ ]:


df_sorted.to_csv('./output/matches_sorted.csv')


# # Matching

# In[ ]:


import pandas as pd


# In[ ]:


try:
    df_sorted
except:
    indata = pd.read_csv('./output/matches_sorted.csv')
    df_sorted = indata.set_index(['name_original_orbis', 'name_original_gdelt'])


# In[ ]:


# Just in case we want to look at the df
# we should have the columns in a nice order.

df_unscored = df_sorted[[
    # 'acronym_gdelt', 
    'freq_gdelt', 
    'fuzz_ratio', 
    'fuzz_partial_ratio', 
    'fuzz_token_sort_ratio', 
    'jaro_distance', 
    'metaphone_unclean_orbis', 
    'metaphone_clean_orbis', 
    'metaphone_gdelt',
    'metaphone_jaro_distance',
    'metaphone_fuzz_ratio',
    'metaphone_fuzz_partial_ratio',
    'metaphone_fuzz_token_sort_ratio',
    'sim_score_distance',
    'sim_score_jaccard',
    'sim_score_cosine',
    'sim_score_dice',
    'sim_score_overlap',
    'sim_score_overlap_coefficient',
]]


# In[ ]:


len(df_unscored)


# In[ ]:


df_unscored.sample(10)


# In[ ]:


# Save progress here to allow fast manipulation of filtering below.
df_scored = df_unscored


# #### Calculate fuzz similarity
# 
# Three fuzz scores are added into a cumulativee "fuzz similarity". Other scoring measures may also be introduced here.

# In[ ]:


# An approach called "fuzz similarity"
# https://www.analyticsinsight.net/company-names-standardization-using-a-fuzzy-nlp-approach/
df_scored['fuzz_similarity'] = (2 * df_scored['fuzz_partial_ratio'] * df_scored['fuzz_token_sort_ratio']) / (df_scored['fuzz_partial_ratio'] + df_scored['fuzz_token_sort_ratio'])

# Cumulative scores.
df_scored['total_score_name'] = df_scored['fuzz_ratio'] + df_scored['fuzz_partial_ratio'] + df_scored['fuzz_token_sort_ratio']
df_scored['total_score_metaphone'] = df_scored['metaphone_fuzz_ratio'] + df_scored['metaphone_fuzz_partial_ratio'] + df_scored['metaphone_fuzz_token_sort_ratio']


# #### Threshold settings
# 
# Change the match threshold scores to experiment with accuracy and sensitivity. You can mix and match different scores to refine results and test different approaches.

# In[ ]:


# Save progress here to allow fast manipulation of matching below.
df_matches = df_scored


# In[ ]:


# Filter matches.
df_matches = df_matches[((df_matches['total_score_name'] > 280.0) & (df_matches['jaro_distance'] > 0.9))]

# Additional scoring methods for experimentation:
# df_matches = df_matches[df_matches['sim_score_distance'] <= 1]
# df_matches = df_matches[df_matches['sim_score_jaccard'] <= 2]
# df_matches = df_matches[df_matches['sim_score_cosine'] <= 2]
# df_matches = df_matches[df_matches['sim_score_dice'] <= 2]
# df_matches = df_matches[df_matches['sim_score_overlap'] <= 2]
# df_matches = df_matches[df_matches['sim_score_overlap_coefficient'] <= 2]


# In[ ]:


len(df_matches)


# In[ ]:


df_matches.head(50)


# In[ ]:


df_matches.to_csv('./output/matches_filtered.csv')


# # Output

# In[ ]:


import pandas as pd


# In[ ]:


try:
    indata = df_matches
except:
    indata = pd.read_csv('./output/matches_filtered.csv')
    indata = indata.set_index(['name_original_orbis', 'name_original_gdelt'])


# In[ ]:


# Clean up the final output.
dataout = indata[['fuzz_similarity', 
                  'total_score_name', 
                  'total_score_metaphone', 
                  'freq_gdelt', 
                  'jaro_distance', 
                  'metaphone_jaro_distance', 
                  'sim_score_distance',
                  'sim_score_jaccard',
                  'sim_score_cosine',
                  'sim_score_dice',
                  'sim_score_overlap',
                  'sim_score_overlap_coefficient',
                 ]]


# In[ ]:


dataout.head(50)


# In[ ]:


dataout.to_csv('./output/OUTPUT.csv')


# In[ ]:




