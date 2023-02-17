#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 18:03:08 2022

@author: joey
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 10:57:20 2022

@author: joey
"""

import time

import pandas as pd
    
def calculate_total_elo(team_elo, qb_elo, qb_weight):
    
    return (1-qb_weight)*team_elo + qb_weight*qb_elo

def predict_game(elo_H, elo_A):
    
    expected_score_H = 1/(1 + 10**((elo_A - elo_H)/400))
    expected_score_A = 1/(1 + 10**((elo_H - elo_A)/400))
    
    probability_home = expected_score_H**(1.00983)
    probability_away = expected_score_A**(1.00983)
    
    return probability_home, probability_away

def predict_playoff_game(elo_H, elo_A):
    
    expected_score_H = 1/(1 + 10**((elo_A - elo_H)/400))
    expected_score_A = 1/(1 + 10**((elo_H - elo_A)/400))
    
    probability_home = expected_score_H**(1)
    probability_away = expected_score_A**(1)
    
    return probability_home, probability_away

def get_betting_odds(probability):
    
    return round(1/probability, 2)

def get_spread(elo_h, elo_a):
    
    return round((elo_h - elo_a)/25)
    
start = time.time()
K = 20
K_QB = 30
qb_weight = 0.452
home_elo = 46.4
    
schedule_df = pd.read_csv('nfl_schedule.csv', sep=',')

teams_elo_df = pd.read_csv('teams_elo.csv', sep=',')
teams_elo_df.set_index('Team', inplace=True)

qb_elo_df = pd.read_csv('qb_elo.csv', sep=',')
qb_elo_df.set_index('QB', inplace=True)

qb_schedule_df = pd.read_csv('team_qb_schedule.csv')
qb_schedule_df.set_index('Team', inplace=True)

for index, row in schedule_df.iterrows():
    
    if row['Neutral'] == 'Yes':
        home_elo = 0
    else:
        home_elo = 46.4
    
    qb_home = qb_schedule_df.loc[row['Home'], str(row['Week'])]
    qb_away = qb_schedule_df.loc[row['Away'], str(row['Week'])]

    elo_home = home_elo + calculate_total_elo(teams_elo_df.loc[row['Home'], 'ELO'], qb_elo_df.loc[qb_home, 'ELO'], qb_weight)
    elo_away = calculate_total_elo(teams_elo_df.loc[row['Away'], 'ELO'], qb_elo_df.loc[qb_away, 'ELO'], qb_weight)
    
    schedule_df.at[index, 'Home Win Prob'], schedule_df.at[index, 'Away Win Prob'] = predict_playoff_game(elo_home, elo_away)
    schedule_df.at[index, 'Tie Prob'] = 1 - (schedule_df.at[index, 'Home Win Prob'] + schedule_df.at[index, 'Away Win Prob'])
    
    schedule_df.at[index, 'ELO Home'] = round(elo_home, 1)
    schedule_df.at[index, 'ELO Away'] = round(elo_away, 1)
    
    schedule_df.at[index, 'Odds Home'] = get_betting_odds(schedule_df.at[index, 'Home Win Prob'])
    schedule_df.at[index, 'Odds Away'] = get_betting_odds(schedule_df.at[index, 'Away Win Prob'])
    schedule_df.at[index, 'Spread'] = get_spread(elo_home, elo_away)
    
end = time.time()

schedule_df.to_csv('probabilities_nfl.csv')

print("The time of execution of above program is :", end-start)
    



