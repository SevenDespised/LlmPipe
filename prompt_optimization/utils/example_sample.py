import random
from collections import defaultdict

def sampled_example_str(dataset: list, x_key: str, y_key: str, sample_size=3, sampling_method='random'):
    """
    从给定的数据集中随机抽取样本，并将其转换为字符串格式返回。字符串示例如下。
    ""
    1.
    feature: value1
    label: class1  
    2.
    feature: value5
    label: class2
    ""
    :param dataset (list): 包含数据的列表，每个元素是一个字典，遍历嵌套结构搜索包含x_key和y_key对应的值。
    :param x_key (str): 字典中用于提取x值的键。
    :param y_key (str): 字典中用于提取y值的键。
    :param sample_size (int, optional): 抽取的样本数量，默认为3。
    :param sampling_method (str, optional): 抽取样本的方法，默认为'random'，表示随机抽取。可选值包括'random'、'stratified'、'systematic'.
    :return 包含抽取样本的字符串表示。
    """
    sample_data = example_sample(dataset, x_key, y_key, sample_size, sampling_method)
    return example_to_string(sample_data)

def example_to_string(dataset: list):
    
    example_string = ""
    for i, data in enumerate(dataset, start=1):
        example_string += f"{i}.\n"
        for key, value in data.items():
            example_string += f"{key}: {value}\n"
    return example_string

def random_sampling(data, sample_size):
    """
    随机采样方法
    :param data: 数据集
    :param sample_size: 采样数量
    :return: 采样后的数据集
    """
    if sample_size > len(data):
        raise ValueError("采样数量不能超过数据集的大小。")
    return random.sample(data, sample_size)


def stratified_sampling(data, sample_size, stratify_key):
    """
    分层采样方法
    :param data: 数据集
    :param sample_size: 采样数量
    :param stratify_key: 分层依据的键
    :return: 采样后的数据集
    """
    strata = defaultdict(list)
    for sample in data:
        strata[sample[stratify_key]].append(sample)

    total_samples = 0
    final_samples = []
    for stratum in strata.values():
        stratum_size = int(len(stratum) / len(data) * sample_size)
        if stratum_size > len(stratum):
            stratum_size = len(stratum)
        final_samples.extend(random.sample(stratum, stratum_size))
        total_samples += stratum_size

    # 如果采样数量不足，从剩余数据中随机补充
    if total_samples < sample_size:
        remaining_samples = [s for s in data if s not in final_samples]
        additional_samples = random.sample(remaining_samples, sample_size - total_samples)
        final_samples.extend(additional_samples)

    return final_samples


def systematic_sampling(data, sample_size):
    """
    系统采样方法
    :param data: 数据集
    :param sample_size: 采样数量
    :return: 采样后的数据集
    """
    data_length = len(data)
    if sample_size > data_length:
        raise ValueError("采样数量不能超过数据集的大小。")
    step = data_length // sample_size
    start = random.randint(0, step - 1)
    indices = list(range(start, data_length, step))[:sample_size]
    return [data[i] for i in indices]


def example_sample(data: list, x_key: str, y_key: str, sample_size=None, sampling_method='random'):
    """
    遍历数据集，提取每条数据中的 x_key 和 y_key 对应的值，并支持采样操作

    :param data: 包含多条数据的列表，每条数据是一个嵌套字典或列表
    :param x_key: 需要提取的键 x
    :param y_key: 需要提取的键 y
    :param sample_size: 采样数量，默认为 None 表示不进行采样
    :param sampling_method: 采样方法，可选值为 'random'（随机采样）、'stratified'（分层采样）、
                            'systematic'（系统采样）默认为 'random'
    :return: 包含所有有效数据对的字典列表
    """
    samples = []

    def find_values(item):
        """
        递归查找单个数据条目中的 x_key 和 y_key 值
        """
        x_val = None
        y_val = None

        def traverse(sub_item):
            nonlocal x_val, y_val
            if isinstance(sub_item, dict):
                for key, value in sub_item.items():
                    if key == x_key and x_val is None:
                        x_val = value
                    elif key == y_key and y_val is None:
                        y_val = value
                    # 提前终止条件
                    if x_val is not None and y_val is not None:
                        return
                    traverse(value)
                    if x_val is not None and y_val is not None:
                        return
            elif isinstance(sub_item, list):
                for element in sub_item:
                    if x_val is not None and y_val is not None:
                        break
                    traverse(element)

        traverse(item)
        return {x_key: x_val, y_key: y_val}

    all_samples = [find_values(item) for item in data]

    if sample_size is not None:
        try:
            if sampling_method == 'random':
                samples = random_sampling(all_samples, sample_size)
            elif sampling_method == 'stratified':
                samples = stratified_sampling(all_samples, sample_size, y_key)
            elif sampling_method == 'systematic':
                samples = systematic_sampling(all_samples, sample_size)
            else:
                raise ValueError("不支持的采样方法，请选择 'random'、'stratified'、'systematic'。")
        except ValueError as ve:
            print(f"采样过程中出现错误: {ve}")
            samples = all_samples
        except Exception as e:
            print(f"发生未知错误: {e}")
            samples = all_samples
    else:
        samples = all_samples
    return samples

if __name__ == "__main__":
    # 示例数据集
    dataset = [
        {"feature": "value1", "label": "class1"},
        {"feature": "value2", "label": "class2"},
        {"feature": "value3", "label": "class1"},
        {"feature": "value4", "label": "class2"},
        {"feature": "value5", "label": "class1"},
        {"feature": "value6", "label": "class2"}
    ]

    # 定义要提取的键
    x_key = "feature"
    y_key = "label"

    # 调用 sampled_example_str 函数
    result = sampled_example_str(dataset, x_key, y_key, sample_size=3, sampling_method='random')

    # 打印结果
    print(result)