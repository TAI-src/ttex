from ttex.log.coco.record import COCOLogHeader, COCOLogRecord
from ..test_coco_events import coco_start_params, eval_params
from ttex.log.coco import COCOState, COCOStart, COCOEval


def test_coco_log():
    state = COCOState()
    start_event = COCOStart(**coco_start_params)
    state.update(start_event)

    header = COCOLogHeader(state, file_type="dummy")
    expected_filepath = f"{start_event.algo}/data_{start_event.problem}/{start_event.exp_id}_{start_event.problem}_d{start_event.dim}.dummy"

    assert header.filepath == expected_filepath

    expected_header = "% f evaluations | g evaluations | best noise-free fitness - Fopt (1.000000000000e-01) + sum g_i+ | measured fitness | best measured fitness or single-digit g-values | x1 | x2..."
    assert str(header) == expected_header

    eval_event = COCOEval(**eval_params)
    state.update(eval_event)

    record = COCOLogRecord(state)
    expected_output = "1 0 +4.000000000e-01 +5.000000000e-01 +5.000000000e-01 +1.0000e+00 +2.0000e+00 +3.0000e+00"
    assert str(record) == expected_output
