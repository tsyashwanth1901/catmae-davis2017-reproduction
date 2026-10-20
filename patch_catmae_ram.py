import sys, re

root = sys.argv[1]  # path to .../downstream/davis2017-seg/code
tm = f"{root}/test_mae.py"
tu = f"{root}/utils/test_utils.py"

# ---------- test_mae.py ----------
s = open(tm).read()
if "feats_flat" in s:
    print("test_mae.py already patched"); 
else:
    old1 = "            keys, query = feats[:, :, key_indices], feats[:, :, n_context:]\n"
    new1 = "            feats_flat = feats.flatten(-2)   # [1, C, N, H*W]  (no 21x duplicated key bank)\n"
    assert old1 in s, "pattern 1 not found"
    s = s.replace(old1, new1)

    old2 = "            keys, query = keys.flatten(-2), query.flatten(-2)\n"
    new2 = "            query = feats_flat[:, :, n_context:]\n"
    assert old2 in s, "pattern 2 not found"
    s = s.replace(old2, new2)

    old3 = "Ws, Is = test_utils.mem_efficient_batched_affinity(query, keys, D, \n"
    new3 = "Ws, Is = test_utils.mem_efficient_batched_affinity(query, feats_flat, key_indices, D, \n"
    assert old3 in s, "pattern 3 not found"
    s = s.replace(old3, new3)

    old4 = "            torch.cuda.empty_cache()\n            print('******* Vid %s TOOK %s *******' % (vid_idx, time.time() - t_vid))\n"
    new4 = ("            del feats, feats_flat, query, Ws, Is, maps, imgs\n"
            "            gc.collect()\n"
            "            torch.cuda.empty_cache()\n"
            "            print('******* Vid %s TOOK %s *******' % (vid_idx, time.time() - t_vid))\n")
    assert old4 in s, "pattern 4 not found"
    s = s.replace(old4, new4)

    s = s.replace("import os\nimport time\n", "import os\nimport gc\nimport time\n", 1)
    open(tm, "w").write(s)
    print("patched test_mae.py")

# ---------- utils/test_utils.py ----------
u = open(tu).read()
if "key_indices" in u.split("def mem_efficient_batched_affinity")[1].split("def batched_affinity")[0]:
    print("test_utils.py already patched")
else:
    old = ("def mem_efficient_batched_affinity(query, keys, mask, temperature, topk, long_mem, device):\n")
    new = ("def mem_efficient_batched_affinity(query, feats_flat, key_indices, mask, temperature, topk, long_mem, device):\n")
    assert old in u, "pattern A not found"
    u = u.replace(old, new)

    old = "    for b in range(0, keys.shape[2], bsize):\n        _k, _q = keys[:, :, b:b+bsize].to(device), query[:, :, b:b+bsize].to(device)\n        w_s, i_s = [], []\n\n        for pb in range(0, _k.shape[-1], pbsize):"
    new = "    for b in range(0, key_indices.shape[0], bsize):\n        _k = feats_flat[:, :, key_indices[b:b+bsize]].to(device)   # gathered on the fly\n        _q = query[:, :, b:b+bsize].to(device)\n        w_s, i_s = [], []\n\n        for pb in range(0, _k.shape[-1], pbsize):"
    assert old in u, "pattern B not found"
    u = u.replace(old, new, 1)
    open(tu, "w").write(u)
    print("patched test_utils.py")
