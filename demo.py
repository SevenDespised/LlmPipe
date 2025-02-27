# pipeline demo
import os
import json
from pipe.pipeline import PipelineProcessor

BASE_DIR = ""
CONF_DIR = "config/test_config.json"

def main():
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

if __name__ == "__main__":
    main()