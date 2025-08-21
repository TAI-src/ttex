from ttex.log.record import COCOInfoHeader, COCOInfoRecord

coco_info_header_vals = {
    "funcId": 3,
    "algId": "test_algo",
    "dim": 2,
    "suite": "bbob",
}
coco_info_record_vals = {
    "file_path": "data_f1/bbobexp_f1_DIM10_i1.dat",
    "inst": 2,
    "f_evals": 100,
    "prec": 0.00014,
}


def test_coco_info_header_vals():
    header = COCOInfoHeader(**coco_info_header_vals)
    ## filepath
    expected_filepath = (
        f"{coco_info_header_vals['algId']}/f{coco_info_header_vals['funcId']}.info"
    )
    assert header.filepath == expected_filepath

    ## uuid
    expected_uuid = f"{coco_info_header_vals['algId']}_{coco_info_header_vals['funcId']}_{coco_info_header_vals['dim']}"
    assert header.uuid == expected_uuid


def test_format_coco_info_header():
    expected_header = (
        "suite = 'bbob', funcId = 3, DIM = 2, Precision = 1.000e-08, "
        "algId = 'test_algo', coco_version = '', logger = 'bbob', "
        "data_format = 'bbob-new2'\n% test_algo"
    )
    header = COCOInfoHeader(**coco_info_header_vals)
    assert str(header) == expected_header


def test_format_coco_info_record():
    record = COCOInfoRecord(**coco_info_record_vals)
    expected_output = "data_f1/bbobexp_f1_DIM10_i1.dat, 2:100|1.4e-04"
    assert str(record) == expected_output
