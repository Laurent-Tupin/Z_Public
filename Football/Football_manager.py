import pandas as pd
import numpy as np
import random


def display_teamList(l_team):
    for play in l_team:
        print(play)
    print('')
    
def display_team(ddd):
    for play in ddd.items():
        print('   ', play)
    print('')

def fDict_addListToDictValues(d_players, l_random):
    d_players_Random = d_players.copy()
    l_players_level = list(d_players.values())
    l_players_name = list(d_players.keys())
    
    for i in range(len(d_players)):
        str_player = l_players_name[i]
        int_level = l_players_level[i]
        int_randomNum = l_random[i]
        int_levelRandom = round(int_level + int_randomNum, 1)
        # Change the value of Player by giving some randomness
        d_players_Random[str_player] = abs(int_levelRandom)
    return d_players_Random



def f_BuildTeams_15(d_players, bl_print = False):
    # PARAM
    l_teamWhite = []
    l_teamColor = []
    l_teamRed =   []
    int_WhiteScore = 0
    int_ColorScore = 0
    int_redScore = 0
    
    # First Player in White team
    # l_teamWhite.append('_Eddie 70$')
    # int_WhiteScore += d_players['_Eddie 70$']
    # del d_players['_Eddie 70$']
    
    # # Second Player in Color team
    # l_teamColor.append('Darren')
    # int_ColorScore += d_players['Darren']
    # del d_players['Darren']
    
    # # Third Player in RED team
    # l_teamRed.append('_Chris 70$')
    # int_redScore += d_players['_Chris 70$']
    # del d_players['_Chris 70$']
    
    
    # Fill the team in a loop
    for i_numPlayer in range(1, len(d_players) + 1):
        int_nbPlayer = len(d_players)
        l_randomlist = random.sample(range(0, int_nbPlayer), int_nbPlayer)
        
        if bl_print:    print('Player in teams: ', i_numPlayer, '   Remaining player: ', int_nbPlayer)
        
        # Color team
        if int_nbPlayer % 3 == 0:
            int_colorAdv = (2*int_ColorScore - int_WhiteScore - int_redScore) / 2
            flt_avgLevelPlayers = round(max(d_players.values()), 1)
            flt_levelWanted = round(flt_avgLevelPlayers - int_colorAdv, 2)
            d_players_level = {play : round(abs(rate - flt_levelWanted) * i_numPlayer, 1)  for (play, rate) in d_players.items()} 
            ## Add some randomness
            d_playersLevel_Random = fDict_addListToDictValues(d_players_level, l_randomlist)
            # Get the right player
            str_player = min(d_playersLevel_Random, key = d_playersLevel_Random.get)
            # Add the player to white team
            l_teamColor.append(str_player)
            int_ColorScore += round(d_players[str_player], 2)
            del d_players[str_player]
        # white Team
        elif (int_nbPlayer - 1) % 3 == 0:
            int_gapToFillForWhite = int_ColorScore - int_WhiteScore
            d_players_level = {play : abs(rate - int_gapToFillForWhite) * i_numPlayer for (play, rate) in d_players.items()}
            ## Add some randomness
            d_playersLevel_Random = fDict_addListToDictValues(d_players_level, l_randomlist)
            # Get the right player
            str_player = min(d_playersLevel_Random, key = d_playersLevel_Random.get)
            # Add the player to white team
            l_teamWhite.append(str_player)
            int_WhiteScore += round(d_players[str_player], 2)
            del d_players[str_player]
        # Red Team
        else:
            int_gapToFillForRed = (int_ColorScore + int_WhiteScore - 2 * int_redScore) /2
            d_players_level = {play : abs(rate - int_gapToFillForRed) * i_numPlayer for (play, rate) in d_players.items()}
            ## Add some randomness
            d_playersLevel_Random = fDict_addListToDictValues(d_players_level, l_randomlist)
            # Get the right player
            str_player = min(d_playersLevel_Random, key = d_playersLevel_Random.get)
            # Add the player to white team
            l_teamRed.append(str_player)
            int_redScore += round(d_players[str_player], 2)
            del d_players[str_player]
            
    return l_teamWhite, int_WhiteScore, l_teamColor, int_ColorScore, l_teamRed, int_redScore

    
    
    

def f_BuildTeams(d_players, bl_print = False):
    # PARAM
    l_teamWhite = []
    l_teamColor = []
    int_WhiteScore = 0
    int_ColorScore = 0
    
    # # First Player in Color team
    # str_firstPlayer = '_Thomas'
    # l_teamColor.append(str_firstPlayer)
    # int_ColorScore += d_players[str_firstPlayer]
    # del d_players[str_firstPlayer]
    
    # # Second Player in White team
    # str_secPlayer = '_Roland'
    # l_teamWhite.append(str_secPlayer)
    # int_WhiteScore += d_players[str_secPlayer]
    # del d_players[str_secPlayer]
    
    
    # Fill the team in a loop
    for i_numPlayer in range(1, len(d_players) + 1):
        int_nbPlayer = len(d_players)
        l_randomlist = random.sample(range(0, int_nbPlayer), int_nbPlayer)
        
        if bl_print:    print('Player in teams: ', i_numPlayer, '   Remaining player: ', int_nbPlayer)
        
        # If White Team (odd number)
        if int_nbPlayer % 2 != 0:
            if bl_print:    print(' White team...')
            int_gapToFillForWhite = int_ColorScore - int_WhiteScore
            if bl_print:    print('   Gap to fill...', int_gapToFillForWhite)
            d_players_level = {play : abs(rate - int_gapToFillForWhite) for (play, rate) in d_players.items()}
            if bl_print:    display_team(d_players_level)
            d_players_level = {play : abs(rate - int_gapToFillForWhite) * i_numPlayer for (play, rate) in d_players.items()}
            if bl_print:    display_team(d_players_level)
            # str_player = min(d_players_level, key = d_players_level.get)
            # print('   ', str_player)
            
            ## Add some randomness
            d_playersLevel_Random = fDict_addListToDictValues(d_players_level, l_randomlist)
            if bl_print:    print('   ', l_randomlist)
            if bl_print:    display_team(d_playersLevel_Random)
            # Get the right player
            str_player = min(d_playersLevel_Random, key = d_playersLevel_Random.get)
            if bl_print:    print('   White Player chosen: ', str_player, '\n')
            # Add the player to white team
            l_teamWhite.append(str_player)
            int_WhiteScore += round(d_players[str_player], 2)
            del d_players[str_player]
        
        # If color Team (even number)
        else:
            if bl_print:    print(' color team...')
            int_whiteAdvantage = int_WhiteScore - int_ColorScore
            if bl_print:    print('   White advantage...', int_whiteAdvantage)
            flt_avgLevelPlayers = round(max(d_players.values()), 1)
            if bl_print:    print('   Average level or remaining player...', flt_avgLevelPlayers)
            flt_levelWanted = round(flt_avgLevelPlayers + int_whiteAdvantage, 2)
            if bl_print:    print('   Level wanted for a new player...', flt_levelWanted)
            d_players_level = {play : round(abs(rate - flt_levelWanted), 1)  for (play, rate) in d_players.items()} 
            if bl_print:    display_team(d_players_level)
            d_players_level = {play : round(abs(rate - flt_levelWanted) * i_numPlayer, 1)  for (play, rate) in d_players.items()} 
            if bl_print:    display_team(d_players_level)
            # str_player = min(d_players_level, key = d_players_level.get)
            # print('   ', str_player)
            
            ## Add some randomness
            d_playersLevel_Random = fDict_addListToDictValues(d_players_level, l_randomlist)
            if bl_print:    print('   ', l_randomlist)
            if bl_print:    display_team(d_playersLevel_Random)
            # Get the right player
            str_player = min(d_playersLevel_Random, key = d_playersLevel_Random.get)
            if bl_print:    print('   Color Player chosen: ', str_player, '\n')
            # Add the player to white team
            l_teamColor.append(str_player)
            int_ColorScore += round(d_players[str_player], 2)
            del d_players[str_player]
            
    # Before Return, sort the players
    # l_teamWhite[0], l_teamWhite[3] = l_teamWhite[3], l_teamWhite[0]
    # l_teamWhite[-1], l_teamWhite[-4] = l_teamWhite[-4], l_teamWhite[-1]
    # l_teamColor[0], l_teamColor[4] = l_teamColor[4], l_teamColor[0]
    # l_teamColor[-1], l_teamColor[-3] = l_teamColor[-3], l_teamColor[-1]

    return l_teamWhite, int_WhiteScore, l_teamColor, int_ColorScore


#=============================================================================

# Get the PLayers
try:
    df_players = pd.read_excel(r'..\..\0_CompanyCopy\0_Personal_doc\SCAA Tuesdays Football.xlsx', 
                               sheet_name = 'Team', header = 0, index_col = None,
                               dtype={'Player':str,'Rate':float})
    print('here')
except:
    str_path = r'C:\Users\laurent.tupin\OneDrive - IHS Markit\Documents\Github\0_CompanyCopy\0_Personal_doc'
    df_players = pd.read_excel(str_path + r'\SCAA Tuesdays Football.xlsx', 
                               sheet_name = 'Team', header = 0, index_col = None,
                               dtype={'Player':str,'Rate':float})
    print('there')

# Fill the dictionary
d_players = {}
for index, row in df_players.iterrows():
    if np.isnan(row['Rate']):   print('The player has a rate which is not a number: ', (row['Player']))
    else:                       d_players[row['Player']] = row['Rate']
# display_team(d_players)


if len(d_players) <= 12:
    l_wh, i_w, l_col, i_col = f_BuildTeams(d_players, bl_print = False)
    bl_15 = False
elif len(d_players) <= 15:
    l_wh, i_w, l_col, i_col, l_red, i_red = f_BuildTeams_15(d_players, bl_print = False)
    bl_15 = True
    
    
# Print the result    
print(' White team:')
random.shuffle(l_wh)
display_teamList(l_wh)
print('  * White score:', round(i_w, 2), '\n')

print(' Color team: ')
random.shuffle(l_col)
display_teamList(l_col)
print('  * Color score:', round(i_col, 2), '\n')

if bl_15:
    print(' Red team: ')
    random.shuffle(l_red)
    display_teamList(l_red)
    print('  * Red score:', i_red, '\n')




