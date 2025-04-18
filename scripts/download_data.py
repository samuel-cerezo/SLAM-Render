import argparse
import os
import requests
from tqdm import tqdm
import zipfile

SEQUENCES = {
    "setup-1-natural-train": "https://zenodo.org/records/15000694/files/1-natural-tr.zip?download=1",
    "setup-1-natural-test": "https://zenodo.org/records/15000694/files/1-natural-tt.zip?download=1",
    "setup-1-dark-train": "https://zenodo.org/records/15000694/files/1-dark-tr.zip?download=1",
    "setup-1-dark-test": "https://zenodo.org/records/15000694/files/1-dark-tt.zip?download=1",
    "setup-1-warm-train": "https://zenodo.org/records/15000694/files/1-warm-tr.zip?download=1",
    "setup-1-warm-test": "https://zenodo.org/records/15000694/files/1-warm-tt.zip?download=1",
    "setup-1-cold-train": "https://zenodo.org/records/15000694/files/1-cold-tr.zip?download=1",
    "setup-1-cold-test": "https://zenodo.org/records/15000694/files/1-cold-tt.zip?download=1",

    "setup-2-natural-train": "https://zenodo.org/records/15000694/files/2-natural-tr.zip?download=1",
    "setup-2-natural-test": "https://zenodo.org/records/15000694/files/2-natural-tt.zip?download=1",
    "setup-2-dark-train": "https://zenodo.org/records/15000694/files/2-dark-tr.zip?download=1",
    "setup-2-dark-test": "https://zenodo.org/records/15000694/files/2-dark-tt.zip?download=1",
    "setup-2-warm-train": "https://zenodo.org/records/15000694/files/2-warm-tr.zip?download=1",
    "setup-2-warm-test": "https://zenodo.org/records/15000694/files/2-warm-tt.zip?download=1",
    "setup-2-cold-train": "https://zenodo.org/records/15000694/files/2-cold-tr.zip?download=1",
    "setup-2-cold-test": "https://zenodo.org/records/15000694/files/2-cold-tt.zip?download=1",

    "setup-3-natural-train": "https://zenodo.org/records/15000694/files/3-natural-tr.zip?download=1",
    "setup-3-natural-test": "https://zenodo.org/records/15000694/files/3-natural-tt.zip?download=1",
    "setup-3-dark-train": "https://zenodo.org/records/15000694/files/3-dark-tr.zip?download=1",
    "setup-3-dark-test": "https://zenodo.org/records/15000694/files/3-dark-tt.zip?download=1",
    "setup-3-warm-train": "https://zenodo.org/records/15000694/files/3-warm-tr.zip?download=1",
    "setup-3-warm-test": "https://zenodo.org/records/15000694/files/3-warm-tt.zip?download=1",
    "setup-3-cold-train": "https://zenodo.org/records/15000694/files/3-cold-tr.zip?download=1",
    "setup-3-cold-test": "https://zenodo.org/records/15000694/files/3-cold-tt.zip?download=1",

    "setup-4-natural-train": "https://zenodo.org/records/15000939/files/4-natural-tr.zip?download=1",
    "setup-4-natural-test": "https://zenodo.org/records/15000939/files/4-natural-tt.zip?download=1",
    "setup-4-dark-train": "https://zenodo.org/records/15000939/files/4-dark-tr.zip?download=1",
    "setup-4-dark-test": "https://zenodo.org/records/15000939/files/4-dark-tt.zip?download=1",
    "setup-4-warm-train": "https://zenodo.org/records/15000939/files/4-warm-tr.zip?download=1",
    "setup-4-warm-test": "https://zenodo.org/records/15000939/files/4-warm-tt.zip?download=1",
    "setup-4-cold-train": "https://zenodo.org/records/15000939/files/4-cold-tr.zip?download=1",
    "setup-4-cold-test": "https://zenodo.org/records/15000939/files/4-cold-tt.zip?download=1",

    "setup-5-natural-train": "https://zenodo.org/records/15000939/files/5-natural-tr.zip?download=1",
    "setup-5-natural-test": "https://zenodo.org/records/15000939/files/5-natural-tt.zip?download=1",
    "setup-5-dark-train": "https://zenodo.org/records/15000939/files/5-dark-tr.zip?download=1",
    "setup-5-dark-test": "https://zenodo.org/records/15000939/files/5-dark-tt.zip?download=1",
    "setup-5-warm-train": "https://zenodo.org/records/15000939/files/5-warm-tr.zip?download=1",
    "setup-5-warm-test": "https://zenodo.org/records/15000939/files/5-warm-tt.zip?download=1",
    "setup-5-cold-train": "https://zenodo.org/records/15000939/files/5-cold-tr.zip?download=1",
    "setup-5-cold-test": "https://zenodo.org/records/15000939/files/5-cold-tt.zip?download=1",
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
