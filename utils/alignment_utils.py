import numpy as np
import matplotlib.pyplot as plt
import yaml
from scipy.spatial.transform import Rotation as R
import os
import argparse

def process_timestamps(dataset_path):
    """
    Reads and processes timestamps from association, flange poses, and ground truth files.
    Filters timestamps to a common range and finds the nearest match for each association timestamp.
    
    Args:
        dataset_path (str): Path to the dataset directory.
    
    Returns:
        tuple: (ts_assoc, matched_ts_flange, matched_flange_poses, matched_ts_gt, matched_gt_poses)
    """
    # Define file paths
    association_file = os.path.join(dataset_path, "associations.txt")
    flange_poses_file = os.path.join(dataset_path, "robot_data/flange_poses.txt")
    gt_file = os.path.join(dataset_path, "groundtruth.txt")

    # Read association timestamps
    ts_assoc = []
    with open(association_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            values = list(line.split())
            ts_assoc.append(float(values[0]))

    # Read flange poses timestamps and data
    ts_flange, flange_poses = [], []
    with open(flange_poses_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            values = list(line.split())
            ts = float(values[0])
            ts_flange.append(ts)
            q = values[1:5]  # Quaternion (qx, qy, qz, qw)
            t = values[5:8]  # Translation (tx, ty, tz)
            flange_poses.append((q, t))

    # Read ground truth timestamps and data
    ts_gt, gt_poses = [], []
    with open(gt_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            values = list(line.split())
            ts = float(values[0])
            ts_gt.append(ts)
            q = values[1:5]  # Quaternion (qx, qy, qz, qw)
            t = values[5:8]  # Translation (tx, ty, tz)
            gt_poses.append((q, t))

    # Determine the common timestamp range
    min_ts = max(min(ts_assoc), min(ts_flange), min(ts_gt))
    max_ts = min(max(ts_assoc), max(ts_flange), max(ts_gt))

    # Filter timestamps within the common range
    ts_assoc = [t for t in ts_assoc if min_ts <= t <= max_ts]
    ts_flange, flange_poses = zip(*[(t, p) for t, p in zip(ts_flange, flange_poses) if min_ts <= t <= max_ts])
    ts_gt, gt_poses = zip(*[(t, p) for t, p in zip(ts_gt, gt_poses) if min_ts <= t <= max_ts])

    # Convert back to lists
    ts_flange, flange_poses = list(ts_flange), list(flange_poses)
    ts_gt, gt_poses = list(ts_gt), list(gt_poses)

    # Function to find the nearest timestamp
    def find_nearest(ts_list, target):
        ts_list = np.array(ts_list, dtype=float)  # Ensure array of floats
        target = float(target)  # Ensure target is float
        idx = np.argmin(np.abs(ts_list - target))
        return ts_list[idx]

    # Match each association timestamp with the closest flange and ground truth timestamp
    matched_ts_flange, matched_flange_poses = [], []
    matched_ts_gt, matched_gt_poses = [], []

    for ts in ts_assoc:
        nearest_flange = find_nearest(ts_flange, ts)
        nearest_gt = find_nearest(ts_gt, ts)

        matched_ts_flange.append(nearest_flange)
        matched_flange_poses.append(flange_poses[ts_flange.index(nearest_flange)])

        matched_ts_gt.append(nearest_gt)
        matched_gt_poses.append(gt_poses[ts_gt.index(nearest_gt)])

    # Ensure all sets have the same length
    assert len(ts_assoc) == len(matched_ts_flange) == len(matched_ts_gt), "Data sets do not match in size"
    
    return ts_assoc, matched_ts_flange, matched_flange_poses, matched_ts_gt, matched_gt_poses


def load_yaml_transformations(yaml_path):
    """
    Loads transformation matrices from a YAML file.

    Parameters:
    - yaml_path (str): Path to the YAML file.

    Returns:
    - transformations (dict): Dictionary with frame pairs as keys and 4x4 transformation matrices as values.
    """
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    transformations = {}
    for entry in data['T']:
        src = entry['source_frame']
        tgt = entry['target_frame']
        matrix = np.array(entry['matrix']['data']).reshape(4, 4)
        transformations[(src, tgt)] = matrix
    
    return transformations

def load_poses(txt_path):
    """
    Loads poses from a text file.

    Parameters:
    - txt_path (str): Path to the text file.

    Returns:
    - timestamps (np.array): Array of timestamps.
    - poses (list of tuples): Each tuple contains a quaternion (qx, qy, qz, qw) and a translation vector (tx, ty, tz).
    """
    timestamps = []
    poses = []
    with open(txt_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            values = list(map(float, line.split()))
            timestamps.append(values[0])
            q = values[1:5]  # Quaternion (qx, qy, qz, qw)
            t = values[5:8]  # Translation (tx, ty, tz)
            poses.append((q, t))
    return np.array(timestamps), poses

def pose_to_homogeneous(q, t):
    """
    Converts a pose (quaternion and translation) into a 4x4 homogeneous transformation matrix.

    Parameters:
    - q (list): Quaternion (qx, qy, qz, qw)
    - t (list): Translation vector (tx, ty, tz)

    Returns:
    - T (np.array): 4x4 homogeneous transformation matrix.
    """
    rot_matrix = R.from_quat(q).as_matrix()
    T = np.eye(4)
    T[:3, :3] = rot_matrix
    T[:3, 3] = t
    return T

def homogeneous_to_pose(T):
    """
    Converts a 4x4 homogeneous transformation matrix into a pose (quaternion and translation).

    Parameters:
    - T (np.array): 4x4 homogeneous transformation matrix.

    Returns:
    - q (np.array): Quaternion (qx, qy, qz, qw)
    - t (np.array): Translation vector (tx, ty, tz)
    """
    rot_matrix = T[:3, :3]
    t = T[:3, 3]
    q = R.from_matrix(rot_matrix).as_quat()
    return q, t

def transform_poses_left(poses, transform):
    """
    Applies a transformation matrix to a set of poses from the left.

    Parameters:
    - poses (list of tuples): List of (quaternion, translation) tuples.
    - transform (np.array): 4x4 transformation matrix.

    Returns:
    - transformed_poses (np.array): Transformed positions (N,3).
    """
    transformed_poses = []
    for q, t in poses:
        T = pose_to_homogeneous(q, t)
        T_transformed = transform @ T
        transformed_poses.append(T_transformed[:3, 3])
    return np.array(transformed_poses)

def transform_poses_right(poses, transform):
    """
    Applies a transformation matrix to a set of poses from the right.

    Parameters:
    - poses (list of tuples): List of (quaternion, translation) tuples.
    - transform (np.array): 4x4 transformation matrix.

    Returns:
    - transformed_poses (np.array): Transformed positions (N,3).
    """
    transformed_poses = []
    for q, t in poses:
        T = pose_to_homogeneous(q, t)
        T_transformed = T @ transform
        transformed_poses.append(T_transformed[:3, 3])
    return np.array(transformed_poses)

def compute_camera_world_positions(poses_flange, T_world_base_marker, T_robot_base_base_marker, T_robot_flange_rgb):
    """
    Computes the world positions and orientations (as quaternions) of a camera given a set of flange poses.

    Parameters:
        poses_flange (list of tuples): Each tuple contains rotation and translation information for a flange pose.
        T_world_base_marker (numpy.ndarray): 4x4 transformation matrix from the base marker to the world.
        T_robot_base_base_marker (numpy.ndarray): 4x4 transformation matrix from the  base marker to robot base.
        T_robot_flange_rgb (numpy.ndarray): 4x4 transformation matrix from the RGB camera to robot flange.

    Returns:
        tuple: 
            - numpy.ndarray: Nx4 array of camera orientations as quaternions.
            - numpy.ndarray: Nx3 array of camera positions in the world frame.
    """
    camera_world_positions = []
    camera_world_orientations = []
    
    for f_pose in poses_flange:
        # Convert pose information to a homogeneous transformation matrix
        T_hom = pose_to_homogeneous(f_pose[0], f_pose[1])
        
        # Compute the transformed pose in the world frame
        T_transformed = (T_world_base_marker @ 
                         np.linalg.inv(T_robot_base_base_marker) @ 
                         T_hom @ 
                         T_robot_flange_rgb)
        
        # Extract the translation component (position)
        position = T_transformed[:3, 3]
        camera_world_positions.append(position)
        
        # Extract the rotation component and convert it to quaternion
        rotation_matrix = T_transformed[:3, :3]
        quaternion = R.from_matrix(rotation_matrix).as_quat()
        camera_world_orientations.append(quaternion)
    
    return np.array(camera_world_orientations), np.array(camera_world_positions)

def compute_camera_world_positions_gt(poses_gt, T_rgb_flange_markers):
    """
    Computes the world positions and orientations (as quaternions) of a camera given a set of ground truth poses (flange-markers).

    Parameters:
        poses_gt (list of tuples): Each tuple contains rotation and translation information for a ground truth pose (flange-markers).
        T_rgb_flange_markers (numpy.ndarray): 4x4 transformation matrix from the RGB camera to the flange markers.

    Returns:
        tuple:
            - numpy.ndarray: Nx4 array of camera orientations as quaternions.
            - numpy.ndarray: Nx3 array of camera positions in the world frame.
    """
    camera_world_positions_gt = []
    camera_world_orientations_gt = []
    
    for gt_pose in poses_gt:
        # Convert ground truth pose information to a homogeneous transformation matrix
        T_hom = pose_to_homogeneous(gt_pose[0], gt_pose[1])
        
        # Compute the transformed pose in the world frame
        T_transformed = T_hom @ np.linalg.inv(T_rgb_flange_markers)
        
        # Extract the translation component (position)
        position = T_transformed[:3, 3]
        camera_world_positions_gt.append(position)
        
        # Extract the rotation component and convert it to quaternion
        rotation_matrix = T_transformed[:3, :3]
        quaternion = R.from_matrix(rotation_matrix).as_quat()
        camera_world_orientations_gt.append(quaternion)
    
    return np.array(camera_world_orientations_gt), np.array(camera_world_positions_gt)
