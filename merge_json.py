import json
import sys
import os
from pathlib import Path
from collections import defaultdict

def find_json_files(paths):
    """查找所有JSON文件路径"""
    json_files = []
    
    def scan_directory(directory):
        """扫描目录获取JSON文件"""
        for entry in os.scandir(directory):
            if entry.is_file() and entry.name.endswith('.json'):
                yield entry.path
            elif entry.is_dir():
                yield from scan_directory(entry.path)  # 递归子目录

    for path in paths:
        if os.path.isfile(path):
            if path.endswith('.json'):
                json_files.append(path)
        elif os.path.isdir(path):
            json_files.extend(scan_directory(path))
        else:
            print(f"警告：忽略无效路径 {path}")

    return sorted(json_files)  # 按路径排序保证可重复性

def validate_json_structure(files):
    """验证JSON结构一致性"""
    structures = set()
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                structures.add(type(data).__name__)
        except json.JSONDecodeError:
            print(f"错误：无效的JSON文件 {file}")
            sys.exit(1)
    
    if len(structures) > 1:
        print("错误：检测到不一致的JSON结构")
        print(f"发现类型: {', '.join(structures)}")
        sys.exit(1)
    return structures.pop()

def merge_json_files(input_paths, output_file, merge_mode='auto'):
    """
    合并JSON文件/目录
    :param input_paths: 文件或目录路径列表
    :param output_file: 输出文件路径
    :param merge_mode: 合并模式 (auto|array|object)
    """
    # 查找所有JSON文件
    all_files = find_json_files(input_paths)
    
    if not all_files:
        print("错误：未找到任何JSON文件")
        return

    print("找到以下JSON文件：")
    for f in all_files:
        print(f"  - {f}")

    # 自动检测结构
    if merge_mode == 'auto':
        structure_type = validate_json_structure(all_files)
        merge_mode = 'array' if structure_type == 'list' else 'object'

    # 执行合并
    merged_data = [] if merge_mode == 'array' else defaultdict(list)
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if merge_mode == 'array':
                    if isinstance(data, list):
                        merged_data.extend(data)
                    else:
                        print(f"警告：{file_path} 不是数组，已跳过")
                        
                elif merge_mode == 'object':
                    if isinstance(data, dict):
                        for k, v in data.items():
                            merged_data[k].append(v)
                    else:
                        print(f"警告：{file_path} 不是对象，已跳过")
                        
        except Exception as e:
            print(f"处理 {file_path} 时出错: {str(e)}")

    # 转换对象类型
    if merge_mode == 'object':
        merged_data = {k: v[0] if len(v) == 1 else v for k, v in merged_data.items()}

    # 写入输出文件
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2, sort_keys=True)
    
    print(f"\n成功合并 {len(all_files)} 个文件到 {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方法: python merge_json.py [选项] <输出文件> <输入路径...>")
        print("选项:")
        print("  -a      自动检测模式 (默认)")
        print("  -array  强制数组模式合并")
        print("  -object 强制对象模式合并")
        print("  -h      显示帮助信息")
        print("\n示例:")
        print("  # https://github.com/hitokoto-osc/sentences-bundle/ 以上是一言核心库，你可以从中下载最新一言。将该文件复制到你下载的 sentences 文件夹中，然后运行以下代码，把最终生成的文件放到插件文件夹中：（其实就只是合并一下）")
        print("  python merge_json.py data.json ./")
        sys.exit()

    # 参数解析
    mode = 'auto'
    if sys.argv[1].startswith('-'):
        mode_map = {
            '-a': 'auto',
            '-array': 'array',
            '-object': 'object',
            '-h': 'help'
        }
        mode = sys.argv[1].lower()
        if mode == '-h':
            print("帮助信息...")
            sys.exit()
        mode = mode_map.get(mode, 'auto')
        output_file = sys.argv[2]
        input_paths = sys.argv[3:]
    else:
        output_file = sys.argv[1]
        input_paths = sys.argv[2:]

    # 检查输入路径是否存在
    valid_paths = []
    for p in input_paths:
        if not os.path.exists(p):
            print(f"警告：路径 {p} 不存在，已跳过")
        else:
            valid_paths.append(p)

    if not valid_paths:
        print("错误：没有有效的输入路径")
        sys.exit(1)

    # 执行合并
    merge_json_files(
        input_paths=valid_paths,
        output_file=output_file,
        merge_mode=mode
    )