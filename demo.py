# pipeline demo
import os
import json
from src.pipe.pipeline import PipelineProcessor
from pprint import pprint

BASE_DIR = ""
CONF_DIR = "config/test_config.json"

class client:
    def response(self, text):
        return text
def main():
    # 读取config.json文件
    path = os.path.join(BASE_DIR, CONF_DIR)
    with open(path, 'r') as f:
        config = json.load(f)

    # 创建PipelineProcessor实例
    pipeline_processor = PipelineProcessor(config)

    # 准备初始输入
    initial_input = {"text": "what is your favorite food"}
    {"client1": "1-50",
     "client2": "51-100"}
    # 设置client
    # 执行流水线
    result = pipeline_processor.execute_pipeline(initial_input)

    pprint(result, indent=2)
    #print(pipeline_processor.execution_data.get_all_data())

if __name__ == "__main__":
    main()