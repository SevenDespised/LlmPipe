import json
import os
import re


BASE_DIR = "prompt_texts"
LANGUAGE_JSON_PATHS = {
    "zh": os.path.join(BASE_DIR, "zh.json"),
    "en": os.path.join(BASE_DIR, "en.json")
}

def read_prompt(key, language="zh", **kwargs):
    """
    根据指定的语言和 key 从对应的 JSON 文件中读取单个字符串，并根据占位符填充相应的值。
    :param key: 要读取的字符串的键
    :param language: 语言标识，如 "zh"、"en" 等，默认值为 "zh"
    :param kwargs: 用于填充占位符的关键字参数
    :return: 填充后的字符串，如果未找到该键、值不是字符串或占位符不匹配则返回 None
    """
    if not key:
        print("请提供有效的键名。")
        return None
    if language not in LANGUAGE_JSON_PATHS:
        print(f"不支持的语言: {language}")
        return None

    file_path = LANGUAGE_JSON_PATHS[language]
    try:
        # 打开并读取 JSON 文件
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 检查 key 是否存在于 JSON 数据中
        if key in data:
            value = data[key]
            if isinstance(value, str):
                # 提取字符串中的占位符
                placeholders = re.findall(r'\{(\w+)\}', value)
                for placeholder in placeholders:
                    if placeholder not in kwargs:
                        print(f"字符串中存在未匹配的占位符 {{ {placeholder} }}，请提供对应的参数。")
                        return None
                try:
                    # 使用提供的关键字参数填充字符串中的占位符
                    filled_value = value.format(**kwargs)
                    return filled_value
                except KeyError:
                    # 如果占位符没有对应的参数，这里理论上不会执行，因为前面已经检查过
                    return None
            else:
                print(f"键 {key} 对应的值不是字符串类型。")
                return None
        else:
            print(f"在文件 {file_path} 中未找到键 {key}。")
            return None

    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    except json.JSONDecodeError:
        print(f"无法解析 {file_path} 为有效的 JSON。")

# 示例调用
if __name__ == "__main__":
    # 使用默认语言（中文）
    zh_greeting = read_prompt("greeting", name="张三")
    print("中文问候语结果：", zh_greeting)

    # 测试占位符不匹配的情况
    zh_info = read_prompt("info", age=25)
    print("中文信息结果：", zh_info)

    # 指定英文语言
    en_info = read_prompt("info", language="en", age=25)
    print("英文信息结果：", en_info)

    # 测试不支持的语言
    unsupported_lang = read_prompt("greeting", language="fr")
    print("不支持语言的结果：", unsupported_lang)