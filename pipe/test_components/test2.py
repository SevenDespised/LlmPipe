class Processor:
    def __init__(self):
        """
        初始化 Processor 类，无需额外参数
        """
        pass

    def generate_prompt(self, input_data):
        """
        生成提示词，在输入数据前添加 "Processed: " 前缀
        """
        # 将输入数据转换为字符串，并添加前缀
        text = input_data["text"]
        prompt = f"{text}, 将这段话翻译为中文。\n请一定以json格式返回结果，样例:{{\"text\": output}}"
        return prompt