# CatMAE Failure Analysis on DAVIS-2017 (val)

Per-sequence analysis of the CatMAE-ViRe ViT-S/16 and ViT-S/8 reproduction. Source data: `results/vits16_per-sequence_results-val.csv` and `results/vits8_per-sequence_results-val.csv`.

Scores are per object (61 objects across the 30 val videos, so a video such as `lab-coat` appears as `lab-coat_1`, `lab-coat_2`, ...). J&F = (J + F) / 2 per object. The mean over objects reproduces the global numbers: **62.57** (S/16) and **70.60** (S/8).

## 1. Global metrics

| Metric | ViT-S/16 | ViT-S/8 |
|---|---|---|
| J&F-Mean | 0.626 | 0.706 |
| J-Mean / J-Recall / J-Decay | 0.597 / 0.715 / 0.147 | 0.676 / 0.804 / 0.163 |
| F-Mean / F-Recall / F-Decay | 0.655 / 0.786 / 0.212 | 0.736 / 0.859 / 0.212 |
| Objects with J&F < 0.30 | 9 | 5 |

## 2. Ten worst objects (ranked by ViT-S/16 J&F)

| Sequence | J&F (S/16) | J&F (S/8) | Change |
|---|---|---|---|
| `lab-coat_2` | 0.000 | 0.000 | +0.000 |
| `lab-coat_1` | 0.000 | 0.000 | +0.000 |
| `paragliding-launch_3` | 0.029 | 0.095 | +0.066 |
| `dogs-jump_1` | 0.193 | 0.607 | +0.415 |
| `shooting_1` | 0.233 | 0.243 | +0.010 |
| `scooter-black_1` | 0.239 | 0.746 | +0.507 |
| `kite-surf_1` | 0.242 | 0.337 | +0.095 |
| `kite-surf_2` | 0.254 | 0.265 | +0.012 |
| `soapbox_3` | 0.280 | 0.635 | +0.355 |
| `soapbox_2` | 0.311 | 0.635 | +0.324 |

## 3. Two groups of failures

Comparing the two patch sizes splits the failures into two groups.

### 3.1 Persistent failures (not fixed by finer patches)

| Sequence | J&F (S/16) | J&F (S/8) | Change |
|---|---|---|---|
| `lab-coat_2` | 0.000 | 0.000 | +0.000 |
| `lab-coat_1` | 0.000 | 0.000 | +0.000 |
| `paragliding-launch_3` | 0.029 | 0.095 | +0.066 |
| `shooting_1` | 0.233 | 0.243 | +0.010 |
| `kite-surf_1` | 0.242 | 0.337 | +0.095 |
| `kite-surf_2` | 0.254 | 0.265 | +0.012 |

Going from 16x16 to 8x8 patches changes these by at most +0.10, so patch resolution is unlikely to be the main cause.

Hypotheses (not yet tested):
- `lab-coat_1/2` (J = F = 0 at both sizes): several people in similar white coats appear in the same frame. Appearance-only nearest-neighbour matching has no mechanism to separate identities.
- `paragliding-launch_3`, `kite-surf_1/2`, `shooting_1`: possibly small objects against large, fairly uniform backgrounds combined with large motion. This needs to be confirmed on the mask overlays.

### 3.2 Resolution-limited failures (fixed largely by finer patches)

| Sequence | J&F (S/16) | J&F (S/8) | Change |
|---|---|---|---|
| `scooter-black_1` | 0.239 | 0.746 | +0.507 |
| `dogs-jump_1` | 0.193 | 0.607 | +0.415 |
| `soapbox_3` | 0.280 | 0.635 | +0.355 |
| `soapbox_2` | 0.311 | 0.635 | +0.324 |
| `dogs-jump_2` | 0.508 | 0.759 | +0.251 |
| `mbike-trick_1` | 0.501 | 0.719 | +0.218 |

These gain 0.2 to 0.5 J&F from S/16 to S/8. Hypothesis (untested): objects too small for a 16x16 patch grid to localise, which an 8x8 grid recovers.

### 3.3 Sequences where ViT-S/8 is worse than ViT-S/16

| Sequence | J&F (S/16) | J&F (S/8) | Change |
|---|---|---|---|
| `drift-chicane_1` | 0.732 | 0.580 | -0.152 |
| `india_3` | 0.566 | 0.512 | -0.053 |
| `car-shadow_1` | 0.917 | 0.885 | -0.032 |
| `bmx-trees_1` | 0.479 | 0.460 | -0.019 |
| `gold-fish_4` | 0.846 | 0.831 | -0.015 |
| `motocross-jump_2` | 0.643 | 0.633 | -0.010 |
| `goat_1` | 0.835 | 0.827 | -0.008 |
| `shooting_2` | 0.750 | 0.749 | -0.001 |

The largest drop is `drift-chicane_1` (-0.152). Finer patches are not a uniform improvement.

## 4. Open question for the next phase

T-CoRe (CVPR 2025) releases a ViT-S/16 checkpoint. At the same patch size as the weaker CatMAE model, does it:
1. fix the persistent failures in 3.1, and
2. recover the resolution-limited sequences in 3.2 without finer patches?

Comparison set: the six sequences in 3.1 plus `scooter-black_1`, `dogs-jump_1`, `soapbox_2`, `soapbox_3`. Results will be added in `tcore_comparison.md` once the T-CoRe run is scored with the same evaluation code.

## 5. Limitations

- The explanations in section 3 are hypotheses that fit how the method works (pure feature correspondence, no memory or re-detection). They have not been separately tested; mask overlays on the failing sequences are the planned check.
- The scores come from one run per model with the settings in the main README.

## Appendix: full per-object results (sorted by ViT-S/16 J&F, ascending)

| Sequence | J (S/16) | F (S/16) | J&F (S/16) | J (S/8) | F (S/8) | J&F (S/8) |
|---|---|---|---|---|---|---|
| `lab-coat_2` | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| `lab-coat_1` | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| `paragliding-launch_3` | 0.013 | 0.045 | 0.029 | 0.029 | 0.160 | 0.095 |
| `dogs-jump_1` | 0.130 | 0.255 | 0.193 | 0.506 | 0.709 | 0.607 |
| `shooting_1` | 0.220 | 0.246 | 0.233 | 0.234 | 0.252 | 0.243 |
| `scooter-black_1` | 0.109 | 0.370 | 0.239 | 0.654 | 0.839 | 0.746 |
| `kite-surf_1` | 0.222 | 0.262 | 0.242 | 0.280 | 0.393 | 0.337 |
| `kite-surf_2` | 0.250 | 0.257 | 0.254 | 0.256 | 0.274 | 0.265 |
| `soapbox_3` | 0.167 | 0.393 | 0.280 | 0.586 | 0.684 | 0.635 |
| `soapbox_2` | 0.254 | 0.368 | 0.311 | 0.604 | 0.666 | 0.635 |
| `loading_2` | 0.330 | 0.410 | 0.370 | 0.427 | 0.578 | 0.502 |
| `drift-straight_1` | 0.514 | 0.377 | 0.446 | 0.609 | 0.540 | 0.575 |
| `bmx-trees_1` | 0.283 | 0.675 | 0.479 | 0.285 | 0.635 | 0.460 |
| `bike-packing_1` | 0.406 | 0.572 | 0.489 | 0.495 | 0.683 | 0.589 |
| `mbike-trick_1` | 0.412 | 0.590 | 0.501 | 0.652 | 0.786 | 0.719 |
| `dogs-jump_2` | 0.460 | 0.555 | 0.508 | 0.740 | 0.778 | 0.759 |
| `motocross-jump_1` | 0.486 | 0.551 | 0.518 | 0.534 | 0.567 | 0.550 |
| `india_3` | 0.574 | 0.557 | 0.566 | 0.513 | 0.511 | 0.512 |
| `india_2` | 0.593 | 0.585 | 0.589 | 0.632 | 0.620 | 0.626 |
| `kite-surf_3` | 0.475 | 0.705 | 0.590 | 0.671 | 0.923 | 0.797 |
| `gold-fish_2` | 0.594 | 0.627 | 0.611 | 0.763 | 0.854 | 0.808 |
| `paragliding-launch_2` | 0.465 | 0.760 | 0.613 | 0.615 | 0.855 | 0.735 |
| `bmx-trees_2` | 0.538 | 0.735 | 0.637 | 0.589 | 0.836 | 0.712 |
| `mbike-trick_2` | 0.618 | 0.658 | 0.638 | 0.725 | 0.727 | 0.726 |
| `soapbox_1` | 0.653 | 0.632 | 0.643 | 0.716 | 0.767 | 0.742 |
| `motocross-jump_2` | 0.663 | 0.624 | 0.643 | 0.614 | 0.652 | 0.633 |
| `loading_3` | 0.620 | 0.674 | 0.647 | 0.668 | 0.725 | 0.697 |
| `pigs_2` | 0.582 | 0.743 | 0.662 | 0.659 | 0.803 | 0.731 |
| `bike-packing_2` | 0.679 | 0.659 | 0.669 | 0.765 | 0.778 | 0.772 |
| `horsejump-high_2` | 0.567 | 0.777 | 0.672 | 0.661 | 0.852 | 0.756 |
| `breakdance_1` | 0.676 | 0.678 | 0.677 | 0.684 | 0.693 | 0.689 |
| `gold-fish_1` | 0.717 | 0.646 | 0.681 | 0.741 | 0.730 | 0.736 |
| `scooter-black_2` | 0.683 | 0.680 | 0.681 | 0.793 | 0.762 | 0.778 |
| `judo_2` | 0.700 | 0.713 | 0.706 | 0.765 | 0.780 | 0.772 |
| `drift-chicane_1` | 0.695 | 0.770 | 0.732 | 0.558 | 0.602 | 0.580 |
| `camel_1` | 0.704 | 0.792 | 0.748 | 0.728 | 0.822 | 0.775 |
| `shooting_2` | 0.747 | 0.752 | 0.750 | 0.756 | 0.742 | 0.749 |
| `horsejump-high_1` | 0.702 | 0.798 | 0.750 | 0.770 | 0.901 | 0.836 |
| `judo_1` | 0.728 | 0.782 | 0.755 | 0.823 | 0.860 | 0.841 |
| `dogs-jump_3` | 0.718 | 0.841 | 0.779 | 0.823 | 0.899 | 0.861 |
| `pigs_1` | 0.809 | 0.771 | 0.790 | 0.843 | 0.827 | 0.835 |
| `shooting_3` | 0.684 | 0.903 | 0.794 | 0.749 | 0.926 | 0.838 |
| `lab-coat_4` | 0.845 | 0.748 | 0.796 | 0.892 | 0.805 | 0.849 |
| `dance-twirl_1` | 0.796 | 0.802 | 0.799 | 0.850 | 0.880 | 0.865 |
| `libby_1` | 0.720 | 0.900 | 0.810 | 0.817 | 0.965 | 0.891 |
| `lab-coat_5` | 0.815 | 0.806 | 0.810 | 0.889 | 0.883 | 0.886 |
| `gold-fish_3` | 0.789 | 0.845 | 0.817 | 0.831 | 0.876 | 0.853 |
| `india_1` | 0.843 | 0.806 | 0.825 | 0.882 | 0.861 | 0.871 |
| `lab-coat_3` | 0.866 | 0.791 | 0.829 | 0.907 | 0.859 | 0.883 |
| `car-roundabout_1` | 0.864 | 0.793 | 0.829 | 0.891 | 0.809 | 0.850 |
| `goat_1` | 0.835 | 0.835 | 0.835 | 0.835 | 0.818 | 0.827 |
| `paragliding-launch_1` | 0.793 | 0.885 | 0.839 | 0.799 | 0.879 | 0.839 |
| `gold-fish_5` | 0.864 | 0.819 | 0.841 | 0.884 | 0.888 | 0.886 |
| `loading_1` | 0.878 | 0.805 | 0.842 | 0.924 | 0.907 | 0.915 |
| `gold-fish_4` | 0.810 | 0.882 | 0.846 | 0.823 | 0.840 | 0.831 |
| `parkour_1` | 0.813 | 0.899 | 0.856 | 0.892 | 0.961 | 0.926 |
| `cows_1` | 0.874 | 0.865 | 0.869 | 0.926 | 0.950 | 0.938 |
| `pigs_3` | 0.901 | 0.868 | 0.885 | 0.941 | 0.931 | 0.936 |
| `blackswan_1` | 0.877 | 0.927 | 0.902 | 0.942 | 0.985 | 0.964 |
| `dog_1` | 0.892 | 0.927 | 0.909 | 0.908 | 0.930 | 0.919 |
| `car-shadow_1` | 0.898 | 0.937 | 0.917 | 0.897 | 0.874 | 0.885 |
