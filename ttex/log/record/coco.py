from ttex.log.record import Record, Header
import os.path as osp
from uuid import uuid4
from typing import Optional


class COCORecord(Record):
    template = (
        "{f_evals} {g_evals} {best_dist_opt:+.9e} {mf:+.9e} {best_mf:+.9e} {x_str}"
    )

    def __init__(
        self,
        x: list[float],
        mf: float,
    ):
        """
        Initialize a COCO step with the given parameters.

        Args:
            x (list): List of decision variable values.
            mf (float): Measured fitness value.
        """
        self.f_evals: Optional[int] = None
        self.g_evals: Optional[int] = None
        self.best_dist_opt: Optional[float] = None
        self.mf = mf
        self.best_mf: Optional[float] = None
        self.x = x

    def __str__(self):
        """
        Format the COCO step as a string.
        Returns:
            str: Formatted COCO step string.
        """
        x_str = " ".join(f"{val:+.4e}" for val in self.x)
        if any(val is None for val in self.__dict__.values()):
            return ("{x_str} {mf}").format(x_str=x_str, mf=self.mf)
        return COCORecord.template.format(
            f_evals=self.f_evals,
            g_evals=self.g_evals,
            best_dist_opt=self.best_dist_opt,
            mf=self.mf,
            best_mf=self.best_mf,
            x_str=x_str,
        )


class COCOHeader(Header):
    template = "% f evaluations | g evaluations | best noise-free fitness - Fopt ({fopt:.12e}) + sum g_i+ | measured fitness | best measured fitness or single-digit g-values | x1 | x2..."

    def __init__(
        self, fopt: float, algo: str, problem: str, dim: str, inst: str, exp_id: str
    ):
        """
        Initialize a COCO header with the optimal function value.

        Args:
            fopt (float): Optimal function value.
        """
        self.fopt = fopt
        exp_id = exp_id or str(uuid4())
        self._filepath = osp.join(
            algo,
            f"data_{problem}",
            f"dim-{dim}",
            f"{exp_id}_{problem}_d{dim}_i{inst}.dat",
        )
        self._uuid = f"{algo}_{problem}_d{dim}_i{inst}_{exp_id}"

    def __str__(self):
        """
        Format the COCO header with the optimal function value.

        Returns:
            str: Formatted header string.
        """
        return COCOHeader.template.format(fopt=self.fopt)

    @property
    def filepath(self):
        """
        Get the file path for the COCO header.

        Returns:
            str: File path for the COCO header.
        """
        return self._filepath

    @property
    def uuid(self):
        """
        Get the UUID for the COCO header.

        Returns:
            str: UUID for the COCO header.
        """
        return self._uuid
