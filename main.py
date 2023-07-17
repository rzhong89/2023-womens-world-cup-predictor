import pandas as pd
import pickle
from scipy.stats import poisson

dict_table = pickle.load(open('dict_table', 'rb'))
df_historical_data = pd.read_csv('clean_fifa_worldcup_matches.csv')
df_fixture = pd.read_csv('clean_fifa_worldcup_fixture.csv')

df_home = df_historical_data[['HomeTeam', 'HomeGoals', 'AwayGoals']]
df_away = df_historical_data[['AwayTeam', 'HomeGoals', 'AwayGoals']]

df_home = df_home.rename(columns={'HomeTeam': 'Team', 'HomeGoals': 'GoalsScored', 'AwayGoals': 'GoalsConceded'})
df_away = df_away.rename(columns={'AwayTeam': 'Team', 'HomeGoals': 'GoalsConceded', 'AwayGoals': 'GoalsScored'})
df_team_strength = pd.concat([df_home, df_away], ignore_index=True).groupby(['Team'], as_index=False).mean()


def predict_points(home, away):
    if home in df_team_strength.values and away in df_team_strength.values:
        index_home_list = df_team_strength.index[df_team_strength['Team'] == home].tolist()
        index_home = index_home_list[0]
        index_away_list = df_team_strength.index[df_team_strength['Team'] == away].tolist()
        index_away = index_away_list[0]
        lamb_home = df_team_strength.at[index_home, 'GoalsScored'] * df_team_strength.at[index_away, 'GoalsConceded']
        lamb_away = df_team_strength.at[index_away, 'GoalsScored'] * df_team_strength.at[index_home, 'GoalsConceded']

        prob_home, prob_away, prob_draw = 0, 0, 0

        for x in range(0, 11):
            for y in range(0, 11):
                p = poisson.pmf(x, lamb_home) * poisson.pmf(y, lamb_away)
                if x == y:
                    prob_draw += p
                elif x > y:
                    prob_home += p
                else:
                    prob_away += p

        points_home = 3 * prob_home + prob_draw
        points_away = 3 * prob_away + prob_draw

        return points_home, points_away
    else:
        return 0, 0


df_fixture_group_48 = df_fixture[:48].copy()
df_fixture_knockout = df_fixture[48:56].copy()
df_fixture_quarter = df_fixture[56:60].copy()
df_fixture_semi = df_fixture[60:62].copy()
df_fixture_final = df_fixture[62:].copy()

for group in dict_table:
    teams_in_group = dict_table[group]['Team'].values
    df_fixture_group_6 = df_fixture_group_48[df_fixture_group_48['home'].isin(teams_in_group)]
    for index, row in df_fixture_group_6.iterrows():
        home, away = row['home'], row['away']
        points_home, points_away = predict_points(home, away)
        dict_table[group].loc[dict_table[group]['Team'] == home, 'Pts'] += points_home
        dict_table[group].loc[dict_table[group]['Team'] == away, 'Pts'] += points_away

    dict_table[group] = dict_table[group].sort_values('Pts', ascending=False).reset_index()
    dict_table[group] = dict_table[group][['Team', 'Pts']]
    dict_table[group] = dict_table[group].round(2)
    print(dict_table[group])

for group in dict_table:
    group_winners = dict_table[group].loc[0, 'Team']
    runners_up = dict_table[group].loc[1, 'Team']
    df_fixture_knockout.replace({f'Winner {group}': group_winners, f'Runner-up {group}': runners_up}, inplace=True)

df_fixture_knockout['winner'] = '?'


def get_winner(df_fixture_updated):
    for index, row in df_fixture_updated.iterrows():
        home, away = row['home'], row['away']
        points_home, points_away = predict_points(home, away)
        if points_home > points_away:
            winner = home
        else:
            winner = away
        df_fixture_updated.loc[index, 'winner'] = winner
    return df_fixture_updated


print(get_winner(df_fixture_knockout))


def update_table(df_fixture_round_1, df_fixture_round_2):
    for index, row in df_fixture_round_1.iterrows():
        winner = df_fixture_round_1.loc[index, 'winner']
        match = df_fixture_round_1.loc[index, 'score']
        df_fixture_round_2.replace({f'Winner {match}': winner}, inplace=True)
    df_fixture_round_2['winner'] = '?'
    return df_fixture_round_2


update_table(df_fixture_knockout, df_fixture_quarter)
print(get_winner(df_fixture_quarter))

update_table(df_fixture_quarter, df_fixture_semi)
print(get_winner(df_fixture_semi))

update_table(df_fixture_semi, df_fixture_final)
print(get_winner(df_fixture_final))
print(predict_points('Norway', 'France'))