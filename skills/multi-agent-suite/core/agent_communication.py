# Agent间通信模块
# 实现Agent消息传递和协作

class AgentCommunication:
    """Agent通信中心"""
    
    def __init__(self):
        self.messages = []
        self.subscriptions = {}
    
    def send_message(self, from_agent, to_agent, message_type, content):
        """发送消息"""
        msg = {
            'from': from_agent,
            'to': to_agent,
            'type': message_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.messages.append(msg)
        return msg
    
    def broadcast(self, from_agent, message_type, content):
        """广播消息"""
        for agent_id in self.get_all_agents():
            if agent_id != from_agent:
                self.send_message(from_agent, agent_id, message_type, content)
    
    def ask_for_help(self, agent_id, task, context):
        """请求协助"""
        return self.send_message(
            agent_id, 'orchestrator', 'help_request',
            {'task': task, 'context': context}
        )
