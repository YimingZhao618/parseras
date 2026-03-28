import os
import subprocess

from geometry_structure import River


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
        print(f"  Has Data Block: True")
        print(f"  Data Block Key: {data_block._key}")
        print(f"  Data Block Count: {data_block.value}")
        print(f"  Data Block Data Length: {len(data_block._data)}")
    else:
        print(f"  Has Data Block: False")

    print("\nGenerated lines:")
    generated_lines = river.generate()
    for line in generated_lines:
        print(f"  {line}")

    output_file = "tests/river.output.g01"
    with open(output_file, "w") as f:
        f.writelines(generated_lines)

    result = subprocess.run(
        ["diff", "-q", "tests/river.g01", output_file], capture_output=True, text=True
    )

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

    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(
        f"{'✓' if river_passed else '✗'} River test: {'PASSED' if river_passed else 'FAILED'}"
    )
    print("=" * 80)

    if river_passed:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
