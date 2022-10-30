import traceback
import warnings

from twilio.rest import Client

import time

from dynamic_routing import dynamic_routing
from utilities.log_results import log_results
from pars.parfile_reader import parfile_reader, dump_parfile, many_parfiles_reader
from utilities.file_movers import clean_up, open_folder
from utilities.plotter_utilities import plot_case_info
from utilities.random_case_generator import random_case_generator
from utilities.slides_to_moving_picture_show import make_moving_picture_show
from utilities.utilities import datetime_string, make_random_seed_list

BASE_OUTPUT_FOLDER_TEMPLATE = "./outputs/{datetime_str}/{random_seed}/{case_name}/"


def main(parfile_name, random_seed, BASE_OUTPUT_FOLDER_TEMPLATE="./outputs/{datetime_str}/{random_seed}/{case_name}/"):
    print(f"{'':=<120}")
    print(f"DATE TIME FOLDER :: {datetime_string()}")
    print(f"RANDOM SEED :: {random_seed}")
    print(f"PARFILE NAME :: {parfile_name}")
    print(f"{'':=<120}")
    # t_start = datetime.now()
    t_start = time.time()
    ## Reading and logging parfile
    pars = parfile_reader(parfile_name)
    BASE_OUTPUT_FOLDER = BASE_OUTPUT_FOLDER_TEMPLATE.format(datetime_str=datetime_string(), random_seed=random_seed,
                                                            case_name=pars['case_name'])
    dump_parfile(
        pars,
        f"{BASE_OUTPUT_FOLDER}/parfile_data.json"
    )

    ## Generating random case
    waypoints_data, *other_random_case_data = \
        random_case_generator(
            random_case_parfile="./pars/random_case_pars.json",
            random_seed=random_seed,
            pars=pars,
            BASE_OUTPUT_FOLDER=BASE_OUTPUT_FOLDER
        )
    minimum_hamiltonian_path, minimum_hamiltonian_path_distance = other_random_case_data[-2:]
    if pars['plots'] in {'all', 'main'}:
        plot_case_info(other_random_case_data, random_seed, pars, BASE_OUTPUT_FOLDER)

    ## Solving dynamically
    route_as_visited, all_memory, n_missed_waypoints, dist_init = dynamic_routing(waypoints_data, pars, random_seed,
                                                                                  BASE_OUTPUT_FOLDER)

    ## Concluding
    # t_taken_sec = datetime.now() - t_start
    t_taken_sec = time.time() - t_start
    if pars['plots'] in {'all'}:
        make_moving_picture_show(
            input_folder=f"{BASE_OUTPUT_FOLDER}/plots/routes/",
            output_folder=f"{BASE_OUTPUT_FOLDER}/",
            filename="route_as_traveled"
        )
    return pars, random_seed, t_taken_sec, route_as_visited, all_memory, n_missed_waypoints, dist_init, minimum_hamiltonian_path_distance


def send_twillo_stuff(message, twillo_pars="./pars/twillo.json"):
    try:
        twillo_pars = parfile_reader(twillo_pars)
        client = Client(twillo_pars["act_sid"], twillo_pars["auth"])
        message = client.messages.create(body=message,
                                         from_=twillo_pars["number"],
                                         to=twillo_pars["my_number"])
        print(message.sid)
    except:
        warnings.warn(f"Failed to send twillo message!")


if __name__ == '__main__':
    try:
        send_twillo_stuff(f"Starting Project Archangel at {datetime_string()}")

        clean_up()
        seeds = make_random_seed_list(100, 12345)
        parfiles = many_parfiles_reader(
            "D:/PythonProjects/ProjectArchangel-AbstractCases-2022-10-15/pars/testing_folder_Oct26"
        )
        logfile_path = f"./logfiles/{datetime_string()}_log.csv"
        for seed in seeds:
            for parfile in parfiles:
                pars, random_seed, t_taken_sec, route_as_visited, all_memory, n_missed_waypoints, dist_init, minimum_hamiltonian_path_distance = main(
                    parfile,
                    seed)
                log_results(
                    pars, random_seed, t_taken_sec, route_as_visited, all_memory, n_missed_waypoints, dist_init, minimum_hamiltonian_path_distance,
                    logfile_path=logfile_path
                )
                clean_up()
            send_twillo_stuff(f"Completed seed {seed} at {datetime_string(current=True)}")

        open_folder(f"G:/OUTPUTS-project-archangel-AbstractCases/{datetime_string()}")
        send_twillo_stuff(f"Finished Project Archangel at {datetime_string()}")
    except Exception as e:
        traceback.print_exc()
        send_twillo_stuff(f"Error in Project Archangel at {datetime_string()}")
        send_twillo_stuff(f"TRACEBACK : {traceback.format_exc()}")
