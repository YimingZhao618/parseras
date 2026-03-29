import subprocess
from typing import List

from geometry_structure import River, GeometryStructure, DataBlockValue


class Block(GeometryStructure):
    def __init__(self, lines: List[str], key: str, value_width: int, values_per_line: int, items_per_value: int):
        self._key_value_types = {
            key: (
                DataBlockValue,
                {"value_width": value_width, "values_per_line": values_per_line, "items_per_value": items_per_value},
            ),
        }
        super().__init__(lines)

    def generate(self) -> List[str]:
        result = []
        for key, value in self._key_value_pairs.items():
            result.append(self._format_key_value_line(key, value))
        return result


BLOCK_TESTS = [
    {
        "test_name": "ReachXY",
        "file_path": "tests/common_blocks/block1.g01",
        "key": "Reach XY",
        "value_width": 16,
        "values_per_line": 4,
        "items_per_value": 2,
        "show_all_lines": True,
    },
    {
        "test_name": "StaElev",
        "file_path": "tests/common_blocks/block2.g01",
        "key": "#Sta/Elev",
        "value_width": 8,
        "values_per_line": 10,
        "items_per_value": 2,
        "show_all_lines": False,
    },
    {
        "test_name": "XSGisCutLine",
        "file_path": "tests/common_blocks/block3.g01",
        "key": "XS GIS Cut Line",
        "value_width": 16,
        "values_per_line": 4,
        "items_per_value": 2,
        "show_all_lines": True,
    },
    {
        "test_name": "StorageAreaSurfaceLine",
        "file_path": "tests/common_blocks/block4.g01",
        "key": "Storage Area Surface Line",
        "value_width": 16,
        "values_per_line": 2,
        "items_per_value": 2,
        "show_all_lines": True,
    },
    {
        "test_name": "StorageArea2DPoints",
        "file_path": "tests/common_blocks/block5.g01",
        "key": "Storage Area 2D Points",
        "value_width": 16,
        "values_per_line": 4,
        "items_per_value": 2,
        "show_all_lines": False,
    },
]


def test_block(test_config):
    print("\n" + "=" * 80)
    print(f"Testing {test_config['test_name']} class")
    print("=" * 80)

    with open(test_config["file_path"], "r") as f:
        lines = f.readlines()

    block = Block(
        lines,
        test_config["key"],
        test_config["value_width"],
        test_config["values_per_line"],
        test_config["items_per_value"],
    )

    print(f"Parsed {test_config['test_name']}:")
    data_block = block[test_config["key"]]
    if data_block:
        print(f"  {test_config['key']} Count: {data_block.value}")
        print(f"  Total data points: {len(data_block)}")
    else:
        print("  Has Data Block: False")

    print("\nGenerated lines:")
    generated_lines = block.generate()
    if test_config["show_all_lines"]:
        for line in generated_lines:
            print(f"  {line.rstrip()}")
    else:
        for i, line in enumerate(generated_lines[:5]):
            print(f"  {line.rstrip()}")
        print(f"  ... ({len(generated_lines)} total lines)")

    output_file = test_config["file_path"].replace(".g01", ".output.g01")
    with open(output_file, "w") as f:
        f.writelines(generated_lines)

    result = subprocess.run(["diff", "-q", test_config["file_path"], output_file], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"\n✓ Generated file matches original: {output_file}")
    else:
        print(f"\n✗ Generated file differs from original: {output_file}")
        print(result.stdout)

    print(f"\n✓ {test_config['test_name']} test completed!")
    return result.returncode == 0


def test_river():
    print("\n" + "=" * 80)
    print("Testing River class")
    print("=" * 80)

    with open("tests/river.g01", "r") as f:
        lines = f.readlines()

    river = River(lines)

    print("Parsed River:")
    print(f"  River Reach: {river['River Reach'].value}")
    print(f"  Rch Text X Y: {river['Rch Text X Y'].value}")
    print(f"  Reverse River Text: {river['Reverse River Text'].value}")

    data_block = river["Reach XY"]
    if data_block:
        print("  Has Data Block: True")
        print(f"  Data Block Count: {data_block.value}")
    else:
        print("  Has Data Block: False")

    print("\nGenerated lines:")
    generated_lines = river.generate()
    for line in generated_lines:
        print(f"  {line}")

    output_file = "tests/river.output.g01"
    with open(output_file, "w") as f:
        f.writelines(generated_lines)

    result = subprocess.run(["diff", "-q", "tests/river.g01", output_file], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"\n✓ Generated file matches original: {output_file}")
    else:
        print(f"\n✗ Generated file differs from original: {output_file}")
        print(result.stdout)

    print("\n✓ River test completed!")
    return result.returncode == 0


def main():
    print("=" * 80)
    print("Running all tests for HEC-RAS 2D Geometry Parser")
    print("=" * 80)

    river_passed = test_river()

    block_results = {}
    for test_config in BLOCK_TESTS:
        block_results[test_config["test_name"]] = test_block(test_config)

    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"{'✓' if river_passed else '✗'} River test: {'PASSED' if river_passed else 'FAILED'}")
    for test_name, passed in block_results.items():
        print(f"{'✓' if passed else '✗'} {test_name} test: {'PASSED' if passed else 'FAILED'}")
    print("=" * 80)

    all_passed = river_passed and all(block_results.values())

    if all_passed:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
