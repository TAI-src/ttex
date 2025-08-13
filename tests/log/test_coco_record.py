from ttex.log.record import COCORecord, COCOHeader

vals = {
    "f_evals": 1,
    "g_evals": 0,
    "best_dist_opt": 9.970982969,
    "mf": 89.45098297,
    "best_mf": 89.45098297,
    "x": [1.6666666666666667, 1.6666666666666667],
}

def test_format_coco_header():
    fopt = 79.48
    expected_header = "% f evaluations | g evaluations | best noise-free fitness - Fopt (7.948000000000e+01) + sum g_i+ | measured fitness | best measured fitness or single-digit g-values | x1 | x2..."
    header = COCOHeader(fopt=fopt)
    assert str(header) == expected_header

def test_format_coco_record():
    record = COCORecord(**vals)
    expected_output = "1 0 +9.970982969e+00 +8.945098297e+01 +8.945098297e+01 +1.6667e+00 +1.6667e+00"
    assert str(record) == expected_output

