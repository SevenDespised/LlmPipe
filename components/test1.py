class Processor:
    def __init__(self, system):
        """
        初始化 Processor 类，接收系统信息作为参数
        :param system: 系统信息，例如角色设定等
        """
        self.system = system
        self.prompt = None
        self.if_store_variable = True
        self.if_post_process = True

    def generate_prompt(self, input_data, data = None):
        """
        生成提示词，将系统信息和输入数据结合
        """
        # 获取输入数据中的文本信息，如果没有则使用空字符串
        text = input_data.get('text', '')
        # 组合系统信息和输入文本，生成提示词
        prompt = f"system: {self.system}\nuser: {text}\nplease return result as json，example:{{\"text\": output}}"
        self.prompt = prompt
        return prompt
    
    def post_process(self, response):
        # 返回后处理后的结果
        response["text"] = "Hahahahaha!" + response["text"]
        return response
    
    def store_variable_in_pipeline(self):
        # 在管道中存储变量
        return self.system