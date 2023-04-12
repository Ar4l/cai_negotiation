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

def plot_results(key, folder):
    '''
    Plots the results for a given key (parameter) name and directory
    '''
    # get all dirs that start with key
    dirs = [d for d in Path(folder).iterdir() if d.name.startswith(key)]

    # Read the Group62Agent row from the 'tournament_results_summary.csv' file from each directory,
    # creating a dictionary from the key to the row 
    dfs = {float(d.name.split(': ')[1]): pd.read_csv(d / 'tournament_results_summary.csv', index_col=0).loc['Group62Agent'] for d in dirs}

    # sort the dictionary on its keys
    dfs = {k: dfs[k] for k in sorted(dfs.keys())}

    # Create a plot with keys on the x axis, and dataframe entries on y axes 
    df = pd.concat(dfs, axis=1).T

    fig, ax1 = plt.subplots()
    ax1.plot(df.index, df['avg_utility'], label='avg_utility')
    ax1.plot(df.index, df['avg_nash_product'], label='avg_nash_product')
    ax1.plot(df.index, df['avg_social_welfare'], label='avg_social_welfare')
    ax1.set_xlabel(key)
    ax1.set_ylabel('Utility')
    ax1.set_ylim(0.3, 1.5)
    ax1.set_title(f'{key} ({folder} agents)')
    
    # if key == 'concending_speed' then set x axis to logarithmic scale
    if key == 'conceding_speed':
        ax1.set_xscale('log')

    # For the respective key, plot a vertical line at the optimal value
    ax1.axvline(optimal[key], color='black', linestyle='--')

    ax2 = ax1.twinx()
    ax2.plot(df.index, df['avg_num_offers'], label='avg_num_offers', color='red')
    ax2.set_ylabel('Number of offers')
    ax2.set_ylim(0, 3000)
    # ax2.legend()
    fig.legend()

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
    # Folder is of format 'comparison_Group62Agent_{run}', read dataframe within: 'tournament_results_summary.csv'
    directory = f'comparison_Group62Agent_{run}'
    df = pd.read_csv(Path(directory) / 'tournament_results_summary.csv', index_col=0)

    values = df.loc['Group62Agent', keys].values.flatten().tolist()

    # #Find the values and angles for Messi - from the table at the top of the page
    # values2 = data.iloc[0].tolist()
    # values2 += values2 [:1]

    # angles2 = [n / float(AttNo) * 2 * pi for n in range(AttNo)]
    # angles2 += angles2 [:1]


    # #Create the chart as before, but with both Ronaldo's and Messi's angles/values
    # ax = plt.subplot(111, polar=True)

    # plt.xticks(angles[:-1],Attributes)

    # ax.plot(angles,values)
    # ax.fill(angles, values, 'teal', alpha=0.1)

    # ax.plot(angles2,values2)
    # ax.fill(angles2, values2, 'red', alpha=0.1)

    # #Rather than use a title, individual text points are added
    # plt.figtext(0.2,0.9,"Messi",color="red")
    # plt.figtext(0.2,0.85,"v")
    # plt.figtext(0.2,0.8,"Ronaldo",color="teal")
    # plt.show()

    # plot each row from the dataframe onto the radar chart, using similar code as the snippet above
    for i, row in df.iterrows():
        values = row[keys].tolist()
        values += values [:1]

        angles = [n / float(len(keys)) * 2 * np.pi for n in range(len(keys))]
        angles += angles [:1]

        ax = plt.subplot(111, polar=True)

        plt.xticks(angles[:-1], keys)

        ax.plot(angles, values)
        ax.fill(angles, values, 'teal', alpha=0.1)

        plt.figtext(0.2,0.9,i,color="teal")
        plt.show()







####################################################################################################
## NOTE: Plotting Comparisons
####################################################################################################



for folder in ['CSE3210', 'ANL2022']:
    plot_comparison(folder)




####################################################################################################
## NOTE: Plotting Results
####################################################################################################

# keys = ['conceding_speed', 'decay_exp', 'threshold']
# folders = ['default', 'cse', 'anl', 'group62']

# for folder in ['default', 'cse']:
#     for key in keys:
#         plot_results(key, folder) 