import traceback

from utilities.log_results import log_results
from main import send_twillo_stuff, main
from utilities.file_movers import clean_up
from utilities.utilities import datetime_string

def scratch_pad():
    seed = 51203
    parfile = "D:/PythonProjects/ProjectArchangel-AbstractCases-2022-10-15/pars" \
              "/testing_folder_Oct20\pars_default.json"
    dt_str = "20221020_140159"


    try:
        send_twillo_stuff(f"Starting Project Archangel at {datetime_string()}")

        # clean_up()
        logfile_path = f"old_logfiles/logfiles/{dt_str}_log.csv"
        # for seed in seeds:
        #     for parfile in parfiles:
        pars, random_seed, t_taken_sec, route_as_visited, all_memory, n_missed_waypoints, dist_init = \
            main(parfile, seed,
                 BASE_OUTPUT_FOLDER_TEMPLATE="./SCRATCH_outputs/{datetime_str}/{random_seed}/{case_name}/")
        log_results(
                    pars, random_seed, t_taken_sec, route_as_visited, all_memory, n_missed_waypoints, dist_init,
                    logfile_path=logfile_path
                )
        send_twillo_stuff(f"Completed seed {seed} at {datetime_string(current=True)}")
        send_twillo_stuff(f"Finished Project Archangel at {dt_str}")
    except Exception as e:
        traceback.print_exc()
        send_twillo_stuff(f"Error in Project Archangel at {dt_str}")
        send_twillo_stuff(f"TRACEBACK : {traceback.format_exc()}")

if __name__ == '__main__':
    clean_up(
        open_the_folder=True,
        base_folders_to_move=f"D:/PythonProjects/ProjectArchangel-AbstractCases-2022-10-15/outputs/",
        destinations=f"G:/OUTPUTS-project-archangel-AbstractCases/",
        LOGFILE_base_folder_to_move="D:/PythonProjects/ProjectArchangel-AbstractCases-2022-10-15/logfiles/",
        LOGFILE_destination="D:/Users/seang/OneDrive - polymtl.ca/project-archangel-logfiles/"
    )
    clean_up(
        open_the_folder=True,
        base_folders_to_move=f"D:/PythonProjects/ProjectArchangel-AbstractCases-2022-10-15/PARALLEL_outputs/",
        destinations=f"G:/OUTPUTS-project-archangel-AbstractCases/",
        LOGFILE_base_folder_to_move="D:/PythonProjects/ProjectArchangel-AbstractCases-2022-10-15/PARALLEL_logfiles/",
    )
