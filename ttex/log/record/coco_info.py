from ttextual import Record, Header, RecordType
import os.path as osp
from abc import ABC
from typing import Type


class COCOInfo(RecordType):
    pass


class COCOInfoHeader(Header, ABC):
    template = "suite = '{suite}', funcId = {funcId}, DIM = {dim}, Precision = {prec:.3e}, algId = '{algId}', coco_version = '{coco_version}', logger = '{logger}', data_format = '{data_format}'\n% {algId}"

    def __init__(self, funcId: int, algId: str, dim: int, suite: str):
        """
        Initialize a COCOInfoHeader with the given parameters.

        Args:
            funcId (int): Function ID.
            algId (str): Algorithm ID.
            dim (int): Dimension of the problem.
            suite (str): Suite name, default is "bbob".
        """
        self.funcId = funcId
        self.algId = algId
        self.dim = dim
        self.suite = suite
        self.prec = 1e-8
        self.coco_version = ""
        self.logger = "bbob"
        self.data_format = "bbob-new2"
        self._filepath = osp.join(f"{self.algId}", f"f{funcId}.info")
        self._uuid = f"{algId}_{funcId}_{dim}"

    @property
    def type(self) -> Type[COCOInfo]:
        """
        Get the type of the COCOInfoHeader.

        Returns:
            COCOInfo: The type of the COCOInfoHeader.
        """
        return COCOInfo

    @property
    def filepath(self) -> str:
        """
        Get the file path for the COCOInfoHeader.

        Returns:
            str: File path for the COCOInfoHeader.
        """
        return self._filepath

    @property
    def uuid(self) -> str:
        """
        Get the UUID for the COCOInfoHeader.

        Returns:
            str: UUID for the COCOInfoHeader.
        """
        return self._uuid

    def __str__(self) -> str:
        """
        Format the COCOInfoHeader as a string.

        Returns:
            str: Formatted COCOInfoHeader string.
        """
        return COCOInfoHeader.template.format(
            suite=self.suite,
            funcId=self.funcId,
            dim=self.dim,
            prec=self.prec,
            algId=self.algId,
            coco_version=self.coco_version,
            logger=self.logger,
            data_format=self.data_format,
        )


class COCOInfoRecord(Record):
    template = "{file_path}, {inst}:{f_evals}|{prec:.1e}"

    def __init__(self, file_path: str, inst: int, f_evals: int, prec: float):
        """
        Initialize a COCOInfoRecord with the given parameters.

        Args:
            file_path (str): Path to the COCO info file.
            inst (int): Instance number.
            f_evals (int): Number of function evaluations.
            prec (float): Precision value.
        """
        self.file_path = file_path
        self.inst = inst
        self.f_evals = f_evals
        self.prec = prec

    def __str__(self) -> str:
        """
        Format the COCOInfoRecord as a string.
        Returns:
            str: Formatted COCOInfoRecord string.
        """
        return COCOInfoRecord.template.format(
            file_path=self.file_path,
            inst=self.inst,
            f_evals=self.f_evals,
            prec=self.prec,
        )

    @property
    def type(self) -> Type[COCOInfo]:
        """
        Get the type of the COCOInfoRecord.

        Returns:
            COCOInfo: The type of the COCOInfoRecord.
        """
        return COCOInfo
