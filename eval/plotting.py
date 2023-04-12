from pathlib import Path
import numpy as np
from numpy import pi
import pandas as pd
import matplotlib.pyplot as plt 

optimal = {
    'conceding_speed': 0.00001,
    'decay_exp': 0.3,
    'threshold': 0.985
}

def plot_results(key, folders):
    '''
    Plots the results for a given key (parameter) name and directory
    '''

    fig, ax1 = plt.subplots()
    ax1.set_title(f'{key} ({folders[0]} and {folders[1]} agents)')
    ax2 = ax1.twinx()

    ax2.set_ylabel('Number of offers')
    ax2.set_ylim(0, 3000)
    ax1.set_xlabel(key)
    ax1.set_ylabel('Utility')
    ax1.set_ylim(0.3, 1.5)

    # For the respective key, plot a vertical line at the optimal value
    ax1.axvline(optimal[key], color='black', linestyle='--')

    # if key == 'concending_speed' then set x axis to logarithmic scale
    if key == 'conceding_speed':
        ax1.set_xscale('log')

    for i, folder in enumerate(folders):
        # get all dirs that start with key
        dirs = [d for d in Path(folder).iterdir() if d.name.startswith(key)]

        # Read the Group62Agent row from the 'tournament_results_summary.csv' file from each directory,
        # creating a dictionary from the key to the row 
        dfs = {float(d.name.split(': ')[1]): pd.read_csv(d / 'tournament_results_summary.csv', index_col=0).loc['Group62Agent'] for d in dirs}

        # sort the dictionary on its keys
        dfs = {k: dfs[k] for k in sorted(dfs.keys())}

        # Create a plot with keys on the x axis, and dataframe entries on y axes 
        df = pd.concat(dfs, axis=1).T

        if i == 0:
            ax1.plot(df.index, df['avg_utility'], label=f'Avg. utility ({folder}) ', color='blue')
            ax1.plot(df.index, df['avg_nash_product'], label=f'Avg. Nash product ({folder})', color='orange')
            ax1.plot(df.index, df['avg_social_welfare'], label=f'Avg. Social welfare ({folder})', color='green')

            ax2.plot(df.index, df['avg_num_offers'], label=f'Num. offers ({folder})', color='red')

        else: # plot the same but with a dashed line
            ax1.plot(df.index, df['avg_utility'], label=f'Avg. utility ({folder})', linestyle='--', color='blue')
            ax1.plot(df.index, df['avg_nash_product'], label=f'Avg. Nash product ({folder})', linestyle='--', color='orange')
            ax1.plot(df.index, df['avg_social_welfare'], label=f'Avg. Social welfare ({folder})', linestyle='--', color='green')

            ax2.plot(df.index, df['avg_num_offers'], label=f'Num. offers ({folder})', color='red', linestyle='--')

    # Place legend in bottom left corner for 'threshold', otherwise in top right
    if key == 'threshold':
        ax1.legend(loc='lower left')
    else:
        ax1.legend(loc='upper right')
    ax2.legend(loc='lower right')


    # Save the plot with the same title as the dataframe
    plt.savefig(f'{key} ({folder} agents).png')


def plot_comparison(folder, keys = ['avg_utility', 'avg_social_welfare', 'avg_num_offers'], run=0):
    '''Plots comparison of agents in the provided folder, sorting them on the provided key'''

    # Folder is of format 'comparison_{key}_0'
    # Average the results from the five domains, which are given as 'tournament_results_summary_i.csv' 
    # where i is the domain number
    directory = f'comparison_{folder}_{run}'

    # Create list of all existing file paths
    files = [Path(directory) / f'tournament_results_summary_{i}.csv' for i in range(5)]
    files = [f for f in files if f.exists()]

    # Read all files, and average the results
    df = pd.concat([pd.read_csv(f, index_col=0) for f in files]).groupby(level=0).mean()

    df = df.sort_values(keys)

    fig, ax = plt.subplots()
    # Create a bar chart with indexes on the x axis and the provided key on the y axis
    df[keys[1]].plot(secondary_y=True, color='green')
    df[keys[0]].plot.bar(title=f'Agent Comparison with {folder}', alpha=0.5)
    
    # Set ylabel to 'Average Utility', secondary y label to 'Average Social Welfare'
    ax.set_ylabel('Average Utility')
    ax.right_ax.set_ylabel('Average Social Welfare')

    # Set the title of the plot to the provided key
    plt.savefig(f'Agent Comparison with {folder}.png')

    plt.tight_layout()

    # Also print the 'avg_num_offers' of Group62Agent, and the averaged for the five top agents
    print(f"[{folder}] Our agent averages {df.loc['Group62Agent', 'avg_num_offers']:.2f} offers, while the top five agents average {df.iloc[:5]['avg_num_offers'].mean():.2f} offers")

    # similarly, print the failed column statistic
    print(f"[{folder}] Our agent failed {df.loc['Group62Agent', 'failed']:.2f} times, while the top five agents failed {df.iloc[:5]['failed'].mean():.2f} times")

    return df 


def plot_with_itself(keys = ['avg_utility', 'avg_nash_product', 'avg_social_welfare', 'avg_num_offers', 'error'], run=0):
    '''
    Creates a radar chart of the provided keys for the provided folder
    '''
    # Read the eval/Group62Agent_{ver}/tournament_results_summary.csv file for ver {'new', 'old'},
    # plotting the row for Group62Agent and Group62AgentOld on the same radar chart

    new_df = pd.read_csv(Path(f'eval/Group62Agent_new_{run}') / 'tournament_results_summary.csv', index_col=0).loc['Group62Agent']
    old_df = pd.read_csv(Path(f'eval/Group62Agent_old_{run}') / 'tournament_results_summary.csv', index_col=0).loc['Group62AgentOld']

    # Plot on a radar chart
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='polar')

    new_df.plot()
    old_df.plot()

    plt.legend(['New', 'Old'])

    plt.savefig(f'Group62Agent comparison.png')



####################################################################################################
## NOTE: Plotting Comparisons
####################################################################################################



# for folder in ['CSE3210', 'ANL2022']:
#     plot_comparison(folder)




####################################################################################################
## NOTE: Plotting Results
####################################################################################################

keys = ['conceding_speed', 'decay_exp', 'threshold']
# folders = ['default', 'cse', 'anl', 'group62']

for key in keys:
    plot_results(key, ['default', 'cse'])