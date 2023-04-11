from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 

keys = ['conceding_speed', 'decay_exp', 'threshold']
folders = ['default', 'cse', 'anl', 'group62']

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


for folder in folders:
    for key in keys:
        plot_results(key, folder) 