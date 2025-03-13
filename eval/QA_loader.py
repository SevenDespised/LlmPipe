from typing import List, Dict, Callable, Iterator, Union
from collections import deque

class QA_loader:
    def __init__(self, load_fn: Callable[[str], Union[List[Dict], Iterator[Dict]]], preprocess_fn: Callable[[List[Dict]], List[Dict]] = None, chunk_size: int = 32):
        """
        初始化 QA_loader 类，支持任何自定义数据加载和预处理函数。

        :param load_fn: 用于加载数据的函数，接受文件路径并返回一个数据列表或数据迭代器。
        :param preprocess_fn: 用于数据预处理的函数，默认情况下将数据直接返回。
        :param chunk_size: 每次加载的批量大小（默认为 32）。
        """
        self.load_fn = load_fn
        self.preprocess_fn = preprocess_fn or self.default_preprocess_fn
        self.chunk_size = chunk_size
        self.data = None

    def load_data(self, file_path: str) -> None:
        """使用提供的加载函数从指定路径加载数据。 """
        self.data = self.load_fn(file_path)

    def default_preprocess_fn(self, data: List[Dict]) -> List[Dict]:
        """默认的预处理函数，将原始数据转换为 QA 对。如果不提供自定义预处理函数，使用此默认行为。"""
        qa_data = []
        for item in data:
            # 假设每个数据项有 'question' 和 'answer' 字段，您可以根据需求进行调整。
            question = item.get('question')
            answer = item.get('answer')
            if question and answer:
                qa_data.append({'question': question, 'answer': answer})
        return qa_data

    def preprocess_data(self) -> List[Dict[str, str]]:
        """预处理加载的数据，返回 QA 对。"""
        if not self.data:
            raise ValueError("Data is not loaded. Please load data first.")
        
        return self.preprocess_fn(self.data)

    def generate_qa_iterator(self) -> Iterator[Dict[str, str]]:
        """生成 QA 数据的迭代器。"""
        qa_data = self.preprocess_data()
        for qa in qa_data:
            yield qa

    def generate_chunked_qa_data(self) -> Iterator[List[Dict[str, str]]]:
        """根据分块大小生成 QA 数据，每次返回一个批量大小的 QA 数据。"""
        qa_data = self.preprocess_data()
        chunk = deque(maxlen=self.chunk_size)
        
        for qa in qa_data:
            chunk.append(qa)
            if len(chunk) == self.chunk_size:
                yield list(chunk)
                chunk.clear()
        
        if chunk:
            yield list(chunk)

    def generate_all_qa_data(self) -> List[Dict[str, str]]:
        """生成并返回所有的 QA 数据。"""
        return self.preprocess_data()
