import datetime
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
    _data = [dict(parfile=parfile, seed=seed) for parfile in parfiles for seed in seeds]
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
        telegram_bot_send_message(
            f"<pre><b>{test_name}</b></pre>\n"
            f"Starting!\n"
            f"At {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        tests = parfile_reader(test_file)
        # random.shuffle(tests)
        while len(tests) > 0:
            KILL_SWITCH(f="./kill-switch/kill-switch.json", k=test_name)
            print(f"test_name : Tests Remaining {len(tests)}")
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
            if time.time() - last_messaged > 4 * 60 * 60:
                if not is_in_time_range(
                        begin=datetime.time(hour=(12 + 8), minute=30),
                        end=datetime.time(hour=8, minute=0)
                ):
                    telegram_bot_send_message(
                        f"<pre><b>{test_name}</b></pre>\n"
                        f"At {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"{len(tests)} remaining tests"
                    )
                    last_messaged = time.time()
    except:
        traceback.print_exc()
        telegram_bot_send_message(
            f"<pre><b>{test_name}</b></pre>"
            f"\nERROR!\n"
            f"At {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        telegram_bot_send_message(f"<pre><b>{test_name}</b></pre>"
                                  f"\nTRACEBACK :\n"
                                  f"<pre>{traceback.format_exc()}</pre>")
    else:
        telegram_bot_send_message(
            f"<pre><b>{test_name}</b></pre>\n"
            f"FINISHED SUCCESSFULLY!\n"
            f"At {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    telegram_bot_send_message(
        f"<pre><b>{test_name}</b></pre>\n"
        f"Teminated\n"
        f"At {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def is_in_time_range(begin, end):
    if isinstance(begin, str):
        begin = datetime.time(hour=time.strptime(begin, "%H:%M").tm_hour, minute=time.strptime(begin, "%H:%M").tm_min)
    if isinstance(end, str):
        end = datetime.time(hour=time.strptime(end, "%H:%M").tm_hour, minute=time.strptime(end, "%H:%M").tm_min)
    now = datetime.datetime.now()
    now = datetime.time(hour=now.hour, minute=now.minute, second=now.second)
    if end <= begin:
        return not is_in_time_range(end, begin)
    return begin <= now <= end


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
    init_seed = int(sys.argv[1])
    test_name = f"{socket.gethostname()}-TEST-{init_seed}"
    time.sleep(int(sys.argv[1][-1]))
    data_destinations = {
        "SEAN-POLY-DESK": "G:/project-archangel-outputs-EXPERIMENTS/",
        "SEAN-LAP-T480": "C:/Users/seang/OneDrive - polymtl.ca/project-archangel-remote-outputs-EXPERIMENTS/",
        "SEAN-LAP-X1": "C:/Users/seang/OneDrive - polymtl.ca/project-archangel-remote-outputs-EXPERIMENTS/",
        "SEAN-HTPC": "C:/Users/seang/OneDrive - polymtl.ca/project-archangel-remote-outputs-EXPERIMENTS/",
        "SEAN-DESK-HOME": None  # todo
    }
    log_destinations = {
        "SEAN-POLY-DESK": "D:/Users/seang/OneDrive - polymtl.ca/project-archangel-logfiles-EXPERIMENTS/",
        "SEAN-LAP-T480": "C:/Users/seang/OneDrive - polymtl.ca/project-archangel-logfiles-EXPERIMENTS/",
        "SEAN-LAP-X1": "C:/Users/seang/OneDrive - polymtl.ca/project-archangel-logfiles-EXPERIMENTS/",
        "SEAN-HTPC": "C:/Users/seang/OneDrive - polymtl.ca/project-archangel-logfiles-EXPERIMENTS/",
        "SEAN-DESK-HOME": None  # todo
    }
    print(test_name)
    _pars = dict(
        test_name=test_name,
        many_parfiles_location="./pars/testing_folder_Nov1_Experiments/",
        test_file=f"./test_file_Nov9_Experiments/{test_name}.json",
        initial_seed=init_seed,
        number_of_seeds=50,
        skip_first_n_seeds=500,
        destinations=data_destinations[socket.gethostname()],  # Point toward OneDrive
        LOGFILE_destination=log_destinations[socket.gethostname()]
    )
    if not os.path.exists(_pars["test_file"]):
        create_tests(**_pars)
    KILL_SWITCH(f="./kill-switch/kill-switch.json", k=test_name, set_val=False)
    generalizable_testbox(**_pars)
