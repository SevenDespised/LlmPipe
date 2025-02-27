class Processor:
    def __init__(self, system):
        """
        初始化 Processor 类，接收系统信息作为参数
        :param system: 系统信息，例如角色设定等
        """
        self.system = system

    def generate_prompt(self, input_data):
        """
        生成提示词，将系统信息和输入数据结合
        """
        # 获取输入数据中的文本信息，如果没有则使用空字符串
        text = input_data.get('text', '')
        # 组合系统信息和输入文本，生成提示词
        prompt = f"system: {self.system}\nuser: {text}\n请一定以json格式返回结果，样例:{{\"text\": output}}"
        return prompt