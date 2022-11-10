import random
from statistics import mean
from great_circle_calculator import great_circle_calculator
import pandas as pd
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, Point
from tqdm import tqdm
from math import cos, sin, radians

from influence_matrix_creators import read_and_process_tornado_file
from pars.parfile_reader import parfile_reader, dump_parfile
from route_nearest_insertion import route_nearest_insertion
from utilities.pickles_io import write_random_case_pickle, get_random_case_data_from_pickle
from utilities.utilities import datetime_string


def random_case_generator(
        pars,
        random_case_parfile,
        random_seed=None,
        BASE_OUTPUT_FOLDER=None, **kwargs
):
    random.seed(random_seed)
    random_case_pars = parfile_reader(random_case_parfile)
    dump_parfile(
        random_case_pars,
        f"{BASE_OUTPUT_FOLDER.format(datetime_str=datetime_string(), random_seed=random_seed, case_name=pars['case_name'])}/ramdom_case_parfile_data.json"
    )
    try:
        waypoints_data, waypoints, sbw, sbw_vertices, tornado_init, tornado_direction, tornado_length, tornado_width, damage_polygon, minimum_hamiltonian_path, minimum_hamiltonian_path_distance = get_random_case_data_from_pickle(pars, random_case_pars,
                                                                                         random_seed)
        print(f"Created Random Case {random_seed} from pickle!")
        return waypoints_data, waypoints, sbw, sbw_vertices, tornado_init, tornado_direction, tornado_length, tornado_width, damage_polygon, minimum_hamiltonian_path, minimum_hamiltonian_path_distance
    except:
        pass
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
        waypoints_data = create_waypoint_table(waypoints, sbw, damage_polygon, 0.5)
        waypoints_to_route = waypoints_data[waypoints_data["damaged"] == True]["_wp"].to_list()
        minimum_hamiltonian_path, minimum_hamiltonian_path_distance = \
            route_nearest_insertion(waypoints_to_route, start_min_arc=False, unknot=True)
    try:
        write_random_case_pickle(pars, random_case_pars, random_seed, waypoints_data, waypoints,
                                 sbw, sbw_vertices, tornado_init, tornado_direction, tornado_length,
                                 tornado_width, damage_polygon, minimum_hamiltonian_path, minimum_hamiltonian_path_distance)
    except:
        pass
    return waypoints_data, waypoints, sbw, sbw_vertices, \
           tornado_init, tornado_direction, tornado_length, tornado_width, damage_polygon, \
           minimum_hamiltonian_path, minimum_hamiltonian_path_distance


def create_waypoint_table(waypoints, sbw, damage, r_scan, default_score=0.5):
    def is_inside(_point, _geoms, _r_scan):
        if isinstance(_geoms, Polygon):
            _geoms = [_geoms]
        return any(geom.contains(Point(_point[0], _point[1])) for geom in _geoms) or any(
            geom.distance(Point(_point[0], _point[1])) <= _r_scan for geom in _geoms)

    data = {
        waypoint: {
            "damaged": is_inside(waypoint, damage, r_scan),
            "in_sbw": is_inside(waypoint, sbw, r_scan),
            "score": default_score * is_inside(waypoint, sbw, r_scan),
            "base_score": default_score * is_inside(waypoint, sbw, r_scan),
            "group_score": default_score * is_inside(waypoint, sbw, r_scan),
            "visited": False,
            "_wp": waypoint,
            "_wp_x": waypoint[0],
            "_wp_y": waypoint[1],
        }
        for waypoint in tqdm(waypoints, desc="Generating Waypoint Data Table")
    }
    return pd.DataFrame(data).transpose()


def create_damage_polygon(pt, direction, length, width):
    if direction >= 0:
        direction = 90 - direction
    else:
        direction = 90 + abs(direction)
    x, y = pt
    p1 = (x + width * 0.5 * cos(radians(direction + 90)), y + width * 0.5 * sin(radians(direction + 90)))
    p2 = (x + width * 0.5 * cos(radians(direction - 90)), y + width * 0.5 * sin(radians(direction - 90)))
    pt_end = (x + length * cos(radians(direction)), y + length * sin(radians(direction)))
    x, y = pt_end
    p3 = (x + width * 0.5 * cos(radians(direction + 90)), y + width * 0.5 * sin(radians(direction + 90)))
    p4 = (x + width * 0.5 * cos(radians(direction - 90)), y + width * 0.5 * sin(radians(direction - 90)))
    damage = Polygon([[p1, p2, p3, p4][i] for i in ConvexHull([p1, p2, p3, p4]).vertices])
    return damage, pt_end


def create_faux_tornado(sbw, tornado_data_file, lb_x=0, ub_x=10_000, lb_y=0, ub_y=10_000):
    d_x, d_y = ub_x - lb_x, ub_y - lb_y
    p_bar = tqdm(desc="Generating Tornado Damage Area")
    min_x, min_y, max_x, max_y = sbw.bounds
    points = []
    while len(points) < 100:
        p_bar.update()
        pt = (random.randint(min_x, max_x), random.randint(min_y, max_y))
        if sbw.contains(Point(pt)):
            points.append(pt)
    x, y = zip(*points)
    pt = int(mean(x)), int(mean(y))
    tornado_track_file = read_and_process_tornado_file(tornado_data_file)
    directions = tornado_track_file['direction'].to_list()
    direction = random.choice(directions)

    tornado_track_file['len'] = tornado_track_file['len'] * 1609.344
    max_len = max(tornado_track_file['len'])
    lengths = [round(i * max(d_x, d_y) / max_len)
               for i in tqdm(tornado_track_file['len'].to_list(), desc="Getting Length")
               if round(i * max(d_x, d_y) / max_len)
               >= 0.1 * max(d_x, d_y)]
    length = random.choice(lengths)
    tornado_track_file['wid'] = tornado_track_file['wid'] * 0.9144
    max_wid = max(tornado_track_file['wid'])
    widths = [round(i * max(d_x, d_y) / max_wid)
              for i in tqdm(tornado_track_file['wid'].to_list(), desc="Getting Width")
              if length >= round(i * max(d_x, d_y) / max_wid)
              >= 0.05 * max(d_x, d_y)]
    width = random.choice(widths)
    return pt, direction, length, width


def create_search_area(lb_x=0, ub_x=10_000, lb_y=0, ub_y=10_000,
                       min_area=0.33, max_area=0.67, n_vertex=4):
    d_x, d_y = ub_x - lb_x, ub_y - lb_y
    area_box = d_x * d_y
    p_bar = tqdm(desc="Creating Search Area")
    while True:
        vertices = set()
        while len(vertices) < n_vertex:
            pt = (random.randint(int(lb_x + .1 * d_x), int(ub_x - .1 * d_x)),
                  random.randint(int(lb_y + .1 * d_y), int(ub_y - .1 * d_y)))
            vertices.add(pt)
        vertices = list(vertices)
        hull = Polygon([vertices[i] for i in ConvexHull(list(vertices)).vertices])
        area_search_area = hull.area
        p_bar.set_postfix_str(f"{area_search_area / area_box:.3f} ({min_area} | {max_area})")
        p_bar.update()
        if min_area <= (area_search_area / area_box) <= max_area:
            break
    return hull, vertices


def create_waypoints(lb_x=0, ub_x=10_000, lb_y=0, ub_y=10_000, n_wpt=5_000, random_seed=None):
    waypoints = set()
    if random_seed:
        random.seed(random_seed)
    p_bar = tqdm(desc="Creating Waypoints")
    while len(waypoints) < n_wpt:
        pt = (random.randint(lb_x, ub_x), random.randint(lb_y, ub_y))
        waypoints.add(pt)
        p_bar.update()
    return list(waypoints)


if __name__ == "__main__":
    waypoints_data, *_ = random_case_generator(parfile="./pars/random_case_pars.json", random_seed=12345)
    print(waypoints_data)
