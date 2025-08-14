from ttex.log.record import COCORecord, COCOHeader
import pytest

coco_record_vals = {
    "mf": 89.45098297,
    "x": [1.6666666666666667, 1.6666666666666667],
}

coco_header_vals = {
    "fopt": 79.48,
    "algo": "test_algo",
    "problem": "f3",
    "dim": "2",
    "inst": "1",
    "exp_id": "12345",
}


def test_coco_header_filepath():
    header = COCOHeader(**coco_header_vals)
    expected_filepath = (
        f"{coco_header_vals['algo']}/data_{coco_header_vals['problem']}/"
        f"dim-{coco_header_vals['dim']}/{coco_header_vals['exp_id']}_"
        f"{coco_header_vals['problem']}_d{coco_header_vals['dim']}_"
        f"i{coco_header_vals['inst']}.dat"
    )
    assert header.filepath == expected_filepath


def test_format_coco_header():
    expected_header = "% f evaluations | g evaluations | best noise-free fitness - Fopt (7.948000000000e+01) + sum g_i+ | measured fitness | best measured fitness or single-digit g-values | x1 | x2..."
    header = COCOHeader(**coco_header_vals)
    assert str(header) == expected_header


def test_format_coco_record():
    record = COCORecord(**coco_record_vals)
    expected_output = "+1.6667e+00 +1.6667e+00 +8.945098297e+01"

    record.f_evals = 1
    record.g_evals = 0
    record.best_dist_opt = 9.970982969
    record.best_mf = 89.45098297

    expected_output = (
        "1 0 +9.970982969e+00 +8.945098297e+01 +8.945098297e+01 +1.6667e+00 +1.6667e+00"
    )
    assert str(record) == expected_output
