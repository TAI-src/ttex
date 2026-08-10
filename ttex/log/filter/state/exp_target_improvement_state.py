from ttex.log.filter.state.improvement_state import ImprovementState
import math
from ttex.log.filter.event.environment_events import EnvironmentStep


class ExpTargetImprovementState(ImprovementState):
    def __init__(
        self,
        target_key: str,
        target_val: float,
        n_bins: int,
        is_min: bool = True,
        target_precision: float = 1e-11,
    ) -> None:
        super().__init__(target_key, 0, is_min=True)
        assert target_precision > 0, "Target precision must be positive"
        self.target_precision = target_precision
        self.true_target = target_val
        self.n_bins = n_bins

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

    @staticmethod
    def convert_to_target(
        value: float,
        target_val: float,
        n_bins: int,
        target_precision: float = 1e-11,
        is_min: bool = True,
    ) -> float:
        diff = ImprovementState.get_diff(value, target_val, is_min=is_min)
        # cap at target precision
        diff = max(diff, target_precision)
        binned_diff = ExpTargetImprovementState.get_exp_bin(n_bins, diff)
        return binned_diff

    def retrieve_val(self, event: EnvironmentStep, target_key: str) -> float | None:
        val = super().retrieve_val(event, target_key)
        if val is not None:
            return self.convert_to_target(
                val, self.target_val, self.n_bins, self.target_precision, self.is_min
            )
        return None
