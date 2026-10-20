# CatMAE Reproduction on DAVIS-2017 (Self-Supervised Video Object Segmentation)

Reproduction of the DAVIS-2017 semi-supervised video object segmentation results of
**CatMAE** (*Concatenated Masked Autoencoders as Spatial-Temporal Learner*, Jiang et al., 2023),
using the authors' released ViRe-trained checkpoints. No retraining is involved: a frozen
pretrained encoder extracts features, and the first-frame mask is propagated through the video by
nearest-neighbour feature matching.

Part of an M.Tech project on self-supervised video object segmentation (IIT Kharagpur).
The next phase is failure analysis and benchmark it against current SOTA memory-based VOS (XMem, Cutie, SAM2), Reproduce T-Core, then stress-test it against CATMAE failure cases.

## Results (DAVIS-2017 val, 30 videos)

| Model | Paper J&F | Reproduced J&F |
|---|---|---|
| CatMAE-ViRe ViT-S/16 | 62.5 | 62.57 |
| CatMAE-ViRe ViT-S/8  | 70.4 | 70.60 |

Per-sequence and global J / F / J&F tables are in [`results/`](results/).

## Observed failure cases (ViT-S/16 run)

- `lab-coat_1`, `lab-coat_2`: J = F = 0.0. Several people in similar white coats appear in the same
  frame, and appearance-only matching has no mechanism to keep identities apart.
- `kite-surf_1/2`, `scooter-black_1`, `shooting_1`: low scores (J around 0.1 to 0.25), consistent
  with small objects and large frame-to-frame motion.

These explanations are hypotheses consistent with how the method works (pure correspondence, no memory
or re-detection), not separately tested.

## Reproducing

Tested on a Kaggle GPU notebook. Use any working directory in place of `/kaggle/working`.

```bash
WORK=/kaggle/working

# 1. Code and dependencies
git clone https://github.com/minhoooo1/CatMAE.git $WORK/CatMAE
pip install timm opencv-python matplotlib scikit-image imageio scikit-learn visdom wandb gdown tqdm

# 2. Released checkpoints
mkdir -p $WORK/checkpoints
gdown 1xWrpSxZy6d3r_XnsZmXvqM1XUReJ7v97 -O $WORK/checkpoints/catmae_vits16.pth
gdown 1ksYZJPa2pZ-NYWjYKLh05-bt_A40Rhm7 -O $WORK/checkpoints/catmae_vits8.pth

# 3. DAVIS-2017 (480p) and conversion to the 480x880 format the evaluation expects
cd $WORK/CatMAE/downstream/davis2017-seg
mkdir -p data
wget -q -P ./data https://data.vision.ee.ethz.ch/csergi/share/davis/DAVIS-2017-trainval-480p.zip
unzip -q ./data/DAVIS-2017-trainval-480p.zip -d ./data
cp -r data/DAVIS data/DAVIS_480_880
python convert_480_880.py

# 4. Metric code
git clone https://github.com/davisvideochallenge/davis2017-evaluation.git $WORK/davis2017-evaluation

# 5. Memory patch (needed for ViT-S/8, see below)
python patch_catmae_ram.py $WORK/CatMAE/downstream/davis2017-seg/code
```

### ViT-S/16

```bash
cd $WORK/CatMAE/downstream/davis2017-seg
python code/test_mae.py --model-type vits16 --resume $WORK/checkpoints/catmae_vits16.pth \
  --gpu-id 0 --workers 0 \
  --save-path results/catmae_vits16/T07_K8_R18_V20 \
  --temperature 0.7 --topk 8 --radius 18 --videoLen 20 \
  --filelist davis_vallist_480_880.txt

python code/eval/convert_davis.py \
  --in_folder results/catmae_vits16/T07_K8_R18_V20/ \
  --out_folder results/catmae_vits16/T07_K8_R18_V20_out/ \
  --dataset data/DAVIS_480_880

python $WORK/davis2017-evaluation/evaluation_method.py \
  --davis_path $WORK/CatMAE/downstream/davis2017-seg/data/DAVIS_480_880 \
  --set val --task semi-supervised \
  --results_path $WORK/CatMAE/downstream/davis2017-seg/results/catmae_vits16/T07_K8_R18_V20_out/
```

### ViT-S/8

```bash
cd $WORK/CatMAE/downstream/davis2017-seg
python code/test_mae.py --model-type vits8 --resume $WORK/checkpoints/catmae_vits8.pth \
  --gpu-id 0 --workers 0 \
  --save-path results/catmae_vits8/T05_K12_R32_V20 \
  --temperature 0.5 --topk 12 --radius 32 --videoLen 20 \
  --filelist davis_vallist_480_880.txt

python code/eval/convert_davis.py \
  --in_folder results/catmae_vits8/T05_K12_R32_V20/ \
  --out_folder results/catmae_vits8/T05_K12_R32_V20_out/ \
  --dataset data/DAVIS_480_880

python $WORK/davis2017-evaluation/evaluation_method.py \
  --davis_path $WORK/CatMAE/downstream/davis2017-seg/data/DAVIS_480_880 \
  --set val --task semi-supervised \
  --results_path $WORK/CatMAE/downstream/davis2017-seg/results/catmae_vits8/T05_K12_R32_V20_out/
```

The ViT-S/8 pass took about 1 h 18 min for the 30 validation videos in my run.

## Why `patch_catmae_ram.py`?

With ViT-S/8 (6,600 tokens per frame), the original `test_mae.py` builds a "key bank" in host RAM in which
every target frame gets its own copy of 21 context-frame feature maps. That is roughly 6 to 17 GB per
video depending on its length, and the previous video's copy is still alive while the next one is
built, so the process was killed by the Linux OOM killer (exit status 137, a bare `Killed` message).
`--workers 0` does not prevent this.

The patch gathers the context features for two target frames at a time inside
`mem_efficient_batched_affinity` and frees each video's tensors before the next one starts. The
tensors fed to the affinity computation were checked to be identical to the original on a small
synthetic test; the full-run result is the table above.

## Contents

| Path | What it is |
|---|---|
| `*.ipynb` | The Kaggle notebook with all cells and their outputs |
| `patch_catmae_ram.py` | Host-RAM patch for the CatMAE DAVIS evaluation code |
| `results/` | Global and per-sequence J / F tables for both models |

This repository does not redistribute the CatMAE code, checkpoints, or the DAVIS data.

## Credits

- CatMAE: Z. Jiang et al., *Concatenated Masked Autoencoders as Spatial-Temporal Learner*, arXiv:2311.00961. Code and checkpoints: https://github.com/minhoooo1/CatMAE
- DAVIS metric code: https://github.com/davisvideochallenge/davis2017-evaluation
