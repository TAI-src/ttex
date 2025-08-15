from ttex.log.record import Record, Header, RecordType
import os.path as osp
from uuid import uuid4
from typing import Type


class COCOLog(RecordType):
    pass


class COCOLogRecord(Record):
    template = (
        "{f_evals} {g_evals} {best_dist_opt:+.9e} {mf:+.9e} {best_mf:+.9e} {x_str}"
    )

    def __init__(
        self,
        x: list[float],
        mf: float,
        f_evals: int,
        g_evals: int,
        best_dist_opt: float,
        best_mf: float,
    ):
        """
        Initialize a COCO step with the given parameters.

        Args:
            x (list): List of decision variable values.
            mf (float): Measured fitness value.
        """
        self.mf = mf
        self.x = x
        self.f_evals = f_evals
        self.g_evals = g_evals
        self.best_dist_opt = best_dist_opt
        self.best_mf = best_mf

    def __str__(self):
        """
        Format the COCO step as a string.
        Returns:
            str: Formatted COCO step string.
        """
        x_str = " ".join(f"{val:+.4e}" for val in self.x)
        return COCOLogRecord.template.format(
            f_evals=self.f_evals,
            g_evals=self.g_evals,
            best_dist_opt=self.best_dist_opt,
            mf=self.mf,
            best_mf=self.best_mf,
            x_str=x_str,
        )

    @property
    def type(self) -> Type[COCOLog]:
        """
        Get the type of the COCOLogRecord.

        Returns:
            Type[COCOLog]: The type of the COCOLogRecord.
        """
        return COCOLog


class COCOLogHeader(Header):
    template = "% f evaluations | g evaluations | best noise-free fitness - Fopt ({fopt:.12e}) + sum g_i+ | measured fitness | best measured fitness or single-digit g-values | x1 | x2..."

    def __init__(
        self, fopt: float, algo: str, problem: str, dim: int, inst: int, exp_id: str
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
            f"{exp_id}_{problem}_d{dim}.dat",
        )
        self._uuid = f"{algo}_{problem}_d{dim}_i{inst}_{exp_id}"

    def __str__(self):
        """
        Format the COCO header with the optimal function value.

        Returns:
            str: Formatted header string.
        """
        return COCOLogHeader.template.format(fopt=self.fopt)

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

    @property
    def type(self) -> Type[COCOLog]:
        """
        Get the type of the COCOLogHeader.

        Returns:
            Type[COCOLog]: The type of the COCOLogHeader.
        """
        return COCOLog
