import copy
import hashlib
import json
import pickle

from utilities.utilities import automkdir


def get_random_case_data_from_pickle(pars, random_case_pars, random_seed):
    pickle_file = f"{pars['pickles_location']}/random_cases/{random_seed}/{random_case_string(random_case_pars, random_seed)}"
    data = pickle_reader(pickle_file)
    waypoints_data = data["waypoints_data"]
    waypoints = data["waypoints"]
    sbw = data["sbw"]
    sbw_vertices = data["sbw_vertices"]
    tornado_init = data["tornado_init"]
    tornado_direction = data["tornado_direction"]
    tornado_length = data["tornado_length"]
    tornado_width = data["tornado_width"]
    damage_polygon = data["damage_polygon"]
    minimum_hamiltonian_path = data["minimum_hamiltonian_path"]
    minimum_hamiltonian_path_distance = data["minimum_hamiltonian_path_distance"]
    return waypoints_data, waypoints, sbw, sbw_vertices, tornado_init, tornado_direction, tornado_length, tornado_width, damage_polygon, minimum_hamiltonian_path, minimum_hamiltonian_path_distance


def write_random_case_pickle(pars, random_case_pars, random_seed, waypoints_data, waypoints,
                             sbw, sbw_vertices, tornado_init, tornado_direction, tornado_length,
                             tornado_width, damage_polygon, minimum_hamiltonian_path,
                             minimum_hamiltonian_path_distance):
    pickle_file = f"{pars['pickles_location']}/random_cases/{random_seed}/{random_case_string(random_case_pars, random_seed)}"
    data = {
        "waypoints_data": waypoints_data,
        "waypoints": waypoints,
        "sbw": sbw,
        "sbw_vertices": sbw_vertices,
        "tornado_init": tornado_init,
        "tornado_direction": tornado_direction,
        "tornado_length": tornado_length,
        "tornado_width": tornado_width,
        "damage_polygon": damage_polygon,
        "minimum_hamiltonian_path": minimum_hamiltonian_path,
        "minimum_hamiltonian_path_distance": minimum_hamiltonian_path_distance
    }
    pickle_dumper(pickle_file, data)


def read_data_driven_influence_matrix(waypoints, tornado_data_file, pars):
    pickle_file = f"{pars['pickles_location']}/data_driven_influence_matrix_pickles/" \
                  f"{data_driven_influence_matrix_string(waypoints, tornado_data_file, pars)}"
    matrix = pickle_reader(pickle_file)
    return matrix


def write_data_driven_influence_matrix(waypoints, matrix, tornado_data_file, pars):
    pickle_file = f"{pars['pickles_location']}/data_driven_influence_matrix_pickles/" \
                  f"{data_driven_influence_matrix_string(waypoints, tornado_data_file, pars)}"
    pickle_dumper(pickle_file, matrix)


def data_driven_influence_matrix_string(waypoints, tornado_data_file, pars):
    _data = {"wpts": waypoints,
             "torn_data_file": tornado_data_file,
             "pars": pars}
    json_str = json.dumps(_data, sort_keys=True)
    return hashlib.sha224(json_str.encode('utf-8')).hexdigest()


def read_symmetric_influence_matrix(waypoints, pars):
    pickle_file = f"{pars['pickles_location']}/" \
                  f"symmetric_influence_matrix_pickles/" \
                  f"{symmetric_influence_matrix_string(waypoints)}.pl"
    matrix = pickle_reader(pickle_file)
    return matrix


def write_symmetric_influence_matrix(waypoints, matrix, pars):
    pickle_file = f"{pars['pickles_location']}/" \
                  f"symmetric_influence_matrix_pickles/" \
                  f"{symmetric_influence_matrix_string(waypoints)}.pl"
    pickle_dumper(pickle_file, matrix)


def symmetric_influence_matrix_string(waypoints):
    sorted(waypoints)
    _data = {"wpts": copy.deepcopy(waypoints)}
    json_str = json.dumps(_data, sort_keys=True)
    return hashlib.sha224(json_str.encode('utf-8')).hexdigest()


def random_case_string(random_case_pars, random_seed):
    _data = copy.deepcopy(random_case_pars)
    _data['random_seed'] = random_seed
    json_str = json.dumps(_data, sort_keys=True)
    return hashlib.sha224(json_str.encode('utf-8')).hexdigest()


def pickle_reader(file_to_try_to_open):
    with open(file_to_try_to_open, 'rb') as f:
        data = pickle.load(f)
    return data


def pickle_dumper(file_to_try_to_dump, data):
    automkdir(file_to_try_to_dump)
    with open(file_to_try_to_dump, 'wb') as f:
        pickle.dump(data, f)
