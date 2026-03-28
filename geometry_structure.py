from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union


class Value(ABC):
    @classmethod
    @abstractmethod
    def __init__(cls, value_str: str):
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    @abstractmethod
    def value(self) -> Any:
        pass


class StringValue(Value):
    def __init__(self, value_str: str):
        self._value = value_str.strip()

    def __str__(self) -> str:
        return self._value

    @property
    def value(self) -> str:
        return self._value


class IntValue(Value):
    def __init__(self, value_str: str):
        self._value = int(value_str.strip())

    def __str__(self) -> str:
        return str(self._value)

    @property
    def value(self) -> int:
        return self._value


class FloatValue(Value):
    def __init__(self, value_str: str):
        self._value = float(value_str.strip())

    def __str__(self) -> str:
        v = self._value
        return str(int(v) if v.is_integer() else v)

    @property
    def value(self) -> float:
        return self._value


class CommaSeparatedValue(Value):
    def __init__(self, value_str: str, element_type: Type[Value] = StringValue):
        parts = value_str.split(",")
        result = []
        for part in parts:
            part = part.strip()
            if part:
                result.append(element_type(part))
            else:
                result.append(None)
        self._value = tuple(result)
        self._element_type = element_type

    def __str__(self) -> str:
        return ",".join(str(v) if v is not None else "" for v in self._value)

    @property
    def value(self) -> Tuple[Any, ...]:
        return self._value


class SpaceSeparatedValue(Value):
    def __init__(self, value_str: str, element_type: Type[Value] = StringValue):
        parts = value_str.split()
        self._value = tuple(element_type(part) for part in parts)
        self._element_type = element_type

    def __str__(self) -> str:
        return " ".join(str(v) for v in self._value)

    @property
    def value(self) -> Tuple[Any, ...]:
        return self._value


class NumericTupleValue(Value):
    def __init__(self, value_str: str):
        parts = value_str.split()
        result = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            try:
                result.append(int(part))
            except ValueError:
                result.append(float(part))
        self._value = tuple(result)

    def __str__(self) -> str:
        return " ".join(str(v) for v in self._value)

    @property
    def value(self) -> Tuple[Union[int, float], ...]:
        return self._value


class DataBlockValue(Value):
    @classmethod
    def parse_data_block(
        cls, header_line: str, lines: List[str], start_idx: int, value_width: int, values_per_line: int
    ) -> Tuple["DataBlockValue", int]:
        """
        解析数据块，返回 (DataBlockValue实例, 下一行索引)
        """
        count = int(header_line.split("=")[1].strip())
        data_lines = []
        idx = start_idx

        while idx < len(lines) and len(data_lines) < count:
            line = lines[idx].rstrip("\n").rstrip()

            if line and "=" not in line:
                data_lines.append(line)
            elif "=" in line:
                break

            idx += 1

        datablock = cls(header_line, data_lines, value_width, values_per_line)
        return datablock, idx

    def __init__(self, header_line: str, data_lines: List[str], value_width: int, values_per_line: int):
        self._value_width = value_width
        self._values_per_line = values_per_line

        key, count_str = header_line.split("=", 1)
        self._key = key.strip()
        self._count = int(count_str.strip())

        self._data = self._parse_data_lines(data_lines)

    def _parse_data_lines(self, lines: List[str]) -> Tuple[FloatValue, ...]:
        result = []
        for line in lines:
            pos = 0
            while pos < len(line):
                chunk = line[pos : pos + self._value_width]
                result.append(FloatValue(chunk.strip()))
                pos += self._value_width

        return tuple(result)

    def __str__(self) -> str:
        data_lines = []
        for i in range(0, len(self._data), self._values_per_line):
            chunk = self._data[i : i + self._values_per_line]
            line = "".join(str(v).rjust(self._value_width) for v in chunk)
            data_lines.append(line)

        return "\n".join([str(self._count)] + data_lines) + "\n"

    @property
    def value(self) -> int:
        return self._count

    def __len__(self) -> int:
        return len(self._data)


T = TypeVar("T", bound="GeometryStructure")


class GeometryStructure(ABC):
    _key_value_pairs: Dict[str, Value]
    _key_value_types: Dict[str, Any]

    def __init__(self, lines: List[str]):
        self._key_value_pairs = {}
        self._parse_lines(lines)

    def __getitem__(self, key: str) -> Value:
        value = self._key_value_pairs.get(key)
        if value is None:
            raise KeyError(f"Key '{key}' not found")
        return value

    def __setitem__(self, key: str, value: Value) -> None:
        self._key_value_pairs[key] = value

    def __delitem__(self, key: str) -> None:
        if key not in self._key_value_pairs:
            raise KeyError(f"Key '{key}' not found")
        del self._key_value_pairs[key]

    def __contains__(self, key: str) -> bool:
        return key in self._key_value_pairs

    def __len__(self) -> int:
        return len(self._key_value_pairs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GeometryStructure):
            return False
        return self._key_value_pairs == other._key_value_pairs

    def _parse_key_value_line(self, line: str) -> Tuple[str, str]:
        if "=" not in line:
            raise ValueError(f"Invalid key-value line: {line}")
        key, value = line.split("=", 1)
        return key.strip(), value.strip()

    def _format_key_value_line(self, key: str, value: Value) -> str:
        return f"{key}={str(value)}"

    def _parse_lines(self, lines: List[str]):
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            key, value_str = self._parse_key_value_line(line)

            if key in self._key_value_types:
                value_type_info = self._key_value_types[key]

                if isinstance(value_type_info, tuple) and len(value_type_info) == 2:
                    value_type, kwargs = value_type_info

                    if value_type == DataBlockValue:
                        datablock, next_idx = DataBlockValue.parse_data_block(line, lines, i + 1, **kwargs)
                        self[key] = datablock
                        i = next_idx
                    else:
                        value = value_type(value_str, **kwargs)
                        self[key] = value
                        i += 1
                elif isinstance(value_type_info, type) and issubclass(value_type_info, Value):
                    value = value_type_info(value_str)
                    self[key] = value
                    i += 1
            else:
                i += 1

        return self

    @abstractmethod
    def generate(self) -> List[str]:
        pass


class River(GeometryStructure):
    def __init__(self, lines: List[str]):
        self._key_value_types = {
            "River Reach": (CommaSeparatedValue, {"element_type": StringValue}),
            "Reach XY": (DataBlockValue, {"value_width": 16, "values_per_line": 4}),
            "Rch Text X Y": (CommaSeparatedValue, {"element_type": StringValue}),
            "Reverse River Text": IntValue,
        }
        super().__init__(lines)

    def generate(self) -> List[str]:
        result = []
        for key, value in self._key_value_pairs.items():
            formatted = self._format_key_value_line(key, value)
            if isinstance(value, DataBlockValue):
                result.append(formatted)
            else:
                result.append(formatted + "\n")
        return result
