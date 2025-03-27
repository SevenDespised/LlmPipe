from typing import Any, Dict, List, Optional

class StageExecutionData:
    """流水线阶段执行数据存储类"""
    def __init__(self):
        self.stages = []  # 存储各阶段数据的列表
        self._current_stage = None  # 当前阶段临时存储

    def start_stage(self, stage_name: str, initial_input: Any):
        """开始记录新阶段"""
        self._current_stage = {
            'stage_name': stage_name,
            'initial_input': initial_input,
            'output': None,
            'cache': None,
            'prompt': None,
            'raw_response': None,
            'status': 'pending',
            'execution_time': None
        }

    def record_prompt(self, prompt: str):
        """记录生成的提示词"""
        if self._current_stage:
            self._current_stage['prompt'] = prompt

    def record_response(self, response: str):
        """记录原始响应"""
        if self._current_stage:
            self._current_stage['raw_response'] = response

    def record_output(self, output: Any):
        """记录阶段输出"""
        if self._current_stage:
            self._current_stage['output'] = output

    def record_cache(self, cache: Any):
        """记录cache"""
        if self._current_stage:
            self._current_stage['cache'] = cache

    def record_execution_time(self, timestring: str):
        """记录执行时间"""
        if self._current_stage:
            self._current_stage['execution_time'] = timestring

    def finalize_stage(self, status: str = 'completed'):
        """完成阶段记录"""
        if self._current_stage:
            self._current_stage['status'] = status
            self.stages.append(self._current_stage.copy())
            self._current_stage = None

    def get_stage_data(self, stage_name: str) -> Optional[Dict]:
        """按阶段名称获取数据"""
        for stage in reversed(self.stages):
            if stage['stage_name'] == stage_name:
                return stage
        return None

    def get_all_data(self) -> List[Dict]:
        """获取完整执行数据"""
        return self.stages.copy()

    def clear_data(self):
        """清空历史数据"""
        self.stages.clear()

    def get_initial_input(self) -> Any:
        """获取流水线原始输入"""
        stage_data = self.get_stage_by_index(0)
        return stage_data.get('initial_input')
    
    def get_output(self, stage_name: str) -> Any:
        """获取阶段输出"""
        stage_data = self.get_stage_data(stage_name)
        return stage_data.get('output')

    def get_cache(self, stage_name: str) -> Any:
        """获取存储变量"""
        stage_data = self.get_stage_data(stage_name)
        return stage_data.get('cache')

    def get_prompt(self, stage_name: str) -> str:
        """获取提示内容"""
        stage_data = self.get_stage_data(stage_name)
        return stage_data.get('prompt', '')

    def get_raw_response(self, stage_name: str) -> str:
        """获取原始响应"""
        stage_data = self.get_stage_data(stage_name)
        return stage_data.get('raw_response', '')

    def get_status(self, stage_name: str) -> str:
        """获取执行状态"""
        stage_data = self.get_stage_data(stage_name)
        return stage_data.get('status', 'unknown_status')
    
    def get_execution_time(self, stage_name: str) -> str:
        """获取执行时间"""
        stage_data = self.get_stage_data(stage_name)
        return stage_data.get('execution_time')

    def get_stage_by_index(self, index: int) -> Optional[dict]:
        """通过索引获取阶段数据"""
        try:
            return self.stages[index]
        except IndexError:
            return None

    def get_latest_stage_data(self) -> Optional[dict]:
        """获取最近一次阶段数据"""
        return self.stages[-1] if self.stages else None

    def get_failed_stages(self) -> List[dict]:
        """获取所有失败的阶段"""
        return [stage for stage in self.stages if self.get_status(stage) == 'failed']