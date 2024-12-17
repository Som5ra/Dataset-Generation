import os
import json
import shutil
import argparse
from PIL import Image
'''
- bproc_dataset
    - 0
        - coco_data
            - images
            - images_filled
    - 1
    ...
'''

def on_the_border(bbox, image_shape):
    return bbox[0] == 0 or bbox[1] == 0 or bbox[0] + bbox[2] == image_shape[1] or bbox[1] + bbox[3] == image_shape[0]
def too_small(bbox, threshold):
    return bbox[2] * bbox[3] < threshold

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_folder", type=str, required=True)
    parser.add_argument("--out_folder", type=str, required=True)
    parser.add_argument("--anti", type=bool, default=True)
    # parser.add_argument("--anti", action='store_true')

    args = parser.parse_args()
    # out_folder = 'transparency_20241015_merged_drop_mini'
    out_folder = args.out_folder
    os.makedirs(os.path.join(out_folder, 'images'), exist_ok=True)
    # positive
    # bproc_dataset_base = "/home/gusto/dataset_generation/transparency_20241015"
    bproc_dataset_base = args.in_folder
    # negative
    # background_list_base = "/home/gusto/dataset_generation/coco_source/test2017"
    scene_list = os.listdir(bproc_dataset_base)
    # eliminate background_used and classes.txt
    scene_list = [x for x in scene_list if x != "background_used" and x != "classes.txt"]

    IMAGE_ID = 0
    ANNO_ID = 0
    big_anno = {
        "info": {
            "description": "coco_annotations",
            "url": "https://github.com/waspinator/pycococreator",
            "version": "0.1.0",
            "year": 2020,
            "contributor": "Unknown",
            "date_created": "2024-10-15 06:36:03.096766"
        },
        "licenses": [
            {
                "id": 1,
                "name": "Attribution-NonCommercial-ShareAlike License",
                "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
            }
        ],
        "categories": [
            {
                "id": 1,
                "supercategory": "coco_annotations",
                "name": "Bruni"
            },
            {
                "id": 2,
                "supercategory": "coco_annotations",
                "name": "Elsa"
            },
            {
                "id": 3,
                "supercategory": "coco_annotations",
                "name": "Anna"
            }
        ],
        "images": [],
        "annotations": []
    }
    for scene in sorted(scene_list, key=lambda x: int(x)):
        if os.path.isdir(os.path.join(bproc_dataset_base, scene)) is False or scene == "background_used":
            continue
        anno_file = os.path.join(bproc_dataset_base, scene, "coco_data", "coco_annotations.json")
        with open(anno_file, "r") as f:
            anno_data = json.load(f)
        image_id_mapper = {}
        for img in anno_data["images"]:
            image_id_mapper[img["id"]] = IMAGE_ID
            img["id"] = IMAGE_ID
            IMAGE_ID += 1
            raw_file_name = img["file_name"].rsplit("/", 1)[-1]
            img["file_name"] = scene + "_" + img["file_name"].rsplit("/", 1)[-1]
            big_anno["images"].append(img)
            shutil.copyfile(os.path.join(bproc_dataset_base, scene, "coco_data", "images_filled", raw_file_name), os.path.join(out_folder, "images", img["file_name"]))
        cat_mapper = {}
        for cat in anno_data["categories"]:
            if 'Bruni' in cat["name"]:
                cat_mapper[cat["id"]] = 1
            elif 'Elsa' in cat["name"]:
                cat_mapper[cat["id"]] = 2
            elif 'Anna' in cat["name"]:
                cat_mapper[cat["id"]] = 3
            else:
                raise Exception("Werid catgroies")
        for anno in anno_data["annotations"]:
            anno["category_id"] = cat_mapper[anno["category_id"] ]
            bbox = anno["bbox"]
            image_w, image_h = anno["width"], anno["height"]
            image_shape = (image_h, image_w)
            if too_small(bbox, 4000):
                continue
            if on_the_border(bbox, image_shape) and too_small(bbox, 5000):
                continue
            anno["id"] = ANNO_ID
            ANNO_ID += 1
            anno["image_id"] = image_id_mapper[anno["image_id"]]
            big_anno["annotations"].append(anno)
    if args.anti:
        background_used_path = os.path.join(bproc_dataset_base, "background_used")
        for bg in os.listdir(background_used_path):
            bg_img = os.path.join(bproc_dataset_base, "background_used", bg)
            shutil.copy2(bg_img, os.path.join(out_folder, "images"))
            image = Image.open(bg_img)
            width, height = image.size
            image_dict = {
                "id": IMAGE_ID,
                "width": width,
                "height": height,
                "file_name": bg
            }
            IMAGE_ID += 1
            big_anno["images"].append(image_dict)
    with open(os.path.join(out_folder, 'labels.json'), "w") as f:
        json.dump(big_anno, f)
    