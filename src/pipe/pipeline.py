# pipeline_processor.py
import time
import importlib
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

        self.model_clients = self._load_model_clients(config['clients_config']['clients_list'])
        self.default_client_name = config['clients_config']['default_client']
        self.processing_chain = self._load_processing_chain(config['processing_chain_config'])
        self.error_policy = config.get('error_handling', {})

        self.history = []
        self.max_history_length = config.get('max_history_length', 0)

        self.execution_data = StageExecutionData()

    def execute_pipeline(self, initial_input: Dict) -> Dict:
        """执行动态处理流程"""
        total_start_time = time.time()
        total_tokens = 0
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
                response = self._call_model(prompt, stage.get('client_name', self.default_client_name))
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
                    "model": stage.get('client_name', self.default_client_name),
                    "prompt": prompt,
                    "raw_response": response['content'],
                    "parsed_output": parsed,
                    "status": "success",
                    "tokens": response.get('tokens', 0)
                }
                execution_report.append(stage_record)

                # 记录执行时间
                stage_time = f"{time.time() - start_time:.2f}s"
                print(f"阶段 {stage_name} 执行时间: {stage_time}")
                self.execution_data.record_execution_time(stage_time)
                # 记录token消耗
                total_tokens += response.get('tokens', 0)
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
                    "model": stage['client_name'],
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
            "tokens": total_tokens
        }
    def _load_model_clients(self, clients_config: Dict) -> Dict[str, Any]:
        """动态加载所有客户端配置"""
        clients = {}
        for client_name, client_config in clients_config.items():
            try:
                client_type = client_config.get("client_type", "openai")
                if client_type == "openai":
                    clients[client_name] = OpenAIClient(config=client_config['model_config'])
                elif client_type == "custom":
                    # 动态导入自定义客户端类
                    module = importlib.import_module(client_config['module'])
                    client_class = getattr(module, client_config['class_name'])
                    clients[client_name] = client_class(**client_config['model_config'])
                else:
                    raise ValueError(f"未知的客户端类型: {client_type}")
            except Exception as e:
                raise RuntimeError(f"加载客户端 {client_name} 失败: {str(e)}")
        return clients

    def _load_processing_chain(self, chain_config: List[Dict]) -> List[Dict]:
        """动态加载处理阶段配置"""
        processing_chain = []
        for stage_config in chain_config:
            try:
                module = importlib.import_module(stage_config['module'])
                Processor = getattr(module, stage_config['class_name'])
                stage_config['processor'] = Processor(
                    **stage_config.get('init_kwargs', {})
                )
                processing_chain.append(stage_config)
            except Exception as e:
                raise RuntimeError(
                    f"加载模块{stage_config['module']}失败: {str(e)}"
                )
        return processing_chain
    def _call_model(self, prompt, client_name: str):
        """调用模型客户端"""
        return self.model_clients[client_name].response(prompt)
    def _parse_response(self, response: str) -> Dict:
        """解析模型响应"""
        return parse_response(response = response)
    def _add_history(self, storage: StageExecutionData) -> None:
        """将阶段执行数据添加至历史记录"""
        if self.max_history_length == 0:
            return
        if self.max_history_length > -1 and len(self.history) >= self.max_history_length:
            self.history.pop(0)
        self.history.append(storage)
    def clear_history(self) -> None:
        """清空历史记录"""
        self.history = []