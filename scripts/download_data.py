import argparse
import os
import requests
from tqdm import tqdm
import zipfile

SEQUENCES = {
    "setup-1-warm-train": "https://zenodo.org/record/.../files/1-warm-train.zip?download=1",
    "setup-1-warm-test": "https://zenodo.org/record/.../files/1-warm-test.zip?download=1",
    "setup-1-cold-train": "https://zenodo.org/record/.../files/1-cold-train.zip?download=1",
    # ...
    "setup-5-dark-test": "https://zenodo.org/record/.../files/5-dark-test.zip?download=1",
}

def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    total = int(response.headers.get('content-length', 0))

    with open(dest_path, 'wb') as file, tqdm(
        desc=dest_path,
        total=total,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sequence', type=str, required=True, help="Name of the sequence to download (e.g. 4-natural-test)")
    args = parser.parse_args()

    if args.sequence not in SEQUENCES:
        print(f"Sequence '{args.sequence}' not found.")
        print("Available sequences:", ", ".join(SEQUENCES.keys()))
        return

    url = SEQUENCES[args.sequence]
    os.makedirs('data', exist_ok=True)
    zip_path = os.path.join('data', f"{args.sequence}.zip")

    print(f"Downloading sequence: {args.sequence}")
    download_file(url, zip_path)

    print("Unzipping...")
    unzip_file(zip_path, "data")
    os.remove(zip_path)
    print("Done!")

if __name__ == "__main__":
    main()
