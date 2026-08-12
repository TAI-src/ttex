from typing import Any


class Parser:

    def retrieve_val(self, obj: Any, target_key: str) -> Any | None:
        if obj is None:
            return None
        # split target_key by '.' to handle nested attributes
        current_key = target_key.split(".")[0]
        remaining_key = (
            ".".join(target_key.split(".")[1:]) if "." in target_key else None
        )
        val = None
        # check if current_key is an integer index
        try:
            index = int(current_key)
            try:
                val = obj[index]
            except (IndexError, TypeError):
                val = None
        except ValueError:
            # current_key is not an integer, treat it as a dictionary key
            if isinstance(obj, dict):
                val = obj.get(current_key, None)
            else:
                # check if current_key is an attribute of the object
                val = getattr(obj, current_key, None)
        return self.retrieve_val(val, remaining_key) if remaining_key else val
