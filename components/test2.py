from typing import Any, Dict
from src.core.component_interface import IProcessor
from src.pipe.storage import StageExecutionData

class Processor(IProcessor):
    def __init__(self):
        """
        初始化 Processor 类，无需额外参数
        """
        self._if_store_variable = False
        self._if_post_process = False

    @property
    def if_store_variable(self) -> bool:
        """是否在流水线中存储该组件的变量"""
        return self._if_store_variable

    @property
    def if_post_process(self) -> bool:
        """是否启用后处理逻辑"""
        return self._if_post_process

    def generate_prompt(self, input_data: Any, data: StageExecutionData = None) -> str:
        """
        生成提示词，在输入数据前添加 "Processed: " 前缀
        """
        text = input_data.get("text", "") if isinstance(input_data, dict) else str(input_data)
        prompt = f"{text}, 将这段话翻译为中文。\n请一定以json格式返回结果，样例:{{\"text\": output}}"
        return prompt

    def post_process(self, output_data: Any) -> Dict[str, Any]:
        """后处理（因未启用，直接返回原数据）"""
        return output_data

    def store_variable_in_pipeline(self) -> Any:
        """向流水线暴露需要存储的变量（默认返回空）"""
        return None