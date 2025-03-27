# pipeline_processor.py
import time
import importlib
import json
import os
from typing import List, Dict, Any

from .parse import parse_response
from .client import OpenAIClient
from .storage import StageExecutionData
BASE_DIR = ".."
CONF_DIR = "config/test_config.json"

class PipelineProcessor:
    def __init__(self, config: Dict):
        """提示工程算法流水线处理
        使用importlib库导入自定义流水线组件，并依次执行。
        流水线组件接收初始输入或上一组件经大模型后的响应输出，并生成提示词
        流水线组件代码至少应实现Processor类
            Processor类至少应实现：
                __init__方法：用于类的初始构造
                generate方法：用于提示词生成

        执行流程示例（其中，小写单词代表输入或输出，大写单词代表功能模块）：
        input -> COMPONENT1 -> prompt1 -> LLM -> response1 ->
        COMPONENT2 -> prompt2 -> LLM -> response2 -> POSTPROCESS -> output
        
        config配置说明：
        - processing_chain: 链式处理组件调用配置参数
            - name: str: 组件名称
            - module: str: importlib导入组件路径
            - init_kwargs: Dict: （可选）组件初始化参数
        - model_config: 模型api调用配置参数
        - max_history_length: （可选）指定历史记录最大长度，超过长度则丢弃最早记录
        """

        self.model_client = self._load_model_client(config['model_config'])
        self.processing_chain = self._load_processing_chain(config['processing_chain'])
        self.error_policy = config.get('error_handling', {})

        self.history = []
        self.max_history_length = config.get('history_limit', 0)

        self.execution_data = StageExecutionData()

    def _load_model_client(self, config: Dict) -> Any:
        """动态加载模型客户端"""
        try:
            client_class = OpenAIClient(config = config)
            return client_class
        except Exception as e:
            raise RuntimeError(f"加载模型客户端失败: {str(e)}")

    def _load_processing_chain(self, chain_config: List[Dict]) -> List[Dict]:
        """动态加载处理阶段配置"""
        processed_chain = []
        for stage_config in chain_config:
            try:
                module = importlib.import_module(stage_config['module'])
                stage_config['processor'] = module.Processor(
                    **stage_config.get('init_kwargs', {})
                )
                processed_chain.append(stage_config)
            except Exception as e:
                raise RuntimeError(
                    f"加载模块{stage_config['module']}失败: {str(e)}"
                )
        return processed_chain

    def execute_pipeline(self, initial_input: Dict) -> Dict:
        """执行动态处理流程"""
        total_start_time = time.time()
        current_output = initial_input
        execution_report = []
        self.execution_data.clear_data()
        # 遍历处理链中的每个阶段
        for idx, stage in enumerate(self.processing_chain):
            start_time = time.time()
            stage_name = stage['name']
            processor = stage['processor']
            
            # 开始记录阶段数据
            self.execution_data.start_stage(stage_name, initial_input)
            try:
                # 生成提示
                prompt = processor.generate_prompt(current_output, self.execution_data)
                self.execution_data.record_prompt(prompt)
                
                # 调用模型
                response = self._call_model(prompt)
                self.execution_data.record_response(response['content'])
                
                # 解析响应
                parsed = self._parse_response(response['content'])
                current_output = parsed['data'] if parsed["valid"] else parsed['original']
                self.execution_data.record_output(current_output)

                # 后处理
                if hasattr(processor, 'post_process') and processor.if_post_process:
                    current_output = processor.post_process(current_output)
                    self.execution_data.record_output(current_output)
                
                # 变量存储
                variable_storage = None
                if hasattr(processor, 'store_variable_in_pipeline') and processor.if_store_variable:
                    variable_storage = processor.store_variable_in_pipeline()
                    self.execution_data.record_cache(variable_storage)
                
                # 生成执行报告
                stage_record = {
                    "stage": stage_name,
                    "prompt": prompt,
                    "raw_response": response['content'],
                    "parsed_output": parsed,
                    "status": "success",
                    "tokens": response['tokens']
                }
                execution_report.append(stage_record)

                # 记录执行时间
                stage_time = f"{time.time() - start_time:.2f}s"
                print(f"阶段 {stage_name} 执行时间: {stage_time}")
                self.execution_data.record_execution_time(stage_time)
                # 完成数据记录
                self.execution_data.finalize_stage('success')

            except Exception as e:
                # 记录执行时间
                stage_time = f"{time.time() - start_time:.2f}s"
                print(f"阶段 {stage_name} 执行错误，时间: {stage_time}")
                self.execution_data.record_execution_time(stage_time)
                # 阶段数据记录失败
                self.execution_data.record_output(current_output)
                self.execution_data.finalize_stage('failed')

                # 记录错误信息
                stage_record = {
                    "stage": stage_name,
                    "status": "failed",
                    "error": str(e),
                    "tokens": response.get('tokens', 0) if 'response' in locals() else 0
                }
                execution_report.append(stage_record)

        # 将阶段存储添加至历史记录
        self._add_history(self.execution_data.get_all_data())
        # 记录总执行时间
        total_time = f"{time.time() - total_start_time:.2f}s"
        # 返回执行报告和最终输出
        return {
            "success": all(s['status'] == 'success' for s in execution_report),
            "execution_report": execution_report,
            "output_data": current_output,
            "execution_time": total_time,
            "model_name": self.model_client.model_name
        }

    # 将输出有限制的添加进历史记录
    def _add_history(self, storage: StageExecutionData) -> None:
        if self.max_history_length == 0:
            return
        if self.max_history_length > -1 and len(self.history) >= self.max_history_length:
            self.history.pop(0)
        self.history.append(storage)
    # 清空历史记录
    def clear_history(self) -> None:
        self.history = []

    def _parse_response(self, response: str) -> Dict:
        return parse_response(response = response)
    def _call_model(self, prompt):
        return self.model_client.generate(prompt)


if __name__ == "__main__":
    # 读取config.json文件
    path = os.path.join(BASE_DIR, CONF_DIR)
    with open(path, 'r') as f:
        config = json.load(f)

    # 创建PipelineProcessor实例
    pipeline_processor = PipelineProcessor(config)

    # 准备初始输入
    initial_input = {"text": "what is your favorite food"}

    # 执行流水线
    result = pipeline_processor.execute_pipeline(initial_input)

    # 打印结果
    print("执行结果:", result["success"])
    print("执行报告:")
    for report in result["execution_report"]:
        for key, value in report.items():
            print(f'{key}: {value}')
    print("最终输出:", result["final_output"]["text"])