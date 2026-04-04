import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List, Dict, Any

# 使用相对导入
import json

from parseras import (
    River,
    BreakLine,
    CrossSection,
    Foot,
    Head,
    LateralWeir,
    StorageArea,
    RASStructure,
    DataBlockValue,
    GeometryFile,
    RiverModel,
)


class Block(RASStructure):
    def __init__(self, lines: List[str], key: str, value_width: int, values_per_line: int, items_per_value: int):
        self._key_value_types = {
            key: (
                DataBlockValue,
                {"value_width": value_width, "values_per_line": values_per_line, "items_per_value": items_per_value},
            ),
        }
        super().__init__(lines)


GEOMETRY_TESTS = [
    {
        "test_name": "River",
        "file_path": "tests/data/river.g01",
        "class": River,
    },
    {
        "test_name": "BreakLine",
        "file_path": "tests/data/breakline.g01",
        "class": BreakLine,
    },
    {
        "test_name": "CrossSection",
        "file_path": "tests/data/cross_secion.g01",
        "class": CrossSection,
    },
    {
        "test_name": "Foot",
        "file_path": "tests/data/foot.g01",
        "class": Foot,
    },
    {
        "test_name": "Head",
        "file_path": "tests/data/head.g01",
        "class": Head,
    },
    {
        "test_name": "LateralWeir",
        "file_path": "tests/data/lateral_weir.g01",
        "class": LateralWeir,
    },
    {
        "test_name": "StorageArea",
        "file_path": "tests/data/storage_area.g01",
        "class": StorageArea,
    },
]


BLOCK_TESTS = [
    {
        "test_name": "ReachXY",
        "file_path": "tests/data/common_blocks/block1.g01",
        "key": "Reach XY",
        "value_width": 16,
        "values_per_line": 4,
        "items_per_value": 2,
    },
    {
        "test_name": "StaElev",
        "file_path": "tests/data/common_blocks/block2.g01",
        "key": "#Sta/Elev",
        "value_width": 8,
        "values_per_line": 10,
        "items_per_value": 2,
    },
    {
        "test_name": "XSGisCutLine",
        "file_path": "tests/data/common_blocks/block3.g01",
        "key": "XS GIS Cut Line",
        "value_width": 16,
        "values_per_line": 4,
        "items_per_value": 2,
    },
    {
        "test_name": "StorageAreaSurfaceLine",
        "file_path": "tests/data/common_blocks/block4.g01",
        "key": "Storage Area Surface Line",
        "value_width": 16,
        "values_per_line": 2,
        "items_per_value": 2,
    },
    {
        "test_name": "StorageArea2DPoints",
        "file_path": "tests/data/common_blocks/block5.g01",
        "key": "Storage Area 2D Points",
        "value_width": 16,
        "values_per_line": 4,
        "items_per_value": 2,
    },
]


FULL_FILE_TESTS = [
    {
        "test_name": "all.g01",
        "file_path": "tests/data/all.g01",
    },
    {
        "test_name": "leak.g01",
        "file_path": "tests/data/leak.g01",
    },
    {
        "test_name": "Muncie.g01",
        "file_path": "tests/data/Muncie.g01",
    },
]


def test_geometry(test_config: Dict[str, Any]) -> bool:
    with open(test_config["file_path"], "r") as f:
        original_lines = f.readlines()

    geometry_class = test_config["class"]
    geometry = geometry_class(original_lines)

    generated_lines = geometry.generate()
    output_file = test_config["file_path"].replace(".g01", ".output.g01")
    with open(output_file, "w") as f:
        f.writelines(generated_lines)

    generated_text = "".join(generated_lines)
    original_text = "".join(original_lines)
    return original_text == generated_text


def test_block(test_config: Dict[str, Any]) -> bool:
    with open(test_config["file_path"], "r") as f:
        original_lines = f.readlines()

    block = Block(
        original_lines,
        test_config["key"],
        test_config["value_width"],
        test_config["values_per_line"],
        test_config["items_per_value"],
    )

    generated_lines = block.generate()
    output_file = test_config["file_path"].replace(".g01", ".output.g01")
    with open(output_file, "w") as f:
        f.writelines(generated_lines)

    generated_text = "".join(generated_lines)
    original_text = "".join(original_lines)
    return original_text == generated_text


def main():
    geometry_results = {}
    for test_config in GEOMETRY_TESTS:
        geometry_results[test_config["test_name"]] = test_geometry(test_config)

    block_results = {}
    for test_config in BLOCK_TESTS:
        block_results[test_config["test_name"]] = test_block(test_config)

    full_file_results = {}
    for test_config in FULL_FILE_TESTS:
        full_file_results[test_config["test_name"]] = test_full_file(test_config["file_path"])

    # 运行河流修改测试
    river_modification_result = test_river_modification()

    print("=" * 80)
    print("Test Summary")
    print("=" * 80)

    all_passed = True

    for test_name, passed in geometry_results.items():
        print(f"{'✅' if passed else '❌'} {test_name} test: {'PASSED' if passed else 'FAILED'}")
        all_passed = all_passed and passed

    print("=" * 60)

    for test_name, passed in block_results.items():
        print(f"{'✅' if passed else '❌'} {test_name} test: {'PASSED' if passed else 'FAILED'}")
        all_passed = all_passed and passed

    print("=" * 60)

    for test_name, passed in full_file_results.items():
        print(f"{'✅' if passed else '❌'} {test_name} test: {'PASSED' if passed else 'FAILED'}")
        all_passed = all_passed and passed

    print("=" * 60)

    print(f"{'✅' if river_modification_result else '❌'} River Modification test: {'PASSED' if river_modification_result else 'FAILED'}")
    all_passed = all_passed and river_modification_result

    print("=" * 80)

    if all_passed:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1


def test_full_file(file_path: str) -> bool:
    with open(file_path, "r") as f:
        original_lines = f.readlines()

    geometry_file = GeometryFile(file_path=file_path)

    generated_lines = geometry_file.generate()
    output_file = file_path.replace(".g01", ".output.g01")
    with open(output_file, "w") as f:
        f.writelines(generated_lines)

    generated_text = "".join(generated_lines)
    original_text = "".join(original_lines)
    return original_text == generated_text


def test_river_modification() -> bool:
    """测试河流修改功能"""
    # 加载测试文件
    g_file = GeometryFile(file_path="tests/data/all.g01")

    # 创建RiverModel实例
    river_model = RiverModel(g_file)

    # 获取所有河段的折线点
    river_data_json = river_model.get_all_river_reach_lines()
    river_data = json.loads(river_data_json)

    if river_data.get("status") == "success" and river_data.get("data"):
        # 遍历所有河流和河段
        for river_name, reaches in river_data["data"].items():
            for reach_name, points in reaches.items():
                # 修改每个点的坐标：x加10，y减10
                modified_points = []
                for point in points:
                    x, y = point
                    modified_points.append([x + 10, y - 10])
                
                # 更新河段
                update_data = {
                    "River": river_name,
                    "Reach": reach_name,
                    "Reach XY": modified_points
                }
                response = river_model.update_or_create_river_reach(json.dumps(update_data))
                print(f"Updated {river_name} - {reach_name}: {response}")

    # 生成新的g01文件
    output_file = "tests/data/all.river.output.g01"
    generated_lines = g_file.generate()
    with open(output_file, "w") as f:
        f.writelines(generated_lines)

    print(f"\nGenerated output file: {output_file}")

    # 检查是否存在模板文件
    template_file = "tests/data/all.river.template.g01"
    if os.path.exists(template_file):
        # 读取模板文件内容
        with open(template_file, "r") as f:
            template_content = f.read()
        
        # 读取生成的文件内容
        with open(output_file, "r") as f:
            output_content = f.read()
        
        # 比较两个文件
        return template_content == output_content
    else:
        print(f"\nTemplate file not found: {template_file}")
        print("Please create the template file based on the generated output.")
        return False


if __name__ == "__main__":
    exit(main())
