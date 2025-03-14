import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from scipy.ndimage import uniform_filter1d
from scipy.signal import correlate
from scipy.fftpack import fft, ifft, fftshift
from scipy.ndimage import uniform_filter1d


# Configuración de argumentos de línea de comandos
parser = argparse.ArgumentParser(description="Sincronizar datos de IMU y cámara (pose) a partir de archivos CSV.")
parser.add_argument("--input", help="Nombre del dataset (sin la ruta completa)", type=str, required=True)

# Obtener el nombre del dataset desde los argumentos
args = parser.parse_args()

# Construir la ruta completa del archivo CSV de la cámara y IMU
dataset_path = f"/Volumes/SSD/archivos/KUKA_notebook/dev/environment_modeling/ROSBAGS/{args.input}/{args.input}.csv"
imu_path = f"/Volumes/SSD/archivos/KUKA_notebook/dev/environment_modeling/ROSBAGS/{args.input}/imu_data.txt"
groundtruth_path = f"/Volumes/SSD/archivos/KUKA_notebook/dev/environment_modeling/ROSBAGS/{args.input}/groundtruth.txt"

# Compute FFT-based Time Delay Estimation (TDE)
def estimate_delay_fft(sig1, sig2):
    """ Estima el desfase entre dos señales usando FFT. """
    N = len(sig1) + len(sig2) - 1  # Longitud de la correlación cruzada
    f1 = fft(sig1, N)
    f2 = fft(sig2, N)
    
    # Cross-power spectrum normalization
    cross_power = f1 * np.conj(f2)
    cross_power /= np.abs(cross_power)  # Solo fase, eliminamos magnitud
    
    # Correlación cruzada inversa
    cross_corr = np.real(ifft(cross_power))
    cross_corr = fftshift(cross_corr)  # Centrar la correlación
    
    # Encontrar el desfase óptimo
    max_index = np.argmax(cross_corr)
    delay_samples = max_index - (N // 2)
    
    return delay_samples, cross_corr


def calculate_angular_velocity_from_quaternions(quaternions, timestamps):
    angular_velocities = []

    # Calcular la primera velocidad angular de manera aproximada
    q1 = R.from_quat(quaternions[0])  # Cuaternión en el tiempo t0
    q2 = R.from_quat(quaternions[1])  # Cuaternión en el tiempo t1
    delta_q_first = q2 * q1.inv()  # Diferencia entre t1 y t0

    # Calcular la velocidad angular centrada (aproximación para el primer valor)
    omega_first = delta_q_first.magnitude() / (timestamps[1] - timestamps[0])  # Velocidad angular para el primer valor
    axis_first = delta_q_first.as_rotvec() / (timestamps[1] - timestamps[0])
    angular_velocities.append(axis_first)

    # Recorrer los cuaterniones desde el segundo hasta el penúltimo, para tener los dos cuaterniones necesarios
    for i in range(1, len(quaternions) - 1):  
        # Diferencias de cuaterniones entre t-1, t, t+1
        q1 = R.from_quat(quaternions[i - 1])  # Cuaternión en el tiempo t-1
        q2 = R.from_quat(quaternions[i])      # Cuaternión en el tiempo t
        q3 = R.from_quat(quaternions[i + 1])  # Cuaternión en el tiempo t+1

        # Calcular la diferencia centrada en cuaterniones: q(t+1) * q(t-1)^(-1)
        delta_q = q3 * q1.inv()  # Diferencia centrada

        # Calcular el ángulo y eje de rotación (en radianes)
        omega = delta_q.magnitude() / (timestamps[i + 1] - timestamps[i - 1])  # Velocidad angular centrada

        # Convertir a un vector de velocidad angular (en rad/s)
        axis = delta_q.as_rotvec() / (timestamps[i + 1] - timestamps[i - 1])
        
        angular_velocities.append(axis)

    return np.array(angular_velocities)



# Función para leer los datos IMU sin modificar los timestamps
def read_imu_data(file_path):
    imu_data = pd.read_csv(file_path, delim_whitespace=True, comment='#', header=None)
    imu_data.columns = ['timestamp', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
    
    return imu_data

# Función para leer el archivo de datos de cámara sin modificar los timestamps
def read_camera_data(file_path):
    camera_data = pd.read_csv(file_path, delim_whitespace=True, comment='#', header=None)
    camera_data.columns = ['timestamp', 'qx', 'qy', 'qz', 'qw', 'x', 'y', 'z']

    return camera_data

# Sincronización de datos basada en timestamp
def synchronize_data(imu_data, camera_data):
    # Convertir ambos timestamps a float para evitar problemas con el formato
    imu_data['timestamp'] = imu_data['timestamp'].astype(float)
    camera_data['timestamp'] = camera_data['timestamp'].astype(float)
    
    # Crear una lista para almacenar los datos sincronizados
    synchronized_data_list = []
    
    # Iterar sobre los datos de la cámara y buscar la sincronización más cercana en los datos IMU
    for _, row in camera_data.iterrows():
        timestamp_camera = row['timestamp']
        closest_imu_idx = (np.abs(imu_data['timestamp'] - timestamp_camera)).idxmin()
        imu_row = imu_data.iloc[closest_imu_idx]
        
        # Agregar la información sincronizada a la lista
        synchronized_data_list.append({
            'timestamp': timestamp_camera,
            'accel_x': imu_row['accel_x'],
            'accel_y': imu_row['accel_y'],
            'accel_z': imu_row['accel_z'],
            'gyro_x': imu_row['gyro_x'],
            'gyro_y': imu_row['gyro_y'],
            'gyro_z': imu_row['gyro_z'],
            'X': row['x'],
            'Y': row['y'],
            'Z': row['z'], 
            'qX': row['qx'],
            'qY': row['qy'],
            'qZ': row['qz'],
            'qW': row['qw'],
        })
    
    # Convertir la lista de datos sincronizados a un DataFrame
    synchronized_data = pd.DataFrame(synchronized_data_list)
    
    return synchronized_data

# Graficar los datos de IMU y la posición de la cámara en función del timestamp real
def plot_data(synchronized_data):

        # Definir la matriz de transformación de la cámara a la IMU
    #transformation_matrix = np.array([
    #    [0.0211126, 0.999762, 0.00540811],
    #    [-0.999615, 0.0210114, 0.0181231],
    #    [0.0180052, -0.00578865, 0.999821]
    #])

    transformation_matrix = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ])

    transformation_matrix = np.array([
    [-1, 0, 0],
    [0, 0, -1],
    [0, 1, 0]
    ])

    # Window size for smoothing filter
    window_size_est = 80
    window_size_imu = 15

    # Define start time as 11 seconds after the first timestamp
    start_time = synchronized_data['timestamp'].min() + 12
    synchronized_data = synchronized_data[synchronized_data['timestamp'] >= start_time]

    # Limit visualization to 3.5 seconds
    max_time = start_time + 20
    synchronized_data = synchronized_data[synchronized_data['timestamp'] <= max_time]

    ### Angular velocity estimation
    quaternions = synchronized_data[['qX', 'qY', 'qZ', 'qW']].values
    timestamps = synchronized_data['timestamp'].values
    angular_velocities = calculate_angular_velocity_from_quaternions(quaternions, timestamps)

    # Transform angular velocities from camera coordinates to IMU coordinates
    angular_velocities_coord_imu = np.dot(transformation_matrix.T, angular_velocities.T).T

    # Apply smoothing filter
    angular_velocities_coord_imu_smooth = uniform_filter1d(angular_velocities_coord_imu[:, 0], size=window_size_est)
    gyro_smooth = uniform_filter1d(synchronized_data['gyro_x'], size=window_size_imu)

    ### Compute time step (sampling interval)
    time_step = np.mean(np.diff(timestamps))  # Average time step in seconds
    time_step_ms = time_step * 1000  # Convert to milliseconds
    # Calcular el desfase óptimo
    delay_samples, cross_corr = estimate_delay_fft(angular_velocities_coord_imu_smooth, gyro_smooth)

    # Convertir desfase a milisegundos
    delay_ms = (delay_samples) * time_step_ms

    # Ajustar el tiempo para que comience desde cero
    time_relative = timestamps[1:] - timestamps[1]
    time_imu_relative = synchronized_data['timestamp'] - synchronized_data['timestamp'].iloc[0]



    ### Plot results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    # Plot angular velocity
        # Plot angular velocity
    ax1.plot(time_relative, angular_velocities_coord_imu_smooth, label='estimated', color='r', linestyle='-', linewidth=2)
    ax1.plot(time_imu_relative, gyro_smooth, label='IMU gyr', color='black', linestyle='-', linewidth=2)
    #ax1.plot(timestamps[1:], angular_velocities_coord_imu_smooth, label='estimated', color='r', linestyle='-', linewidth=2)
    #ax1.plot(synchronized_data['timestamp'], gyro_smooth, label='IMU', color='black', linestyle='-', linewidth=2)

    ax1.set_xlabel('time [s]')
    ax1.set_ylabel('angular velocity [rad/s]')
    # Agregar leyenda con fondo blanco y borde negro
    ax1.legend(facecolor='white', edgecolor='black', loc='upper right')
    # Definir los ticks del eje X cada 2 segundos
    ax1.set_xticks(np.arange(0, max(time_relative), 1.5))
    # Establecer los límites del eje X
    ax1.set_xlim([0, max(time_relative)])

    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)  # 'both' activa grilla menor y mayor


    #ax1.set_title('Angular Velocity on')
    ax1.grid(True)

    # Definir el rango de interés en milisegundos
    min_lag_ms = -100
    max_lag_ms = 100

    # Crear el array de desfases en ms
    lags = np.arange(-len(cross_corr)//2 , len(cross_corr)//2) * time_step_ms

    # Filtrar los valores dentro del rango deseado
    valid_indices = (lags >= min_lag_ms) & (lags <= max_lag_ms)
    lags_filtered = lags[valid_indices]
    cross_corr_filtered = abs(cross_corr[valid_indices])

    # Graficar la correlación cruzada en el rango limitado
    ax2.plot(lags_filtered, cross_corr_filtered, color='blue', linewidth=2)
    #ax2.axvline(x=delay_ms, color='red', linestyle='--', label=f'Estimated Delay: {delay_ms:.2f} ms')
    # Establecer las marcas de los ejes X y Y con los intervalos deseados
    ax2.set_xticks(np.arange(min_lag_ms, max_lag_ms + 1, 10))  # Intervalo de 10 ms para el eje X
    ax2.set_yticks(np.arange(0, max(cross_corr_filtered), 0.1))  # Intervalo de 0.01 para el eje Y
    ax2.set_xlim([min_lag_ms, max_lag_ms])

    ax2.set_xlabel('temporal offset [ms]')
    ax2.set_ylabel('Cross-Correlation')

    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)  # 'both' activa grilla menor y mayor

    plt.tight_layout()

    # Guardar la imagen
    plt.savefig("sync_fft.png", dpi=300)  # Guardar con resolución de 300 dpi
    plt.show()

# Leer y sincronizar los datos
imu_data = read_imu_data(imu_path)
camera_data = read_camera_data(groundtruth_path)
synchronized_data = synchronize_data(imu_data, camera_data)

# Graficar los datos en función del timestamp real
plot_data(synchronized_data)


# usage: 
# python3 sync.py --input 2-natural-tr-data