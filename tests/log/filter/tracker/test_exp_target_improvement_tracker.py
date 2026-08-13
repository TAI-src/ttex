from ttex.log.filter.tracker.exp_target_improvement_tracker import (
    ExpTargetImprovementTracker,
    ExpTargetImprovementParser,
)
import math


def test_get_exp_bin():
    n_bins = 10
    # 10 bins between 1 and 10 means each bin is a factor of 10^(1/10) ~ 1.2589
    # Test a few values to ensure they fall into the correct bins
    for exp in range(3, 50):
        value = 10 ** (exp / n_bins)
        assert math.isclose(
            ExpTargetImprovementParser.get_exp_bin(n_bins, value), value
        ), f"Failed at value: {value}"

        next_value = 10 ** ((exp + 1) / n_bins)
        mid_value = (value + next_value) / 2
        assert math.isclose(
            ExpTargetImprovementParser.get_exp_bin(n_bins, mid_value), next_value
        ), f"Failed at mid value: {mid_value}"


def test_retrieve_val():
    parser = ExpTargetImprovementParser(target_val=0.1, n_bins=10, is_min=True)
    obj = {"fitness": 0.2}
    target_key = "fitness"
    binned_diff = parser.retrieve_val(obj, target_key)
    expected_diff = 0.1
    expected_binned_diff = ExpTargetImprovementParser.get_exp_bin(10, expected_diff)
    assert math.isclose(
        binned_diff, expected_binned_diff
    ), f"Expected {expected_binned_diff}, got {binned_diff}"


def test_retrieve_val_none():
    parser = ExpTargetImprovementParser(target_val=0.1, n_bins=10, is_min=True)
    obj = {"fitness": None}
    target_key = "fitness"
    binned_diff = parser.retrieve_val(obj, target_key)
    assert binned_diff is None, f"Expected None, got {binned_diff}"


def test_retrieve_val_precision():
    parser = ExpTargetImprovementParser(
        target_val=0.1, n_bins=10, is_min=True, target_precision=1e-5
    )
    obj = {"fitness": 0.100001}
    target_key = "fitness"
    binned_diff = parser.retrieve_val(obj, target_key)
    expected_diff = 1e-5
    assert (
        abs(obj["fitness"] - parser.target_val) < parser.target_precision
    ), "Difference is less than target precision"
    expected_binned_diff = ExpTargetImprovementParser.get_exp_bin(10, expected_diff)
    assert math.isclose(
        binned_diff, expected_binned_diff
    ), f"Expected {expected_binned_diff}, got {binned_diff}"


def test_exp_target_improvement_tracker_init():
    tracker = ExpTargetImprovementTracker(
        target_key="fitness", target_val=0.1, n_bins=10, is_min=True
    )
    assert tracker.target_key == "fitness"
    assert tracker.parser.target_val == 0.1
    assert tracker.parser.n_bins == 10
    assert tracker.parser.is_min is True


def test_exp_target_improvement_tracker_process_event():
    tracker = ExpTargetImprovementTracker(
        target_key="fitness", target_val=0.1, n_bins=10, is_min=True, event_type=dict
    )  # Using dict for simplicity in this test
    event = {"fitness": 0.22}
    tracker.process_event(event)
    assert tracker.event_count == 1
    assert math.isclose(
        tracker.last_observed, ExpTargetImprovementParser.get_exp_bin(10, 0.12)
    )
    assert math.isclose(
        tracker.best_observed, ExpTargetImprovementParser.get_exp_bin(10, 0.12)
    )
    assert tracker.last_update == 1

    # Process a better value on same step
    event = {"fitness": 0.21}
    tracker.process_event(event)
    assert tracker.event_count == 2
    assert math.isclose(
        tracker.last_observed, ExpTargetImprovementParser.get_exp_bin(10, 0.12)
    )
    assert math.isclose(
        tracker.best_observed, ExpTargetImprovementParser.get_exp_bin(10, 0.12)
    )  # best should remain the same since it's the same step
    assert tracker.last_update == 1  # last_update should remain 1

    # Process a better value on a new step
    event = {"fitness": 0.19}
    tracker.process_event(event)
    assert tracker.event_count == 3
    assert math.isclose(
        tracker.last_observed, ExpTargetImprovementParser.get_exp_bin(10, 0.09)
    )
    assert math.isclose(
        tracker.best_observed, ExpTargetImprovementParser.get_exp_bin(10, 0.09)
    )  # best should update to new step
    assert tracker.last_update == 3  # last_update should update to 3

    # Process a worse value
    event = {"fitness": 0.25}
    tracker.process_event(event)
    assert tracker.event_count == 4
    assert math.isclose(
        tracker.last_observed, ExpTargetImprovementParser.get_exp_bin(10, 0.15)
    )
    assert math.isclose(
        tracker.best_observed, ExpTargetImprovementParser.get_exp_bin(10, 0.09)
    )  # best should remain the same since it's worse
