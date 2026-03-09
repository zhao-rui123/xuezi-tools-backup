# 智能任务预估模块
# 基于历史数据预测任务时间和风险

class TaskEstimator:
    """任务预估器"""
    
    def __init__(self):
        self.history_file = SUITE_DIR / "task_history.json"
        self.history = self.load_history()
    
    def estimate_task(self, task_type, complexity):
        """预估任务"""
        # 基于历史数据
        similar_tasks = [
            h for h in self.history
            if h['type'] == task_type
        ]
        
        if similar_tasks:
            avg_duration = sum(h['duration'] for h in similar_tasks) / len(similar_tasks)
            estimated_hours = avg_duration * complexity
        else:
            # 默认估算
            base_hours = {'ui': 4, 'backend': 6, 'ai': 12, 'data': 8}
            estimated_hours = base_hours.get(task_type, 6) * complexity
        
        # 风险评估
        risk_level = self.assess_risk(task_type, complexity)
        
        return {
            'estimated_hours': round(estimated_hours, 1),
            'risk_level': risk_level,
            'confidence': 'high' if similar_tasks else 'medium'
        }
    
    def assess_risk(self, task_type, complexity):
        """风险评估"""
        if complexity > 3:
            return 'high'
        elif task_type in ['ai', 'security']:
            return 'medium'
        return 'low'
