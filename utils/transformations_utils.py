import numpy as np
import matplotlib.pyplot as plt
import yaml
from scipy.spatial.transform import Rotation as R
import os
import argparse

def compute_ate_rmse(estimated_positions, groundtruth_positions):   
    """
    Calcula el Absolute Trajectory Error (ATE) basado en RMSE.

    Parámetros:
    - estimated_positions: np.array de forma (N,3) con posiciones estimadas (X, Y, Z)
    - groundtruth_positions: np.array de forma (N,3) con posiciones ground truth (X, Y, Z)

    Retorna:
    - ATE RMSE 
    """
    assert estimated_positions.shape == groundtruth_positions.shape, "Las trayectorias deben tener la misma longitud"

    errors = np.linalg.norm(estimated_positions - groundtruth_positions, axis=1)
    ate_rmse = np.sqrt(np.mean(errors**2))
    
    return ate_rmse

def load_yaml_transformations(yaml_path):
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
    timestamps = []
    poses = []
    with open(txt_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            values = list(map(float, line.split()))
            timestamps.append(values[0])
            q = values[1:5]  # qx, qy, qz, qw
            t = values[5:8]  # tx, ty, tz
            poses.append((q, t))
    return np.array(timestamps), poses

def pose_to_homogeneous(q, t):
    rot_matrix = R.from_quat(q).as_matrix()
    T = np.eye(4)
    T[:3, :3] = rot_matrix
    T[:3, 3] = t
    return T

def homogeneous_to_pose(T):
    rot_matrix = T[:3, :3]  # Extraer matriz de rotación
    t = T[:3, 3]  # Extraer traslación
    q = R.from_matrix(rot_matrix).as_quat()  # Convertir matriz de rotación a quaternion
    return q, t

def transform_poses_left(poses, transform):
    transformed_poses = []
    for q, t in poses:
        T = pose_to_homogeneous(q, t)
        T_transformed = transform @ T
        transformed_poses.append(T_transformed[:3, 3])
    return np.array(transformed_poses)

def transform_poses_right(poses, transform):
    transformed_poses = []
    for q, t in poses:
        T = pose_to_homogeneous(q, t)
        T_transformed = T @ transform
        transformed_poses.append(T_transformed[:3, 3])
    return np.array(transformed_poses)
