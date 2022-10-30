import csv
import os

import numpy as np

from utilities.utilities import datetime_string, euclidean, automkdir


def log_results(
        pars, random_seed, t_taken_sec, route_as_visited, all_memory,
        n_missed_waypoints, dist_init, minimum_hamiltonian_path_distance,
        logfile_path=None
):
    if logfile_path is None:
        logfile_path = f"./logfiles/{datetime_string()}_log.csv"
    wpt_num_first_damage, dist_first_damage, wpt_num_last_damage, dist_last_damage, dist_of_traveled_route = None, None, None, None, 0
    dist_of_traveled_route = sum(euclidean(p1, p2)
                                 for p1, p2 in
                                 zip(route_as_visited, route_as_visited[1:]))
    if any(all_memory):
        for i, (p1, dmg) in enumerate(zip(route_as_visited, all_memory)):
            if dmg:
                wpt_num_first_damage = i
                dist_first_damage = sum(euclidean(p1, p2)
                                        for p1, p2 in
                                        zip(route_as_visited[:i], route_as_visited[1:]))
                break
        for i, (p1, dmg) in enumerate(zip(route_as_visited, all_memory)):
            if dmg:
                wpt_num_last_damage = i
                dist_last_damage = sum(euclidean(p1, p2)
                                       for p1, p2 in
                                       zip(route_as_visited[:i], route_as_visited[1:]))
    else:
        wpt_num_first_damage = None
        dist_first_damage = None
        wpt_num_last_damage = None
        dist_last_damage = None

    n_damaged = sum(all_memory) + n_missed_waypoints

    if dist_last_damage is None or dist_first_damage is None:
        delta_dist, delta_wpt = None, None
        score_as_dist,  score_as_wp = None, None
    else:
        delta_dist = dist_last_damage - dist_first_damage
        delta_wpt = wpt_num_last_damage - wpt_num_first_damage
        score_as_dist = delta_dist / minimum_hamiltonian_path_distance
        score_as_wp = delta_wpt / n_damaged

    row = [
        datetime_string(current=True),

        t_taken_sec,

        datetime_string(),
        random_seed,
        pars["routing_mode"],
        pars["init_route"],

        wpt_num_first_damage,
        dist_first_damage,
        wpt_num_last_damage,
        dist_last_damage,

        delta_dist,
        delta_wpt,

        minimum_hamiltonian_path_distance,
        n_damaged,

        score_as_dist,
        score_as_wp,

        dist_init,
        dist_of_traveled_route,
        n_missed_waypoints,

        pars["case_name"],

        pars["min_score_to_consider"],
        pars["influence_matrix_type"],
        pars["max_influence"],
        pars["mag_limit"],
        pars["bin_width"],

    ]
    header = [
        "datetime",

        "Time taken sec",

        "datetime_str data",
        "random_seed",
        "routing_mode",
        "init_route",

        "waypoint when first damage is uncovered",
        "distance when first damage is uncovered",
        "waypoint when all damage is uncovered",
        "distance when all damage is uncovered",

        "distance to uncover damage",
        "waypoints to uncover damage",

        "minimum distance to uncover all damage",
        "number of damaged waypoints",

        "score_as_dist",
        "score_as_wp",

        "distance of initial route",
        "distance of complete route",
        "number of missed damaged points",

        "case_name",

        "min_score_to_consider",
        "symmetric_influence_matrix",
        "max_influence",
        "mag_limit",
        "bin_width"
    ]
    automkdir(logfile_path)
    if os.path.exists(logfile_path):
        header = False
    with open(logfile_path, 'a', newline='') as logfile:
        writer = csv.writer(logfile)
        if header:
            writer.writerow(header)
        writer.writerow(row)
