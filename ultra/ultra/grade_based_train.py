# MIT License
#
# Copyright (C) 2021. Huawei Technologies Co., Ltd. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import json
import os
import sys
import numpy as np

from ultra.utils.ray import default_ray_kwargs

# Set environment to better support Ray
os.environ["MKL_NUM_THREADS"] = "1"
import argparse
import pickle
import time

import dill
import gym
import psutil
import ray
import torch
import matplotlib.pyplot as plt

from smarts.zoo.registry import make
from ultra.evaluate import evaluation_check
from ultra.utils.episode import episodes, LogInfo
from ultra.utils.coordinator import coordinator
from itertools import cycle

num_gpus = 1 if torch.cuda.is_available() else 0

plot_name = ""

# @ray.remote(num_gpus=num_gpus / 2, max_calls=1)
@ray.remote(num_gpus=num_gpus / 2)
def train(
    scenario_info,
    num_episodes,
    max_episode_steps,
    policy_class,
    eval_info,
    timestep_sec,
    headless,
    seed,
    log_dir,
):
    torch.set_num_threads(1)
    total_step = 0
    finished = False

    AGENT_ID = "007"

    spec = make(locator=policy_class, max_episode_steps=max_episode_steps)
    env = gym.make(
        "ultra.env:ultra-v0",
        agent_specs={AGENT_ID: spec},
        scenario_info=(scenario_info[0], (scenario_info[1].split(","))[0]),
        headless=headless,
        timestep_sec=timestep_sec,
        seed=seed,
    )

    agent = spec.build_agent()

    episode_count = 0
    old_episode = None

    agent_coordinator = coordinator("../scenarios/grade_based_task/")
    # agent_coordinator.build_all_scenarios()
    counter = cycle(
        tuple([i * 1 for i in range(agent_coordinator.get_num_of_grades())])
    )

    env_score_list = []

    for episode in episodes(num_episodes, etag=policy_class, log_dir=log_dir):
        if (
            episode.index % (num_episodes / agent_coordinator.get_num_of_grades())
        ) == 0:
            agent_coordinator.next_grade(next(counter) + 1)
            observations = env.reset(True, agent_coordinator.get_grade())
            print(agent_coordinator)
        else:
            observations = env.reset()
            # print(agent_coordinator)

        state = observations[AGENT_ID]
        dones, infos = {"__all__": False}, None
        episode.reset()
        experiment_dir = episode.experiment_dir

        # save entire spec [ policy_params, reward_adapter, observation_adapter]
        if not os.path.exists(f"{experiment_dir}/spec.pkl"):
            if not os.path.exists(experiment_dir):
                os.makedirs(experiment_dir)
            with open(f"{experiment_dir}/spec.pkl", "wb") as spec_output:
                dill.dump(spec, spec_output, pickle.HIGHEST_PROTOCOL)

        while not dones["__all__"]:
            if episode.get_itr(AGENT_ID) >= 1000000:
                finished = True
                break
            action = agent.act(state, explore=True)
            observations, rewards, dones, infos = env.step({AGENT_ID: action})
            next_state = observations[AGENT_ID]

            loss_output = agent.step(
                state=state,
                action=action,
                reward=rewards[AGENT_ID],
                next_state=next_state,
                done=dones[AGENT_ID],
                info=infos[AGENT_ID],
            )
            episode.record_step(
                agent_id=AGENT_ID,
                infos=infos,
                rewards=rewards,
                total_step=total_step,
                loss_output=loss_output,
            )
            total_step += 1
            state = next_state

        episode.record_episode(old_episode, eval_info["eval_rate"])
        old_episode = episode

        if (episode_count + 1) % eval_info["eval_rate"] == 0:
            episode.record_tensorboard()
            old_episode = None

        if (eval_info["eval_episodes"] != 0 ):
            evaluation_check(
                agent=agent,
                agent_id=AGENT_ID,
                policy_class=policy_class,
                episode=episode,
                log_dir=log_dir,
                max_episode_steps=max_episode_steps,
                episode_count=episode_count,
                agent_coordinator=agent_coordinator,
                **eval_info,
                **env.info,
            )
        episode_count += 1

        env_score_list.append(episode.info[episode.active_tag][AGENT_ID].data["reached_goal"])

        if finished:
            break

    # for key, val in summary_log.data.items():
    #     if not isinstance(val, (list, tuple, np.ndarray)):
    #         summary_log.data[key] /= num_episodes
    #         print(f"{key}: {summary_log.data[key]}")

    # print(f">>>>>>>>>>>>>>>> Scenario success : {scenario_success} <<<<<<<<<<<<<<<<<<")

    x_list = [i for i in range(num_episodes)]

    # print("x axis length:",len(x_list))
    # print("y axis length:",len(env_score_list))
    plt.scatter(x_list, env_score_list)
    plt.plot(x_list, env_score_list)

    # x coordinates for the lines
    xcoords = [100]
    # colors for the lines
    colors = ['r']

    for xc,c in zip(xcoords,colors):
        plt.axvline(x=xc, label='line at x = {}'.format(xc), c=c)

    plt.legend()
    
    plt.savefig(plot_name)
    # for key, val in summary_log.data.items():
    #     if not isinstance(val, (list, tuple, np.ndarray)):
    #         summary_log.data[key] /= num_episodes
    #         print(f"{key}: {summary_log.data[key]}")
    env.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("intersection-single-agent")
    parser.add_argument(
        "--task", help="Tasks available : [0, 1, 2]", type=str, default="1"
    )
    parser.add_argument(
        "--level",
        help="Levels available : [easy, medium, hard, no-traffic]",
        type=str,
        default="easy",
    )
    parser.add_argument(
        "--policy",
        help="Policies available : [ppo, sac, ddpg, dqn, bdqn]",
        type=str,
        default="sac",
    )
    parser.add_argument(
        "--episodes", help="Number of training episodes", type=int, default=1000000
    )
    parser.add_argument(
        "--max-episode-steps",
        help="Maximum number of steps per episode",
        type=int,
        default=10000,
    )
    parser.add_argument(
        "--timestep", help="Environment timestep (sec)", type=float, default=0.1
    )
    parser.add_argument(
        "--headless", help="Run without envision", type=bool, default=False
    )
    parser.add_argument(
        "--eval-episodes", help="Number of evaluation episodes", type=int, default=200
    )
    parser.add_argument(
        "--eval-rate",
        help="Evaluation rate based on number of episodes",
        type=int,
        default=100,
    )
    parser.add_argument(
        "--seed",
        help="Environment seed",
        default=2,
        type=int,
    )
    parser.add_argument(
        "--log-dir",
        help="Log directory location",
        default="logs",
        type=str,
    )
    parser.add_argument(
        "--plot-name",
        help="name of plot",
        default="foo.png",
        type=str,
    )

    base_dir = os.path.dirname(__file__)
    pool_path = os.path.join(base_dir, "agent_pool.json")
    args = parser.parse_args()

    with open(pool_path, "r") as f:
        data = json.load(f)
        if args.policy in data["agents"].keys():
            policy_path = data["agents"][args.policy]["path"]
            policy_locator = data["agents"][args.policy]["locator"]
        else:
            raise ImportError("Invalid policy name. Please try again")

    # Required string for smarts' class registry
    policy_class = str(policy_path) + ":" + str(policy_locator)

    plot_name = args.plot_name

    ray.init()
    ray.wait(
        [
            train.remote(
                scenario_info=(args.task, args.level),
                num_episodes=int(args.episodes),
                max_episode_steps=int(args.max_episode_steps),
                eval_info={
                    "eval_rate": int(args.eval_rate),
                    "eval_episodes": int(args.eval_episodes),
                },
                timestep_sec=float(args.timestep),
                headless=args.headless,
                policy_class=policy_class,
                seed=args.seed,
                log_dir=args.log_dir,
            )
        ]
    )