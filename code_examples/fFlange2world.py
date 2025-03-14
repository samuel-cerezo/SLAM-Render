import numpy as np
import matplotlib.pyplot as plt
import yaml
from scipy.spatial.transform import Rotation as R
import os
import argparse
from alignment_utils import *

def main():
    # pointing to the dataset folder
    parser = argparse.ArgumentParser(description='Compare poses (obtained by joint-robot vs gt)')
    parser.add_argument('--path', type=str, required=True, help='Folder containing dataset')
    args = parser.parse_args()
        
    dataset_path = os.path.join(args.path)
    # we retrieve the data from the files
    _ , poses_flange = load_poses(os.path.join(dataset_path, "robot_data/flange_poses.txt")) # flange wrt base robot
    _ , poses_gt = load_poses(os.path.join(dataset_path, "groundtruth.txt"))    # flange-markers wrt world
    
    # 
    
    transforms = load_yaml_transformations(os.path.join(dataset_path,  "extrinsics.yaml"))  # to obtain the transform matrixs

    #----- retrieving all transformations (T_target_source) -------
    T_world_base_marker = transforms[('base_marker_ring', 'world')]                     # base markers --> world
    T_robot_base_base_marker = transforms[('base_marker_ring', 'robot_base')]           # base markers --> robot base
    T_robot_flange_flange_marker = transforms[('flange_marker_ring', 'robot_flange')]   # flange markers --> flange 
    T_robot_flange_rgb = transforms[('rgb_sensor', 'robot_flange')]                     # camera  --> flange
    
    # ---- calculation for useful transformations ---
    T_flange_marker_robot_flange = np.linalg.inv(T_robot_flange_flange_marker)          # flange  --> flange markers
    T_rgb_flange_markers = np.linalg.inv(T_robot_flange_rgb) @ np.linalg.inv(T_flange_marker_robot_flange)  # flange markers --> camera 
    T_base_marker_robot_base =  np.linalg.inv(T_robot_base_base_marker)                      # robot base --> robot marker
    T_world_robot_base = T_world_base_marker @ T_base_marker_robot_base                      # robot base --> world

    # we convert the data into a same world reference frame
    _ , camera_world_positions  = compute_camera_world_positions(poses_flange, T_world_base_marker, T_robot_base_base_marker, T_robot_flange_rgb)
    _ , camera_world_positions_gt = compute_camera_world_positions_gt(poses_gt, T_rgb_flange_markers)

    # plotting
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(camera_world_positions[:, 0], camera_world_positions[:, 1], camera_world_positions[:, 2], label="Camera (obtained by robot-joints)", linestyle='--')
    ax.plot(camera_world_positions_gt[:, 0], camera_world_positions_gt[:, 1], camera_world_positions_gt[:, 2], label="Groundtruth ", linestyle=':')
    ax.legend()
    plt.show()

if __name__ == '__main__':
    main()

# example:
#           python3 fFlange2world.py --path /Volumes/SSD/archivos/KUKA_dev/environment_modeling/ROSBAGS/1-dark-tr
