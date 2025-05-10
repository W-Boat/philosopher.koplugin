import json
import os

def process_json_file(filepath):
    """
    读取单个 JSON 文件，校验格式，并提取指定字段。

    Args:
        filepath (str): JSON 文件的路径。

    Returns:
        list: 包含提取后数据的字典列表，如果文件无效或不符合预期结构则返回空列表。
    """
    processed_data = []
    filename = os.path.basename(filepath) # 用于错误信息

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 检查数据是否是列表或单个字典
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        processed_item = {
                            "type": item.get("type"),
                            "hitokoto": item.get("hitokoto"),
                            "from_who": item.get("from_who"),
                            "from": item.get("from")
                        }
                        processed_data.append(processed_item)
                    else:
                        print(f"警告: 文件 '{filename}' 中的列表项 '{str(item)[:50]}...' 不是一个有效的对象，已跳过。")
            elif isinstance(data, dict): # 处理根元素是单个JSON对象的情况
                processed_item = {
                    "type": data.get("type"),
                    "hitokoto": data.get("hitokoto"),
                    "from_who": data.get("from_who"),
                    "from": data.get("from")
                }
                processed_data.append(processed_item)
            else:
                print(f"警告: 文件 '{filename}' 的顶层结构不是列表或字典，已跳过。")
    except json.JSONDecodeError:
        print(f"错误: 文件 '{filename}' 不是有效的 JSON 格式，已跳过。")
    except FileNotFoundError:
        print(f"错误: 文件 '{filename}' 未找到，已跳过。")
    except UnicodeDecodeError:
        print(f"错误: 文件 '{filename}' 编码可能不是 UTF-8，无法读取。请确保文件是 UTF-8 编码，已跳过。")
    except Exception as e:
        print(f"处理文件 '{filename}' 时发生未知错误: {e}，已跳过。")
    return processed_data

def process_folder(folder_path, output_filename="data.json"):
    """
    处理指定文件夹下所有 JSON 文件，合并提取的数据并输出到新文件。

    Args:
        folder_path (str): 包含 JSON 文件的文件夹路径。
        output_filename (str, optional): 输出合并数据的 JSON 文件名。
                                        默认为 "data.json"。
    """
    all_processed_data = []
    if not os.path.isdir(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在或不是一个有效的目录。")
        return

    print(f"开始处理文件夹: {folder_path}")
    found_json_files = False
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".json") and filename.lower() != output_filename.lower(): # 避免处理自己生成的输出文件
            filepath = os.path.join(folder_path, filename)
            print(f"  正在处理文件: {filename}")
            found_json_files = True
            data = process_json_file(filepath)
            all_processed_data.extend(data)

    if not found_json_files:
        print("在指定的文件夹中没有找到 .json 文件 (除了可能的输出文件)。")
        return

    if all_processed_data:
        output_filepath = os.path.join(folder_path, output_filename)
        try:
            with open(output_filepath, 'w', encoding='utf-8') as outfile:
                json.dump(all_processed_data, outfile, ensure_ascii=False, indent=2)
            print(f"\n处理完成！合并后的数据已保存到: {output_filepath}")
        except Exception as e:
            print(f"写入输出文件 '{output_filepath}' 时发生错误: {e}")
    else:
        print("\n没有成功提取到任何数据，未生成输出文件。")

if __name__ == "__main__":
    folder_to_process = input("请输入包含 JSON 文件的文件夹路径: ").strip()
    if folder_to_process:
        process_folder(folder_to_process)
    else:
        print("未输入文件夹路径。")

    # 示例用法说明:
    # 1. 将此脚本保存为 .py 文件 (例如, process_my_jsons.py)。
    # 2. 创建一个文件夹，例如 "my_jsons"。
    # 3. 将您的 JSON 文件放入 "my_jsons" 文件夹中。
    #    您的示例 JSON 可以保存为 "example1.json":
    #    [
    #      {
    #        "commit_from": "web",
    #        "created_at": "1468605909",
    #        "creator": "跳舞的果果",
    #        "creator_uid": 0,
    #        "from": "幸运星",
    #        "from_who": null,
    #        "hitokoto": "与众不同的生活方式很累人呢，因为找不到借口。",
    #        "id": 1,
    #        "length": 22,
    #        "reviewer": 0,
    #        "type": "a",
    #        "uuid": "9818ecda-9cbf-4f2a-9af8-8136ef39cfcd"
    #      },
    #      {
    #        "commit_from": "api",
    #        "created_at": "1500000000",
    #        "creator": "测试员",
    #        "creator_uid": 1,
    #        "from": "某作品",
    #        "from_who": "某角色",
    #        "hitokoto": "这是另一条一言。",
    #        "id": 2,
    #        "length": 10,
    #        "reviewer": 1,
    #        "type": "b",
    #        "uuid": "another-uuid-string"
    #      }
    #    ]
    #    您可以创建更多类似的 JSON 文件。
    # 4. 运行脚本: python process_my_jsons.py
    # 5. 当提示时，输入文件夹路径 (例如, my_jsons，或者如果不在同一目录，输入完整路径)。
    # 6. 脚本将在 "my_jsons" 文件夹内生成一个 "data.json" 文件，其中包含所有处理后的数据。
