#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 19:27:48 2022

Programme to update ELO ratings based on past results. Initial ELO is 1000.

@author: joey
"""

import pandas as pd

# Function updates the elo for an away team
def update_away_team_elo(elo_A, elo_B, result, K, home_elo):
    
    expected_score = 1/(1 + 10**(((elo_B + home_elo) - elo_A)/400))
    
    return elo_A + K * (result - expected_score)

# Function updates the elo for a home team
def update_home_team_elo(elo_A, elo_B, result, K, home_elo):
    
    expected_score = 1/(1 + 10**((elo_B - (elo_A + home_elo))/400))
    
    return elo_A + K * (result - expected_score)

def home_score(result):
    
    if result == 'H':
        return 1
    elif result == 'T':
        return 0.5
    elif result == 'A':
        return 0
    
def away_score(result):
    
    if result == 'H':
        return 0
    elif result == 'T':
        return 0.5
    elif result == 'A':
        return 1
    
def get_K_value(home_points, away_points, initial_K):
    
    if abs(home_points - away_points) <= 7:
        return initial_K
    elif 7 < abs(home_points - away_points) <= 14:
        return 1.5 * initial_K
    elif 15 < abs(home_points - away_points) <= 21:
        return 1.75 * initial_K
    elif 22 < abs(home_points - away_points) <= 28:
        return 1.875 * initial_K
    elif 29 < abs(home_points - away_points) <= 35:
        return 2 * initial_K
    elif 36 < abs(home_points - away_points) <= 42:
        return 2.125 * initial_K
    elif 43 < abs(home_points - away_points) <= 49:
        return 2.25 * initial_K
    elif 50 < abs(home_points - away_points) <= 56:
        return 2.375 * initial_K
    elif 57 < abs(home_points - away_points) <= 63:
        return 2.5 * initial_K
    else:
        return initial_K
    
def get_QB_K_value(home_points, away_points, home_defence, away_defence, result, initial_K):
    
    K = get_K_value(home_points, away_points, initial_K)
    
    if result == 'H' and home_points > away_defence and away_points < home_defence:
        return K * 1.5
    elif result == 'A' and home_points < away_defence and away_points > home_defence:
        return K * 1.5
    elif result == 'H' and home_points < away_defence and away_points > home_defence:
        return K * 0.5
    elif result == 'A' and home_points > away_defence and away_points < home_defence:
        return K * 0.5
    else:
        return K


results_df = pd.read_csv('nfl_results.csv', sep=',')

teams_df = pd.read_csv('teams.csv', sep=',')
teams_df.set_index('Team', inplace=True)

qb_df = pd.read_csv('qb.csv', sep=',')
qb_df.set_index('QB', inplace=True)

initial_K = 20
QB_K_value = 30
home_elo = 46.4

for index, row in results_df.iterrows():
        
    home_result = home_score(row['Result'])
    away_result = away_score(row['Result'])
    
    # ELO increases/decreases more in the first 4 weeks of the season
    if row['Week'] == '1' or row['Week'] == '2' or row['Week'] == 3 or row['Week'] == 4:
        
        K = get_K_value(row['HomePoints'], row['AwayPoints'], initial_K*2)
        
    else:
        
        K = get_K_value(row['HomePoints'], row['AwayPoints'], initial_K)
        
    if qb_df.at[row['QBHome'], 'Games Played'] <= 16:
        K_QB_H = get_QB_K_value(row['HomePoints'], row['AwayPoints'], teams_df.at[row['HomeTeam'], 'Defence'], teams_df.at[row['AwayTeam'], 'Defence'], row['Result'], QB_K_value*2)
    
    else:
        K_QB_H = get_QB_K_value(row['HomePoints'], row['AwayPoints'], teams_df.at[row['HomeTeam'], 'Defence'], teams_df.at[row['AwayTeam'], 'Defence'], row['Result'], QB_K_value)
    
    if qb_df.at[row['QBAway'], 'Games Played'] <= 16:
        K_QB_A = get_QB_K_value(row['HomePoints'], row['AwayPoints'], teams_df.at[row['HomeTeam'], 'Defence'], teams_df.at[row['AwayTeam'], 'Defence'], row['Result'], QB_K_value*2)
    
    else:
        K_QB_A = get_QB_K_value(row['HomePoints'], row['AwayPoints'], teams_df.at[row['HomeTeam'], 'Defence'], teams_df.at[row['AwayTeam'], 'Defence'], row['Result'], QB_K_value)
            
    teams_df.at[row['HomeTeam'], 'ELO'] = update_home_team_elo(teams_df.loc[row['HomeTeam'], 'ELO'], 
                                                      teams_df.loc[row['AwayTeam'], 'ELO'],
                                                      home_result, K, home_elo)
    
    teams_df.at[row['AwayTeam'], 'ELO'] = update_away_team_elo(teams_df.loc[row['AwayTeam'], 'ELO'], 
                                                      teams_df.loc[row['HomeTeam'], 'ELO'],
                                                      away_result, K, home_elo)

    qb_df.at[row['QBHome'], 'ELO'] = update_home_team_elo(qb_df.loc[row['QBHome'], 'ELO'], 
                                                      teams_df.loc[row['AwayTeam'], 'ELO'],
                                                      home_result, K_QB_H, home_elo)
    
    qb_df.at[row['QBAway'], 'ELO'] = update_away_team_elo(qb_df.loc[row['QBAway'], 'ELO'], 
                                                      teams_df.loc[row['HomeTeam'], 'ELO'],
                                                      away_result, K_QB_A, home_elo)
    
    teams_df.at[row['HomeTeam'], str(teams_df.at[row['HomeTeam'], 'Game Number'] % 16)] = row['AwayPoints']
    teams_df.at[row['AwayTeam'], str(teams_df.at[row['AwayTeam'], 'Game Number'] % 16)] = row['HomePoints']
    
    teams_df.at[row['HomeTeam'], 'Defence'] = (teams_df.at[row['HomeTeam'], '0'] + teams_df.at[row['HomeTeam'], '1'] + teams_df.at[row['HomeTeam'], '2'] + teams_df.at[row['HomeTeam'], '3'] + teams_df.at[row['HomeTeam'], '4'] + teams_df.at[row['HomeTeam'], '5'] + teams_df.at[row['HomeTeam'], '6'] + teams_df.at[row['HomeTeam'], '7'] + teams_df.at[row['HomeTeam'], '8'] + teams_df.at[row['HomeTeam'], '9'] + teams_df.at[row['HomeTeam'], '10'] + teams_df.at[row['HomeTeam'], '11'] + teams_df.at[row['HomeTeam'], '12'] + teams_df.at[row['HomeTeam'], '13'] + teams_df.at[row['HomeTeam'], '14'] + teams_df.at[row['HomeTeam'], '15'])/16
    teams_df.at[row['AwayTeam'], 'Defence'] = (teams_df.at[row['AwayTeam'], '0'] + teams_df.at[row['AwayTeam'], '1'] + teams_df.at[row['AwayTeam'], '2'] + teams_df.at[row['AwayTeam'], '3'] + teams_df.at[row['AwayTeam'], '4'] + teams_df.at[row['AwayTeam'], '5'] + teams_df.at[row['AwayTeam'], '6'] + teams_df.at[row['AwayTeam'], '7'] + teams_df.at[row['AwayTeam'], '8'] + teams_df.at[row['AwayTeam'], '9'] + teams_df.at[row['AwayTeam'], '10'] + teams_df.at[row['AwayTeam'], '11'] + teams_df.at[row['AwayTeam'], '12'] + teams_df.at[row['AwayTeam'], '13'] + teams_df.at[row['AwayTeam'], '14'] + teams_df.at[row['AwayTeam'], '15'])/16

    # Update number of games for team
    teams_df.at[row['HomeTeam'], 'Game Number'] = teams_df.at[row['HomeTeam'], 'Game Number'] + 1
    teams_df.at[row['AwayTeam'], 'Game Number'] = teams_df.at[row['AwayTeam'], 'Game Number'] + 1
    qb_df.at[row['QBHome'], 'Games Played'] = qb_df.at[row['QBHome'], 'Games Played'] + 1
    qb_df.at[row['QBAway'], 'Games Played'] = qb_df.at[row['QBAway'], 'Games Played'] + 1
    
teams_df.to_csv('teams_elo.csv')
qb_df.to_csv('qb_elo.csv')
        


    
    
    
    