import json
import sys
import os

def process_json_content(json_string, filename=""):
    """
    处理 JSON 字符串，只保留每个对象中的 "id" 和 "desc" 字段。
    自动检验 JSON 格式。

    Args:
        json_string (str): 包含 JSON 数据的字符串。
        filename (str, optional): 原始文件名，用于错误报告。默认为空。

    Returns:
        tuple: (processed_data, error_message)
               processed_data (list or dict or None): 处理后的数据。
               error_message (str or None): 如果发生错误，则为错误信息字符串；否则为 None。
    """
    processed_output = None
    error_msg = None

    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        error_msg = f"文件 '{filename}' 中的 JSON 格式无效: {e}"
        return None, error_msg
    except Exception as e:
        error_msg = f"解析文件 '{filename}' 中的 JSON 时发生未知错误: {e}"
        return None, error_msg

    if isinstance(data, list):
        processed_output = []
        for item in data:
            if isinstance(item, dict):
                new_item = {
                    "id": item.get("id"),
                    "desc": item.get("desc") # 保留 "desc" 字段，如果不存在则为 None
                }
                processed_output.append(new_item)
            else:
                print(f"警告: 文件 '{filename}' 中的列表项 '{item}' 不是一个有效的对象，已跳过。")
    elif isinstance(data, dict):
        processed_output = {
            "id": data.get("id"),
            "desc": data.get("desc") # 保留 "desc" 字段，如果不存在则为 None
        }
    else:
        error_msg = f"错误: 文件 '{filename}' 中的 JSON 数据必须是列表或单个对象结构。"
        return None, error_msg

    return processed_output, error_msg

def main():
    # sys.argv[0] 是脚本本身的名称
    # sys.argv[1:] 是传递给脚本的参数列表 (即拖拽的文件路径)
    if len(sys.argv) < 2:
        print("使用方法: 请将一个或多个 JSON 文件拖拽到此脚本文件上执行。")
        print("或者通过命令行运行: python your_script_name.py file1.json file2.json ...")
        input("按 Enter 键退出。") # 防止窗口在双击运行时立即关闭
        return

    dropped_files = sys.argv[1:]
    print(f"检测到 {len(dropped_files)} 个文件准备处理...\n")

    for filepath in dropped_files:
        print(f"--- 正在处理文件: {filepath} ---")
        filename = os.path.basename(filepath) # 获取文件名部分

        if not os.path.isfile(filepath):
            print(f"错误: '{filepath}' 不是一个有效的文件路径或文件不存在，已跳过。\n")
            continue

        if not filepath.lower().endswith(".json"):
            print(f"警告: 文件 '{filename}' 可能不是 JSON 文件 (非 .json 后缀)。正在尝试处理...\n")
            # 你可以选择在这里跳过非 .json 文件:
            # print(f"错误: 文件 '{filename}' 不是 .json 文件，已跳过。\n")
            # continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            processed_data, error = process_json_content(content, filename)

            if error:
                print(f"处理文件 '{filename}' 时发生错误: {error}\n")
            elif processed_data is not None:
                print(f"文件 '{filename}' 处理后的数据:")
                print(json.dumps(processed_data, indent=2, ensure_ascii=False))

                # (可选) 保存处理后的文件
                output_dir = os.path.dirname(filepath) # 获取原始文件所在目录
                base, ext = os.path.splitext(filename)
                output_filename = os.path.join(output_dir, f"types.json")
                try:
                    with open(output_filename, 'w', encoding='utf-8') as outfile:
                        json.dump(processed_data, outfile, indent=2, ensure_ascii=False)
                    print(f"已将处理后的数据保存到: {output_filename}\n")
                except Exception as e_save:
                    print(f"保存处理后的文件 '{output_filename}' 失败: {e_save}\n")
            else:
                print(f"文件 '{filename}' 未产生有效输出或为空。\n")

        except FileNotFoundError:
            print(f"错误: 文件 '{filepath}' 未找到，已跳过。\n")
        except UnicodeDecodeError:
            print(f"错误: 文件 '{filepath}' 编码可能不是 UTF-8，无法读取。请确保文件是 UTF-8 编码。\n")
        except Exception as e:
            print(f"读取或处理文件 '{filepath}' 时发生未知错误: {e}\n")

    print("所有文件处理完毕。")
    input("按 Enter 键退出。") # 防止窗口在处理完毕后立即关闭

if __name__ == "__main__":
    main()
