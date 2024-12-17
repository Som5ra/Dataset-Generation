import subprocess
import os
from multiprocessing import Pool


if __name__ == '__main__':
    bproc_dataset_base = "/home/gusto/dataset_generation/transparency@30a@large@20241025"
    background_list_base = "/home/gusto/dataset_generation/coco_source/test2017"
    scene_list = os.listdir(bproc_dataset_base)

    def call_cmd(cmd):
        print("calling: ", cmd)
        subprocess.call(cmd)

    with Pool(4) as pool:
        for scene in scene_list:
            scene_images_path = os.path.join(bproc_dataset_base, scene, 'coco_data', 'images')
            output_path = os.path.join(bproc_dataset_base, scene, 'coco_data', 'images_filled')
            background_copy_path = os.path.join(bproc_dataset_base, "background_used")
            cmd = [f"python3", "fill_background.py", 
                    "-i", f"{scene_images_path}",
                    "-b", f"{background_list_base}",
                    "-o", f"{output_path}",
                    "-bo", f"{background_copy_path}"]
            pool.apply_async(
                    call_cmd,
                    (cmd, )
                )
        pool.close()
        pool.join()
        # subprocess.call(cmd)