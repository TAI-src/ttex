class FunctionInfo:
    def __init__(self, func_id: int, name: str, long_name: str):
        self.func_id = func_id
        self.name = name
        self.long_name = long_name

    def to_str(self, short: bool = False) -> str:
        if short:
            return f"{self.func_id} {self.name}"
        else:
            return f"{self.func_id} {self.long_name}"


class SuiteInfo:
    pass
