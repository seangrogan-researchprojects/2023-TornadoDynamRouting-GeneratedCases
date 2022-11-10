import random

from matplotlib import pyplot as plt

from pars.parfile_reader import parfile_reader
from route_nearest_insertion import route_nearest_insertion
from utilities.plotter_utilities import plot_with_polygon_case
from utilities.random_case_generator import create_waypoints, create_search_area, create_damage_polygon, \
    create_waypoint_table, create_faux_tornado
from utilities.utilities import automkdir, make_random_seed_list

GLOBAL_OVERRIDES = dict(
    dpi=300,
    bbox_inches="tight"
)





def random_case_plotter_creator(
        random_seed,
        random_case_parfile
):
    base_folder = "C:/Users/seang/OneDrive - polymtl.ca/reasearch-projects/project-archangel/plot_samples_steps/"
    random.seed(random_seed)
    random_case_pars = parfile_reader(random_case_parfile)
    lb_x, ub_x, lb_y, ub_y = random_case_pars["bounds"]
    n_wpt = random_case_pars["n_wpt"]
    waypoints = create_waypoints(lb_x, ub_x, lb_y, ub_y, n_wpt)
    sbw, sbw_vertices = create_search_area(lb_x, ub_x, lb_y, ub_y, **random_case_pars["search_area_pars"])
    minimum_hamiltonian_path_distance, waypoints_to_route = -1, []
    while minimum_hamiltonian_path_distance <= 0 and len(waypoints_to_route) < 2:
        tornado_init, tornado_direction, tornado_length, tornado_width = create_faux_tornado(
            sbw, random_case_pars["tornado_data_file"], lb_x, ub_x, lb_y, ub_y
        )
        damage_polygon = create_damage_polygon(tornado_init, tornado_direction, tornado_length, tornado_width)
        minimum_hamiltonian_path_distance, waypoints_to_route = -1, []
        while minimum_hamiltonian_path_distance <= 0 and len(waypoints_to_route) < 2:
            tornado_init, tornado_direction, tornado_length, tornado_width = create_faux_tornado(
                sbw, random_case_pars["tornado_data_file"], lb_x, ub_x, lb_y, ub_y
            )
            damage_polygon, torn_end = create_damage_polygon(tornado_init, tornado_direction, tornado_length, tornado_width)
            waypoints_data = create_waypoint_table(waypoints, sbw, damage_polygon, 0.5)
            waypoints_to_route = waypoints_data[waypoints_data["damaged"] == True]["_wp"].to_list()
            minimum_hamiltonian_path, minimum_hamiltonian_path_distance = \
                route_nearest_insertion(waypoints_to_route, start_min_arc=False, unknot=True)

    bounds = list(zip(damage_polygon.bounds, sbw.bounds, (lb_x, lb_y, ub_x, ub_y)))
    minx, miny, maxx, maxy = min(bounds[0]), min(bounds[1]), max(bounds[2]), max(bounds[3])
    bounds = (minx, maxx, miny, maxy)

    plot_with_polygon_case(
        waypoints=waypoints,
        sbw=None,
        sbw_verts=None,
        damage_poly=None,
        tornado_point=None,
        bounds=bounds,
        show=False,
        title="Waypoints",
        path=f"{base_folder}/{random_seed}/00-waypoints.png",
        route=None
    )
    plot_with_polygon_case(
        waypoints=waypoints,
        sbw=sbw,
        sbw_verts=None,
        damage_poly=None,
        tornado_point=None,
        bounds=bounds,
        show=False,
        title="Generated SBW",
        path=f"{base_folder}/{random_seed}/01-waypoints-sbw.png",
        route=None
    )
    plot_with_polygon_case(
        waypoints=None,
        sbw=sbw,
        sbw_verts=None,
        damage_poly=None,
        tornado_point=None,
        bounds=bounds,
        show=False,
        title="Generated SBW",
        path=f"{base_folder}/{random_seed}/02-sbw.png",
        route=None
    )
    plot_with_polygon_case(
        waypoints=None,
        sbw=sbw,
        sbw_verts=None,
        damage_poly=None,
        tornado_point=tornado_init,
        bounds=bounds,
        show=False,
        title="Selected Tornado Point",
        path=f"{base_folder}/{random_seed}/03-torn-point.png",
        route=None
    )
    plot_with_polygon_case(
        waypoints=None,
        sbw=sbw,
        sbw_verts=None,
        damage_poly=None,
        tornado_point=tornado_init,
        torn_path=(tornado_init, torn_end),
        bounds=bounds,
        show=False,
        title="Generated Tornado Path",
        path=f"{base_folder}/{random_seed}/04-torn-path.png",
        route=None
    )
    plot_with_polygon_case(
        waypoints=None,
        sbw=sbw,
        sbw_verts=None,
        damage_poly=damage_polygon,
        tornado_point=tornado_init,
        torn_path=None,
        bounds=bounds,
        show=False,
        title="Generated Damaged Area",
        path=f"{base_folder}/{random_seed}/05-torn-Polygon.png",
        route=None
    )
    plot_with_polygon_case(
        waypoints=waypoints,
        sbw=sbw,
        sbw_verts=None,
        damage_poly=damage_polygon,
        tornado_point=tornado_init,
        torn_path=None,
        bounds=bounds,
        show=False,
        title=f"{random_seed}",
        path=f"{base_folder}/{random_seed}.png",
        route=None
    )

    return 0


if __name__ == '__main__':
    # seeds = make_random_seed_list(50, 12345)
    seeds = [768470]
    for seed in seeds:
        random_case_plotter_creator(
        seed,
        f"./pars/random_case_pars.json"
    )