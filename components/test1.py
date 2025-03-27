from typing import Any, Dict
from src.core.component_interface import IProcessor
from src.pipe.storage import StageExecutionData

class Processor(IProcessor):
    def __init__(self, system: str):
        """
        初始化 Processor 类，接收系统信息作为参数
        :param system: 系统信息，例如角色设定等
        """
        self.system = system
        self.prompt = None
        self._if_store_variable = True
        self._if_post_process = True

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
        生成提示词，将系统信息和输入数据结合
        """
        # 获取输入数据中的文本信息，如果没有则使用空字符串
        text = input_data.get('text', '') if isinstance(input_data, dict) else ""
        prompt = f"system: {self.system}\nuser: {text}\nplease return result as json，example:{{\"text\": output}}"
        self.prompt = prompt
        return prompt

    def post_process(self, output_data: Any) -> Dict[str, Any]:
        """对模型响应进行后处理"""
        if isinstance(output_data, dict) and "text" in output_data:
            output_data["text"] = "Hahahahaha!" + output_data["text"]
        return output_data

    def store_variable_in_pipeline(self) -> Any:
        """向流水线暴露需要存储的变量"""
        return self.system