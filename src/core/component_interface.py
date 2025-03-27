from abc import ABC, abstractmethod
from typing import Any, Dict
from ..pipe.storage import StageExecutionData

class IProcessor(ABC):
    """
    Processor接口
    """
    
    @property
    @abstractmethod
    def if_store_variable(self) -> bool:
        """是否在流水线中存储该组件的变量"""
        ...
    
    @property
    @abstractmethod
    def if_post_process(self) -> bool:
        """是否启用后处理逻辑"""
        ...

    @abstractmethod
    def generate_prompt(self, input_data: Any, data: StageExecutionData = None) -> str:
        """
        生成提示词的核心逻辑
        :param input_data: 组件输入数据
        :param data: 流水线中间数据类
        :return: 构造完成的提示词字符串
        """
        ...

    @abstractmethod
    def post_process(self, output_data: Any) -> Dict[str, Any]:
        """
        对模型响应进行后处理，如不启用，直接返回原始数据
        :param output_data: 经过模型响应的输出数据
        :return: 处理后的结构化数据
        """
        ...

    @abstractmethod
    def store_variable_in_pipeline(self) -> Any:
        """
        向流水线暴露需要存储的变量，如不启用，直接返回None
        :return: 需存储的变量（类型由具体组件决定）
        """
        ...
