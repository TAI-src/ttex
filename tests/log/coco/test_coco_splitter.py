from ttex.log.coco import COCOKeySplitter, COCOState, COCOStart, COCOEval, COCOEnd
import pytest


def get_started_state(splitter: COCOKeySplitter):
    state = COCOState()
    start_event = COCOStart(
        fopt=0.1,
        algo="test_algo",
        problem=1,
        dim=10,
        inst=1,
        suite="test_suite",
        exp_id="test_exp_id",
    )
    state.update(start_event)  # Update state with start event
    result = splitter.process(state, start_event)
    return state, result


def test_process_coco_start():
    state, result = get_started_state(COCOKeySplitter())

    assert "info" in result
    assert "log_dat" in result
    assert "log_tdat" in result
    assert state.dat_filepath is not None


def test_trigger_target_resetting():
    splitter = COCOKeySplitter(trigger_nth=1, trigger_targets=[0.5, 0.6])
    state, _ = get_started_state(splitter)
    assert splitter.trigger_targets == [0.6, 0.5]
    assert splitter.start_trigger_targets == [0.5, 0.6]
    splitter.trigger_targets.pop(0)  # Simulate popping a target
    assert splitter.trigger_targets == [0.5]
    state, _ = get_started_state(splitter)
    assert splitter.trigger_targets == [0.6, 0.5]  # Should be reset


def test_no_targets():
    splitter = COCOKeySplitter(trigger_nth=1)
    state, _ = get_started_state(splitter)
    assert splitter.trigger_targets == []


def test_reset_trigger_bbob():
    splitter = COCOKeySplitter(trigger_nth=1)
    splitter._reset_triggers("bbob")
    assert len(splitter.trigger_targets) > 0


def test_process_coco_eval():
    splitter = COCOKeySplitter(trigger_nth=1, trigger_targets=[0.5])
    state, _ = get_started_state(splitter)

    eval_event = COCOEval(x=[1.0, 2.0, 3.0], mf=0.5)
    state.update(eval_event)
    result = splitter.process(state, eval_event)

    assert "log_dat" in result
    assert "log_tdat" in result
    assert state.f_evals == 1
    assert state.best_mf == 0.5
    assert state.last_dat_emit == state.f_evals


def test_process_coco_end_assert():
    splitter = COCOKeySplitter(trigger_nth=20)
    state, _ = get_started_state(splitter)

    end_event = COCOEnd()
    state.update(end_event)
    with pytest.raises(AssertionError):
        splitter.process(state, end_event)


@pytest.mark.parametrize("add_last", [True, False])
def test_process_coco_end_default(add_last):
    splitter = COCOKeySplitter(trigger_nth=20)
    state, _ = get_started_state(splitter)
    eval_event = COCOEval(x=[1.0, 2.0, 3.0], mf=0.5)
    state.update(eval_event)  # Add an eval to avoid assert
    splitter.process(state, eval_event)
    if add_last:
        eval_event = COCOEval(x=[1.0, 2.0, 3.0], mf=0.3)
        state.update(
            eval_event
        )  # Add another eval so we have one that is not already emitted
        splitter.process(state, eval_event)
    end_event = COCOEnd()
    state.update(end_event)
    result = splitter.process(state, end_event)
    assert "info" in result
    assert (
        state._needs_start is True
    )  # After COCOEnd, state should require a new start event
    assert ("log_dat" in result) == add_last
    assert "log_tdat" not in result


def test_process_coco_eval_with_trigger_nth():
    splitter = COCOKeySplitter(trigger_nth=3, trigger_targets=[0.5, 0.3])
    state, _ = get_started_state(splitter)
    eval_event = COCOEval(x=[1.0, 2.0, 3.0], mf=0.5)
    state.update(eval_event)  # First eval, always triggers log_dat
    result = splitter.process(state, eval_event)
    assert "log_dat" in result
    assert "log_tdat" in result
    eval_event = COCOEval(x=[1.0, 2.0, 3.0], mf=0.3)
    state.update(eval_event)  # Second eval, should not trigger log_dat
    result = splitter.process(state, eval_event)
    assert "log_dat" not in result
    assert "log_tdat" in result
    assert state.f_evals == 2
    assert state.last_dat_emit == 1


def test_process_coco_eval_with_trigger_targets():
    splitter = COCOKeySplitter(trigger_nth=1, trigger_targets=[0.5, 0.6])
    state, _ = get_started_state(splitter)
    eval_event = COCOEval(x=[1.0, 2.0, 3.0], mf=0.7)
    state.update(eval_event)  # Worse than targets, should not trigger log_tdat
    result = splitter.process(state, eval_event)
    assert "log_dat" in result
    assert "log_tdat" in result
    assert splitter.trigger_targets == [0.5]  # 0.6 should be popped
