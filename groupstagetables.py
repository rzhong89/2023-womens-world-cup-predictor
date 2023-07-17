import pandas as pd
from string import ascii_uppercase as alphabet
import pickle

tables = pd.read_html('https://en.wikipedia.org/wiki/2023_FIFA_Women%27s_World_Cup', match = 'Pos')
dict_table = {}

for letter, i in zip(alphabet, range(0, 8)):
    df = tables[i]
    df.rename(columns={'Teamvte': 'Team'}, inplace=True)
    df[['Pld', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']] = 0
    df.pop('Qualification')
    dict_table[f'Group {letter}'] = df

with open('dict_table', 'wb') as output:
    pickle.dump(dict_table, output)