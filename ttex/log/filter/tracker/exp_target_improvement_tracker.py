import math

from ttex.log.filter.event_keysplit_filter import LogEvent
from ttex.log.filter.tracker.improvement_tracker import ImprovementTracker
from ttex.log.filter.tracker.parser import Parser


class ExpTargetImprovementParser(Parser):
    def __init__(
        self,
        target_val: float,
        n_bins: int,
        is_min: bool = True,
        target_precision: float = 1e-11,
    ) -> None:
        super().__init__()
        self.target_val = target_val
        self.n_bins = n_bins
        self.is_min = is_min
        self.target_precision = target_precision

    @staticmethod
    def get_exp_bin(n_bins: int, val: float) -> float:
        """
        Get the exponential bin for a given value.
        There are n_bins between each power of 10.
        Args:
            n_bins (int): Number of bins between each power of 10.
            val (float): The value to bin.
        Returns:
            float: The binned value.
        """
        if val <= 0:
            raise ValueError("Value must be positive")
        if n_bins <= 0:
            raise ValueError("Number of bins must be positive")
        exponent = math.ceil(n_bins * math.log10(val))
        value = 10 ** (exponent / n_bins)
        return value

    def retrieve_val(self, obj, target_key) -> float | None:
        val = super().retrieve_val(obj, target_key)
        if val is not None:
            dist_to_target = ImprovementTracker.get_diff(
                val, self.target_val, self.is_min
            )
            # cap at target precision
            dist_to_target = max(dist_to_target, self.target_precision)
            binned_diff = self.get_exp_bin(self.n_bins, dist_to_target)
            return binned_diff
        return None


class ExpTargetImprovementTracker(ImprovementTracker):
    def __init__(
        self,
        target_key: str,
        target_val: float,
        n_bins: int,
        is_min: bool = True,
        target_precision: float = 1e-11,
        event_type: type[LogEvent] = LogEvent,
    ) -> None:
        parser = ExpTargetImprovementParser(
            target_val=target_val,
            n_bins=n_bins,
            is_min=is_min,
            target_precision=target_precision,
        )
        # Since we are tracking the distance to the target, we set target_val=0 and is_min=True
        super().__init__(
            target_key=target_key,
            target_val=0,
            is_min=True,
            parser=parser,
            event_type=event_type,
        )
