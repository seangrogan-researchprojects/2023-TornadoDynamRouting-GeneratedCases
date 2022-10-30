from multiprocessing import Process
from pathlib import Path

import imageio
import imageio.v3 as iio
from tqdm import tqdm

from utilities.utilities import automkdir


def slides_to_moving_picture_show(input_folder, out_file):
    images = list()
    print(f"Reading slides in {input_folder}")
    for file in Path(input_folder).iterdir():
        if file.is_file():
            images.append(file)
    automkdir(out_file)
    print(f"Making {out_file}")
    with imageio.get_writer(out_file, mode='I', fps=6) as writer:
        for image in tqdm(images, desc="Making movie"):
            data = iio.imread(image)
            writer.append_data(data)
    print(f"Done ! {out_file}")


def make_moving_picture_show(input_folder, output_folder, filename):
    print("Making Moving Pictures...")
    proc = list()
    for ext in ["mp4"]:#["gif", "mp4"]:
        print(f"Making the '{ext}'")
        proc.append(Process(target=slides_to_moving_picture_show, args=(
            f"{input_folder}/",
            f"{output_folder}/{filename}.{ext}"
        )
                         ))
        proc[-1].start()
    for p in proc:
        p.join()



if __name__ == '__main__':
    DT = "20221005_110204"
    RS = "RS_267460_RM_order_scores_MStC_0.0_WithHistory"

    make_moving_picture_show(
        f"D:/PythonProjects/ProjectArchangel-AbstractCases-2022-10-01/outputs/plots/{DT}/{RS}/routes",
        f"D:/PythonProjects/ProjectArchangel-AbstractCases-2022-10-01/outputs/plots/{DT}/{RS}/",
        f"{DT}_RS_{RS}"
    )
