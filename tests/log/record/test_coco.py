from ttex.log.record import COCOLog, COCOEval, COCOEnd, COCOStart


def test_inits():
    """
    Test the initialization of COCO evaluation, end, and start records.
    This test checks if the records can be created with the correct parameters.
    """
    # Test COCOEval
    eval_record = COCOEval(x=[1.0, 2.0], mf=3.0)
    assert eval_record.x == [1.0, 2.0]
    assert eval_record.mf == 3.0

    # Test COCOEnd
    end_record = COCOEnd()
    assert isinstance(end_record, COCOLog)

    # Test COCOStart
    start_record = COCOStart(
        fopt=1.0,
        algo="test_algo",
        problem=1,
        dim=2,
        inst=3,
        exp_id="exp_123",
        suite="bbob",
    )
    assert start_record.fopt == 1.0
    assert start_record.algo == "test_algo"
    assert start_record.problem == 1
    assert start_record.dim == 2
    assert start_record.inst == 3
    assert start_record.exp_id == "exp_123"
    assert start_record.suite == "bbob"
