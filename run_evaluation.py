import json
import os
from pathlib import Path
import time

from agents.group62_agent.utils.opponent_model import DECAY_EXP
from agents.group62_agent.utils.acceptance_strategy import THRESHOLD
from agents.group62_agent.utils.bidding_strategy import CONCEDING_SPEED, RESERVATION_VALUE, ISO_TOLERANCE

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
agents_ANL2022 = [
            # {
            #     "class": "agents.ANL2022.Pinar_Agent.Pinar_Agent.PinarAgent",
            #     "parameters": {"storage_dir": "agent_storage/PinarAgent"},
            # },
            {
                "class": "agents.ANL2022.agent007.agent007.Agent007",
                "parameters": {"storage_dir": "agent_storage/Agent007"},
            },
            {
                "class": "agents.ANL2022.agent4410.agent_4410.Agent4410",
                "parameters": {"storage_dir": "agent_storage/Agent4410"},
            },
            {
                "class": "agents.ANL2022.agentfish.agentfish.AgentFish",
                "parameters": {"storage_dir": "agent_storage/AgentFish"},
            },
            {
                "class": "agents.ANL2022.AgentFO2.AgentFO2.AgentFO2",
                "parameters": {"storage_dir": "agent_storage/AgentFO2"},
            },
            {
                "class": "agents.ANL2022.BIU_agent.BIU_agent.BIU_agent",
                "parameters": {"storage_dir": "agent_storage/BIU_agent"},
            },
            {
                "class": "agents.ANL2022.charging_boul.charging_boul.ChargingBoul",
                "parameters": {"storage_dir": "agent_storage/ChargingBoul"},
            },
            {
                "class": "agents.ANL2022.compromising_agent.compromising_agent.CompromisingAgent",
                "parameters": {"storage_dir": "agent_storage/CompromisingAgent"},
            },
            {
                "class": "agents.ANL2022.dreamteam109_agent.dreamteam109_agent.DreamTeam109Agent",
                "parameters": {"storage_dir": "agent_storage/DreamTeam109Agent"},
            },
            {
                "class": "agents.ANL2022.gea_agent.gea_agent.GEAAgent",
                "parameters": {"storage_dir": "agent_storage/GEAAgent"},
            },
            {
                "class": "agents.ANL2022.learning_agent.learning_agent.LearningAgent",
                "parameters": {"storage_dir": "agent_storage/LearningAgent"},
            },
            {
                "class": "agents.ANL2022.LuckyAgent2022.LuckyAgent2022.LuckyAgent2022",
                "parameters": {"storage_dir": "agent_storage/LuckyAgent2022"},
            },
            {
                "class": "agents.ANL2022.micro_agent.micro_agent.micro_agent.MiCROAgent",
                "parameters": {"storage_dir": "agent_storage/MicroAgent"},
            },
            {
                "class": "agents.ANL2022.procrastin_agent.procrastin_agent.ProcrastinAgent",
                "parameters": {"storage_dir": "agent_storage/ProcrastinAgent"},
            },
            {
                "class": "agents.ANL2022.rg_agent.rg_agent.RGAgent",
                "parameters": {"storage_dir": "agent_storage/RgAgent"},
            },
            {
                "class": "agents.ANL2022.super_agent.super_agent.SuperAgent",
                "parameters": {"storage_dir": "agent_storage/SuperAgent"},  
            },
            {
                "class": "agents.ANL2022.thirdagent.third_agent.ThirdAgent",
                "parameters": {"storage_dir": "agent_storage/ThirdAgent"},
            },
            {
                "class": "agents.ANL2022.tjaronchery10_agent.tjaronchery10_agent.Tjaronchery10Agent",
                "parameters": {"storage_dir": "agent_storage/Tjaronchery10Agent"},
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

profile_sets = [
            ["domains/domain00/profileA.json", "domains/domain00/profileB.json"],
            ["domains/domain01/profileA.json", "domains/domain01/profileB.json"],
            ["domains/domain02/profileA.json", "domains/domain02/profileB.json"],
            ["domains/domain03/profileA.json", "domains/domain03/profileB.json"],
            ["domains/domain04/profileA.json", "domains/domain04/profileB.json"],
        ]

def run_optimisation(params, path='results', key='', agents=agents_default, profile_sets=None):
    '''Runs a tournament with specified parameters'''

    conceding_speed = params.get('conceding_speed', 0.000045) if params else 0.000045
    reservation_value = params.get('reservation_value', 0.95) if params else 0.95
    iso_tolerance = params.get('iso_tolerance', 0.05) if params else 0.05
    threshold = params.get('threshold', 0.98) if params else 0.98
    decay_exp = params.get('decay_exp', 0.4) if params else 0.4

    print(f"Running tournament: {path} {key}:{params.get(key)}")
    RESULTS_DIR = Path(path, f'{params}')

    # create results directory if it does not exist
    if not RESULTS_DIR.exists():
        RESULTS_DIR.mkdir(parents=True)
    else:
        # add a number to end of directory name if it already exists
        RESULTS_DIR = Path(str(RESULTS_DIR) + str(len(list(RESULTS_DIR.parent.glob(f'{RESULTS_DIR.name}*')))))
        RESULTS_DIR.mkdir(parents=True)

    agent_list = [{
                # "class": "agents.group62_agent.group62_agent.Group62Agent",
                # "parameters": {"storage_dir": "agent_storage/Group62Agent",
                #             "bidding_strategy": {
                #                     "conceding_speed": conceding_speed,
                #                     "reservation_value": reservation_value,
                #                     "iso_tolerance": iso_tolerance,
                #             },
                #             "acceptance_strategy": {
                #                     "threshold": threshold,
                #             },
                #             "opponent_model": {
                #                     "decay": (decay_exp >= 0), # true if exp provided
                #                     "decay_exp": decay_exp,
                #             },
                #         }
                "class": "agents.group62_agent_old.group62_agent_old.Group62AgentOld",
                "parameters": {"storage_dir": "agent_storage/Group62AgentOld",}
            }]
    agent_list.extend(agents)

    tournament_settings = {
        "agents": agent_list,
        "profile_sets": profile_sets,
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

def run_comparison(params, path='results', key='', agents=agents_default, profile_sets=None):
    '''Runs a tournament with specified parameters'''

    conceding_speed = CONCEDING_SPEED
    reservation_value = RESERVATION_VALUE
    iso_tolerance = ISO_TOLERANCE
    threshold = THRESHOLD
    decay_exp = DECAY_EXP

    print(f"Running tournament: {path}{key}")
    RESULTS_DIR = Path(path, f'{key}')

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
        "profile_sets": profile_sets,
        "deadline_time_ms": 10000,
    }

    # NOTE: Select a type of tournament. Selfish only runs first profile against every other profile.
    tournament_steps, tournament_results, tournament_results_summary = run_tournament(tournament_settings, ask=False)
    # tournament_steps, tournament_results, tournament_results_summary = run_selfish_tournament(tournament_settings, ask=False, play_with_itself=False)

    # save the tournament settings for reference
    with open(RESULTS_DIR.joinpath("tournament_steps.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(tournament_steps, indent=2))
    # save the tournament results
    with open(RESULTS_DIR.joinpath("tournament_results.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(tournament_results, indent=2))
    # save the tournament results summary
    # convert all numbers in the CSV to :.2f
    tournament_results_summary.to_csv(RESULTS_DIR.joinpath("tournament_results_summary.csv"))



import logging 
logging.getLogger('geniusweb').disabled = True # disable all messages from geniusweb
import numpy as np


#### NOTE: AGENT COMPARISON

## CSE AGENTS
# import threading
# for i, profile_set in enumerate(profile_sets):

#     # use threading for CSE agents
#     print(f'Running tournament for profile set {i}: {profile_set}')
#     t = threading.Thread(target=run_comparison, args=(None, f'eval2/comparison_cse_{i}', '', agents_CSE3210, [profile_set]))
#     t.start()

## ANL AGENTS
# i = 4
# profile_set = profile_sets[i]
# print(f'Running tournament for profile set {i}: {profile_set}')
# # don't use threading for ANL agents
# run_comparison(None, f'eval/comparison_ANL2022_{i}', '', agents_ANL2022, [profile_set])

## VS ITSELF
# run optimisation 
all_agents = agents_default + agents_CSE3210 + agents_ANL2022
run_optimisation({}, 'eval3/optimisation', '', all_agents, profile_sets)



# #### NOTE: PARAMETER OPTIMISATION
# # Generate linspaces for each parameter
# conceding_speeds = np.logspace(-6, -2, 20).tolist()
# thresholds = np.linspace(0.80, 0.999, 20).tolist()
# decay_exps = np.linspace(0.1, 1, 20).tolist()


# # Ideally, we generate a grid of all possible combinations of parameters, but that's 100 evaluations
# # which I don't think we have time for. Instead, just run each parameter individually.

# agents = agents_default

# # print(f'Running tournament for conceding speeds: {conceding_speeds}')
# # for conceding_speed in conceding_speeds:
# #     run({'conceding_speed': conceding_speed}, path="eval3/default", key='conceding_speed', agents=agents)

# print(f'Running tournament for thresholds: {thresholds}')
# for threshold in thresholds:
#     print(f'Running tournament for threshold {threshold}')
#     run_optimisation({'threshold': threshold}, path="eval/cse/", key='threshold', agents=agents_CSE3210, profile_sets=profile_sets)

# Do the threshold thingy above but on multiple threads 
# import threading
# for i, profile_set in enumerate(profile_sets):
#     print(f'Running tournament for profile set {i}: {profile_set}')
#     t = threading.Thread(target=run_optimisation, args=({'threshold': 0.9}, f'eval/cse/', 'threshold', agents_CSE3210, [profile_set]))
#     t.start()

# for i, threshold in enumerate(thresholds):
#     print(f'Running tournament for threshold {i}: {threshold}')
#     t = threading.Thread(target=run_optimisation, args=({'threshold': threshold}, f'eval/cse/', 'threshold', agents_CSE3210, profile_sets))
#     t.start()

# print(f'Running tournament for decay exps: {decay_exps}')
# for decay_exp in decay_exps:
#     run({'decay_exp': decay_exp}, path="eval3/default", key='decay_exp', agents=agents)

