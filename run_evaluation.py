import json
import os
from pathlib import Path
import time

from utils.runners import run_tournament, run_selfish_tournament

agents_default = [
            {
                "class": "agents.boulware_agent.boulware_agent.BoulwareAgent",
            },
            {
                "class": "agents.conceder_agent.conceder_agent.ConcederAgent",
            },
            {
                "class": "agents.hardliner_agent.hardliner_agent.HardlinerAgent",
            },
            {
                "class": "agents.linear_agent.linear_agent.LinearAgent",
            },
            {
                "class": "agents.random_agent.random_agent.RandomAgent",
            },
            {
                "class": "agents.stupid_agent.stupid_agent.StupidAgent",
            },
            {
                "class": "agents.template_agent.template_agent.TemplateAgent",
                "parameters": {"storage_dir": "agent_storage/TemplateAgent"},
            },
            {
                "class": "agents.time_dependent_agent.time_dependent_agent.TimeDependentAgent",
            }]
agents_ANL2022 = [{
                "class": "agents.ANL2022.Pinar_Agent.Pinar_Agent.PinarAgent",
                "parameters": {"storage_dir": "agent_storage/PinarAgent"},
            },
            {
                "class": "agents.ANL2022.dreamteam109_agent.dreamteam109_agent.DreamTeam109Agent",
                "parameters": {"storage_dir": "agent_storage/DreamTeam109Agent"},
            },
            {
                "class": "agents.ANL2022.smart_agent.smart_agent.SmartAgent",
                "parameters": {"storage_dir": "agent_storage/SmartAgent"},
            }]
agents_CSE3210 = [
            {
                "class": "agents.CSE3210.agent2.agent2.Agent2",
            },
            {
                "class": "agents.CSE3210.agent3.agent3.Agent3",
            },
            {
                "class": "agents.CSE3210.agent7.agent7.Agent7",
            },
            {
                "class": "agents.CSE3210.agent11.agent11.Agent11",
            },
            {
                "class": "agents.CSE3210.agent14.agent14.Agent14",
            },
            {
                "class": "agents.CSE3210.agent18.agent18.Agent18",
            },
            {
                "class": "agents.CSE3210.agent19.agent19.Agent19",
            },
            {
                "class": "agents.CSE3210.agent22.agent22.Agent22",
            },
            {
                "class": "agents.CSE3210.agent24.agent24.Agent24",
            },
            {
                "class": "agents.CSE3210.agent25.agent25.Agent25",
            },
            {
                "class": "agents.CSE3210.agent26.agent26.Agent26",
            },
            {
                "class": "agents.CSE3210.agent27.agent27.Agent27",
            },
            {
                "class": "agents.CSE3210.agent29.agent29.Agent29",
            },
            {
                "class": "agents.CSE3210.agent32.agent32.Agent32",
            },
            {
                "class": "agents.CSE3210.agent33.agent33.Agent33",
            },
            {
                "class": "agents.CSE3210.agent41.agent41.Agent41",
            },
            {
                "class": "agents.CSE3210.agent43.agent43.Agent43",
            },
            {
                "class": "agents.CSE3210.agent50.agent50.Agent50",
            },
            {
                "class": "agents.CSE3210.agent52.agent52.Agent52",
            },
            {
                "class": "agents.CSE3210.agent55.agent55.Agent55",
            },
            {
                "class": "agents.CSE3210.agent58.agent58.Agent58",
            },
            {
                "class": "agents.CSE3210.agent61.agent61.Agent61",
            },
            {
                "class": "agents.CSE3210.agent64.agent64.Agent64",
            },
            {
                "class": "agents.CSE3210.agent67.agent67.Agent67",
            },
            {
                "class": "agents.CSE3210.agent68.agent68.Agent68",
            }]


def run(params, path='results', key='', agents=agents_default):
    '''Runs a tournament with specified parameters'''

    conceding_speed = params.get('conceding_speed', 0.000045)
    reservation_value = params.get('reservation_value', 0.95)
    iso_tolerance = params.get('iso_tolerance', 0.05)
    threshold = params.get('threshold', 0.98)
    decay_exp = params.get('decay_exp', 0.4)

    print(f"Running tournament: {key} = {params.get(key):.5f}")
    RESULTS_DIR = Path(path, f'{key}: {params.get(key):.5f}')

    # create results directory if it does not exist
    if not RESULTS_DIR.exists():
        RESULTS_DIR.mkdir(parents=True)
    else:
        # add a number to end of directory name if it already exists
        RESULTS_DIR = Path(str(RESULTS_DIR) + str(len(list(RESULTS_DIR.parent.glob(f'{RESULTS_DIR.name}*')))))
        RESULTS_DIR.mkdir(parents=True)

    agent_list = [{
                "class": "agents.group62_agent.group62_agent.Group62Agent",
                "parameters": {"storage_dir": "agent_storage/Group62Agent",
                            "bidding_strategy": {
                                    "conceding_speed": conceding_speed,
                                    "reservation_value": reservation_value,
                                    "iso_tolerance": iso_tolerance,
                            },
                            "acceptance_strategy": {
                                    "threshold": threshold,
                            },
                            "opponent_model": {
                                    "decay": (decay_exp >= 0), # true if exp provided
                                    "decay_exp": decay_exp,
                            },
                        }
            }]
    agent_list.extend(agents)

    tournament_settings = {
        "agents": agent_list,
        "profile_sets": [
            ["domains/domain00/profileA.json", "domains/domain00/profileB.json"],
            ["domains/domain01/profileA.json", "domains/domain01/profileB.json"],
            ["domains/domain02/profileA.json", "domains/domain02/profileB.json"],
            ["domains/domain03/profileA.json", "domains/domain03/profileB.json"],
            ["domains/domain04/profileA.json", "domains/domain04/profileB.json"],
        ],
        "deadline_time_ms": 10000,
    }

    # NOTE: Select a type of tournament. Selfish only runs first profile against every other profile.
    # tournament_steps, tournament_results, tournament_results_summary = run_tournament(tournament_settings, ask=False)
    tournament_steps, tournament_results, tournament_results_summary = run_selfish_tournament(tournament_settings, ask=False, play_with_itself=False)

    # save the tournament settings for reference
    with open(RESULTS_DIR.joinpath("tournament_steps.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(tournament_steps, indent=2))
    # save the tournament results
    with open(RESULTS_DIR.joinpath("tournament_results.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(tournament_results, indent=2))
    # save the tournament results summary
    # convert all numbers in the CSV to :.2f
    tournament_results_summary.to_csv(RESULTS_DIR.joinpath("tournament_results_summary.csv"))


# run(info='default')

# Possible ranges for values:
# conceding_speed: 0.000001 - 0.0005
# threshold: 0.950 - 0.999
# decay_exp: 0.1 - 1 

# Fucking hell of a workaround
import logging 
logging.getLogger('geniusweb').disabled = True # disable all messages from geniusweb

import numpy as np
# Generate linspaces for each parameter
conceding_speeds = np.logspace(-6, -2, 20).tolist()
thresholds = np.linspace(0.50, 0.999, 20).tolist()
decay_exps = np.linspace(0.1, 1, 20).tolist()


# Ideally, we generate a grid of all possible combinations of parameters, but that's 100 evaluations
# which I don't think we have time for. Instead, just run each parameter individually.

agents = agents_default

# print(f'Running tournament for conceding speeds: {conceding_speeds}')
# for conceding_speed in conceding_speeds:
#     run({'conceding_speed': conceding_speed}, path="eval3/default", key='conceding_speed', agents=agents)

# print(f'Running tournament for thresholds: {thresholds}')
# for threshold in thresholds:
#     run({'threshold': threshold}, path="eval3/default", key='threshold', agents=agents)

print(f'Running tournament for decay exps: {decay_exps}')
for decay_exp in decay_exps:
    run({'decay_exp': decay_exp}, path="eval3/default", key='decay_exp', agents=agents)

