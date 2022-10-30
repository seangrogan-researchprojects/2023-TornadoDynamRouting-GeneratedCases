import os.path
import random
import sys
import traceback
import socket

from utilities.log_results import log_results
from main import main
from pars.parfile_reader import many_parfiles_reader, dump_parfile, parfile_reader
from utilities.file_movers import clean_up
from utilities.telegram_bot import telegram_bot_send_message
from utilities.utilities import datetime_string, make_random_seed_list
import time


def create_tests(
        many_parfiles_location,
        initial_seed,
        number_of_seeds,
        test_file,
        skip_first_n_seeds,
        **kwargs
):
    parfiles = many_parfiles_reader(
        many_parfiles_location
    )
    print(f"Creating Tests!")
    seeds = make_random_seed_list(number_of_seeds, initial_seed, skip_first_n_seeds)
    if random.choice([True, False]):
        _data = [dict(parfile=parfile, seed=seed) for parfile in parfiles for seed in seeds]
    else:
        _data = [dict(parfile=parfile, seed=seed) for seed in seeds for parfile in parfiles]
    # random.shuffle(_data)
    dump_parfile(_data, test_file)


def generalizable_testbox(
        test_name, test_file, destinations, LOGFILE_destination,
        open_the_folder=False,
        **kwargs
):
    logfile_path = f"./logfiles/{datetime_string()}_{test_name}_log.csv"
    logfile_folder = os.path.dirname(logfile_path)

    clean_up(
        open_the_folder=open_the_folder,
        base_folders_to_move=f"./outputs-{test_name}/",
        destinations=destinations,
        LOGFILE_base_folder_to_move=logfile_folder,
        LOGFILE_destination=LOGFILE_destination
    )
    last_messaged = 0
    try:
        telegram_bot_send_message(f"<pre><b>{test_name}</b></pre>\nStarting Project Archangel at {datetime_string()}")
        tests = parfile_reader(test_file)
        # random.shuffle(tests)
        while len(tests) > 0:
            KILL_SWITCH(f="./kill-switch/kill-switch.json", k=test_name)
            print(test_name)
            ## Get test
            test = tests.pop()
            ## Run Test
            pars, random_seed, t_taken_sec, route_as_visited, all_memory, n_missed_waypoints, dist_init, \
            minimum_hamiltonian_path_distance = \
                main(test["parfile"], test["seed"],
                     BASE_OUTPUT_FOLDER_TEMPLATE=
                     "./outputs-" + f"{test_name}" + "/{datetime_str}/{random_seed}/{case_name}/")
            ## Log Results
            log_results(
                pars, random_seed, t_taken_sec, route_as_visited, all_memory, n_missed_waypoints, dist_init,
                minimum_hamiltonian_path_distance,
                logfile_path=logfile_path
            )
            ## Clean up
            dump_parfile(tests, test_file)
            clean_up(
                open_the_folder=open_the_folder,
                base_folders_to_move=f"./outputs-{test_name}/",
                destinations=destinations,
                LOGFILE_base_folder_to_move=logfile_folder,
                LOGFILE_destination=LOGFILE_destination
            )
            if len(tests) % 100 == 0 or time.time() - last_messaged > 6 * 60 * 60:
                telegram_bot_send_message(
                    f"<pre><b>{test_name}</b></pre>\nat {datetime_string(current=True)} Project Archangel, Remaining Tests {len(tests)}"
                )
                last_messaged = time.time()
    except:
        traceback.print_exc()
        telegram_bot_send_message(f"<pre><b>{test_name}</b></pre>\nERROR! at {datetime_string(current=True)}")
        telegram_bot_send_message(f"<pre><b>{test_name}</b></pre>\nTRACEBACK :\n{traceback.format_exc()}")
    telegram_bot_send_message(f"<pre><b>{test_name}</b></pre>\nFinished Project Archangel at {datetime_string()} at {datetime_string(current=True)}")


def KILL_SWITCH(f, k, set_val=None):
    if not os.path.exists(f):
        dump_parfile({k: False}, f)
    kill_switch = parfile_reader(f)
    if k not in kill_switch:
        kill_switch[k] = False
        dump_parfile(kill_switch, f)
    if set_val is not None:
        kill_switch[k] = set_val
        dump_parfile(kill_switch, f)
    if kill_switch.get(k, False):
        raise Exception(f"Killed {k} by kill switch")


if __name__ == '__main__':
    time.sleep(random.randint(1, 5))
    init_seed = int(sys.argv[1])
    test_name = f"{socket.gethostname()}-TEST-{init_seed}"
    print(test_name)
    _pars = dict(
        test_name=test_name,
        many_parfiles_location="./pars/testing_folder_Oct26/",
        test_file=f"./test_file/{test_name}.json",
        initial_seed=init_seed,
        number_of_seeds=100,
        skip_first_n_seeds=None,
        destinations="G:/OUTPUTS-project-archangel-AbstractCases/",  # Point toward OneDrive
        LOGFILE_destination="D:/Users/seang/OneDrive - polymtl.ca/project-archangel-logfiles/"
    )
    if not os.path.exists(_pars["test_file"]):
        create_tests(**_pars)
    KILL_SWITCH(f="./kill-switch/kill-switch.json", k=test_name, set_val=False)
    generalizable_testbox(**_pars)
