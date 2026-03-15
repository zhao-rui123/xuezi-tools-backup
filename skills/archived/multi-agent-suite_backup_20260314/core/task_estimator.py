# 智能任务预估模块
# 基于历史数据预测任务时间和风险

from datetime import datetime
from pathlib import Path
import json

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()

class TaskEstimator:
    """任务预估器"""
    
    def __init__(self):
        self.history_file = SUITE_DIR / "task_history.json"
        self.history = self.load_history()
    
    def load_history(self):
        """加载历史数据"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_history(self):
        """保存历史数据"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def record_completion(self, task_type: str, actual_hours: float, success: bool = True):
        """记录任务完成信息"""
        self.history.append({
            'type': task_type,
            'duration': actual_hours,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
        self.save_history()
    
    def estimate_task(self, task_type: str, complexity: float = 1.0) -> dict:
        """预估任务"""
        similar_tasks = [
            h for h in self.history
            if h.get('type') == task_type and h.get('success', True)
        ]
        
        if similar_tasks:
            avg_duration = sum(h['duration'] for h in similar_tasks) / len(similar_tasks)
            estimated_hours = avg_duration * complexity
        else:
            base_hours = {'ui': 4, 'backend': 6, 'ai': 12, 'data': 8, 'fullstack': 8, 'security': 5, 'performance': 4}
            estimated_hours = base_hours.get(task_type, 6) * complexity
        
        risk_level = self.assess_risk(task_type, complexity)
        
        return {
            'estimated_hours': round(estimated_hours, 1),
            'risk_level': risk_level,
            'confidence': 'high' if similar_tasks else 'medium',
            'based_on_records': len(similar_tasks)
        }
    
    def assess_risk(self, task_type: str, complexity: float) -> str:
        """风险评估"""
        if complexity > 3:
            return 'high'
        elif task_type in ['ai', 'security'] or complexity > 2:
            return 'medium'
        return 'low'
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        if not self.history:
            return {'total_tasks': 0, 'avg_duration': 0, 'success_rate': 0}
        
        total = len(self.history)
        successful = sum(1 for h in self.history if h.get('success', True))
        avg_duration = sum(h.get('duration', 0) for h in self.history) / total if total > 0 else 0
        
        return {
            'total_tasks': total,
            'successful_tasks': successful,
            'success_rate': round(successful / total * 100, 1) if total > 0 else 0,
            'avg_duration': round(avg_duration, 1)
        }
