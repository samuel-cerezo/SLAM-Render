<p align="center">
  <h1 align="center">SLAM&Render: A Benchmark for the Intersection Between Neural Rendering, Gaussian Splatting and SLAM</h1>
  <p align="center">
    <a href="https://samuel-cerezo.github.io/"><strong>Samuel Cerezo</strong></a> ·
    <a><strong>Gaetano Meli</strong></a> ·
    <a><strong>Tomas Berriel</strong></a> ·
    <a><strong>Kirill Safronov</strong></a> ·
    <a><strong>Javier Civera</strong></a>
  </p>
  <h3 align="center">2025 (repository under development)</h3>
  <p align="center"><a>Paper</a> | <a>Video</a> | <a href="https://samuel-cerezo.github.io/SLAM&Render.html">Project Page</a></p>
</p>

<p align="center">
  <img src="./media/light-conditions.png" alt="teaser" width="100%">
</p>

---

## 📌 Overview

Existing datasets fail to include the specific challenges of two fields: 
- **Multi-modality** and **sequentiality** in SLAM.
- **Generalization across viewpoints and lighting** in Neural Rendering.

We introduce **SLAM&Render**, a novel dataset designed to explore the intersection of both domains. It includes:
- 40 real-world sequences.
- Synchronized RGB, depth, IMU, robot encoders, and ground-truth poses.

---

## 📁 Dataset Structure

Each sequence contains:

```
sequence_name/
├── rgb/               # RGB images (30 Hz)
├── depth/             # Aligned depth images
├── imu.csv            # Accelerometer + gyroscope (200 Hz)
├── joint_states.csv   # Robot joint encoders (1 kHz)
├── flange_pose.csv    # Forward kinematics pose
├── groundtruth.csv    # MoCap ground truth (120 Hz)
```

> See [`data/README.md`](data/README.md) for full details.

---

## 🚀 Getting Started

```bash
git clone https://github.com/samuel-cerezo/slam-render.git
cd slam-render
pip install -r requirements.txt
```

To download a sequence:

```bash
python scripts/download_data.py --sequence 4-natural
```

---

## 🛠️ Examples & Tools

We provide utility scripts to align and use the dataset easily:

| Script | Description |
|--------|-------------|
| `scripts/temporal_align.py` | Align timestamps between RGB and sensor data. |
| `scripts/fFlange2world.py` | Align poses to a world frame using motion capture. |
| `slamrender/alignment_utils.py` | Core functions for spatial and temporal alignment. |

> See the notebook [`notebooks/example_usage.ipynb`](notebooks/example_usage.ipynb) for a full pipeline.

---

## 🧪 Evaluation

Coming soon:
- SLAM benchmark scripts (ATE, RPE).
- Neural Rendering evaluation (PSNR, LPIPS, Chamfer).

---

## 🤝 Acknowledgements

This work builds on many open-source projects including:
- COLMAP
- GaussianSplats3D
- ROS/TF
- Evo (for trajectory evaluation)

---

## 📄 License

Released under the [LICENSE.md](LICENSE.md).

---

## 📚 Citation

If you find this dataset or code useful, please cite us:

```bibtex
@misc{slamrender2025,
  title={SLAM\&Render: A Benchmark for the Intersection Between Neural Rendering and SLAM},
  author={Samuel Cerezo and Gaetano Meli and Tomas Berriel and Kirill Safronov and Javier Civera},
  year={2025},
  howpublished={\url{https://github.com/samuel-cerezo/slam-render}}
}
```

---

## 🌐 Links

- 📄 [Project Page](https://samuel-cerezo.github.io/SLAM&Render)
- 📦 [Demo Viewer (GaussianSplats3D)](https://samuel-cerezo.github.io/models/4-natural.ply)

---



