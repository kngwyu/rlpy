import click
from rlpy.Domains import GridWorld
from rlpy.Tools.cli import run_experiment

import methods

MAX_STEPS = 10000


def select_domain(map_="4x5", **kwargs):
    map_ = GridWorld.default_map(map_ + ".txt")
    return GridWorld(map_, random_start=True, noise=0.1)


def select_agent(name, domain, _seed, **kwargs):
    if name is None or name == "lspi":
        return methods.tabular_lspi(domain, MAX_STEPS)
    elif name == "nac":
        return methods.tabular_nac(domain)
    elif name == "tabular-q":
        return methods.tabular_q(domain, initial_learn_rate=0.11)
    elif name == "ifddk-q":
        return methods.tabular_q(domain, initial_learn_rate=0.11)
    else:
        raise NotImplementedError("Method {} is not supported".format(name))


if __name__ == "__main__":
    run_experiment(
        select_domain,
        select_agent,
        default_max_steps=MAX_STEPS,
        default_num_policy_checks=10,
        default_checks_per_policy=50,
        other_options=[
            click.Option(["--map", "map_"], type=str, default="4x5"),
            click.Option(["--noise"], type=float, default=0.1),
        ],
    )
