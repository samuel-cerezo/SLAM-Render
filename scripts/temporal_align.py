import numpy as np
import matplotlib.pyplot as plt
import yaml
from scipy.spatial.transform import Rotation as R
import os
import argparse
from alignment_utils import *

def main():
    # pointing to the dataset folder
    parser = argparse.ArgumentParser(description='Time alignment')
    parser.add_argument('--path', type=str, required=True, help='Folder containing dataset')
    args = parser.parse_args()
        
    dataset_path = os.path.join(args.path)
    # we retrieve the data from the files

    ts_assoc, matched_ts_flange, matched_flange_poses, matched_ts_gt, matched_gt_poses = process_timestamps(dataset_path)

    # retrieve an especific element
    i = 10
    print((ts_assoc[i]))
    print((matched_ts_flange[i]))
    print((matched_flange_poses[i]))
    print((matched_ts_gt[i]))
    print((matched_gt_poses[i]))

    

if __name__ == '__main__':
    main()

# example:
#           python3 fFlange2world.py --path /Volumes/SSD/archivos/KUKA_dev/environment_modeling/ROSBAGS/1-dark-tr
