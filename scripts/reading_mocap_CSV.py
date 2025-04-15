import pandas as pd
import csv
import argparse
from datetime import datetime
import os

# Función para cargar y extraer los datos del archivo CSV
def extract_metadata(file_name):
    frame_rate = None
    capture_start_time = None
    total_exported_frames = None

    try:
        with open(file_name, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                # Extraer información de la primera fila
                if row[0] == "Format Version":
                    # Parsear valores necesarios
                    frame_rate = row[row.index("Capture Frame Rate") + 1]
                    capture_start_time = row[row.index("Capture Start Time") + 1]
                    total_exported_frames = row[row.index("Total Exported Frames") + 1]
                    break
        # Convertir la hora de inicio de captura a objeto datetime
        time_obj = datetime.strptime(capture_start_time, "%Y-%m-%d %I.%M.%S.%f %p")
        # Convertir a timestamp Unix
        #zero_unix_time_sec = int(time_obj.timestamp())
        zero_unix_time_sec = time_obj.timestamp()  # No usar int(), para no perder mseg

        return frame_rate, capture_start_time, total_exported_frames, zero_unix_time_sec
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return None

# Función para limpiar y procesar los datos
def process_data(file_name, zero_unix_time_sec):
    try:
        # Cargar el archivo CSV en un DataFrame
        df = pd.read_csv(file_name, skiprows=6)

        # Filtrar las columnas necesarias
        filtered_data = df[['Time (Seconds)', 'qX', 'qY', 'qZ', 'qW', 'X', 'Y', 'Z']].copy()

        # Renombrar las columnas para mayor claridad
        filtered_data.columns = ['Time', 'qX', 'qY', 'qZ', 'qW', 'PosX', 'PosY', 'PosZ']

        # Convertir 'Time' a formato numérico
        filtered_data.loc[:, "Time"] = pd.to_numeric(filtered_data["Time"], errors="coerce")

        # Añadir el tiempo de inicio
        filtered_data.loc[:, "Time"] += zero_unix_time_sec

        # Eliminar filas con valores NaN
        filtered_data = filtered_data.dropna()

        filtered_data["Time"] = filtered_data["Time"].apply(lambda x: f"{x:.9f}")
        filtered_data["Time"] = filtered_data["Time"].astype(str)  # Asegura que todo sea de tipo str

        return filtered_data
    except Exception as e:
        print(f"Error al procesar los datos: {e}")
        return None

# Función para guardar los datos procesados en un archivo de texto
def save_output(filtered_data, output_file_name):
    try:
        output_text = "#timestamp qx qy qz qw tx ty tz\n"
        output_text += "\n".join(
            filtered_data.apply(lambda row: " ".join(map(str, row)), axis=1)
        )

        # Guardar el archivo de salida
        with open(output_file_name, "w") as file:
            file.write(output_text)

        print(f"Archivo de salida guardado como {output_file_name}")
        return output_file_name
    except Exception as e:
        print(f"Error al guardar el archivo de salida: {e}")
        return None

# Función principal
def main():
    # Configuración de argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Procesar un archivo CSV con datos de captura y generar un archivo de texto de salida.")
    parser.add_argument("--input", help="Nombre del dataset (sin la ruta completa)", type=str, required=True)

    # Obtener el nombre del dataset desde los argumentos
    args = parser.parse_args()

    # Construir la ruta completa del archivo CSV
    #dataset_path = f"/home/samuel/dev/environment_modeling/ROSBAGS/{args.input}/{args.input}.csv"
    #dataset_path = f"/Volumes/SSD/archivos/KUKA_notebook/dev/environment_modeling/ROSBAGS/{args.input}/{args.input}.csv"
    dataset_path = f"/Volumes/SSD/archivos/KUKA_dev/environment_modeling/ROSBAGS/{args.input}/groundtruth_raw.csv"
                    
    # Verificar si el archivo existe
    if not os.path.exists(dataset_path):
        print(f"Error: El archivo {dataset_path} no existe.")
        return

    # Extraer metadatos del archivo CSV
    metadata = extract_metadata(dataset_path)
    if not metadata:
        return

    frame_rate, capture_start_time, total_exported_frames, zero_unix_time_sec = metadata

    # Mostrar los metadatos extraídos
    print(f"Frame Rate: {frame_rate}")
    print(f"Capture Start Time: {capture_start_time}")
    print(f"Capture Start Time (Unix): {zero_unix_time_sec:.9f}")
    print(f"Total Exported Frames: {total_exported_frames}")

    # Procesar los datos del archivo CSV
    filtered_data = process_data(dataset_path, zero_unix_time_sec)
    if filtered_data is None:
        return

    # Obtener la carpeta donde está el archivo CSV
    file_dir = os.path.dirname(dataset_path)
    # Construir el nombre del archivo de salida
#    output_file_name = os.path.join(file_dir, f"groundtruth_{args.input}.txt")
    output_file_name = os.path.join(file_dir, f"groundtruth.txt")

    # Guardar los resultados procesados en un archivo de texto
    save_output(filtered_data, output_file_name)

if __name__ == "__main__":
    main()

# uso:
#       primero, ir a la fila 7 y reemplazar "Frame,Time (Seconds),X,Y,Z,W,X,Y,Z,,,,,,,,,,,,," por  "Frame,Time (Seconds),qX,qY,qZ,qW,X,Y,Z,,,,,,,,,,,,,"
#       si no esta en la fila 7, hay que cambiar la linea de codigo " df = pd.read_csv(file_name, skiprows=6)", que saltea las primeras 6 lineas.}
# run:
#       python3 reading_mocap_CSV.py --input nombre-dataset

#INFO: (el archivo .csv tiene el mismo nombre que el dataset ubicado en la carpeta ROSBAGS)
 