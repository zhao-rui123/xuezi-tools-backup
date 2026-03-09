#!/usr/bin/env python3
"""
Enhanced Memory - 简化版增强记忆系统
基于 LanceDB Pro 思路，使用本地文件存储
"""

import json
import os
import re
import hashlib
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# 尝试导入可选依赖
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False

# 默认配置
DEFAULT_CONFIG = {
    "db_path": "~/.openclaw/memory/enhanced",
    "embedding_model": "local",  # local 或 openai
    "auto_decay": True,
    "default_scope": "global",
    "max_entries": 10000,
    "decay_half_life": 60,  # 天
    "recency_weight": 0.1,
}

class EnhancedMemory:
    """增强记忆管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.db_path = Path(self.config["db_path"]).expanduser()
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # 加载或创建索引
        self.index_file = self.db_path / "index.json"
        self.memories = self._load_index()
        
        # 词频索引（用于 BM25）
        self.term_index = self._build_term_index()
    
    def _load_index(self) -> Dict:
        """加载记忆索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"memories": {}, "next_id": 1}
    
    def _save_index(self):
        """保存记忆索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)
    
    def _build_term_index(self) -> Dict:
        """构建词频索引"""
        index = {}
        for mem_id, mem in self.memories.get("memories", {}).items():
            terms = self._tokenize(mem["text"])
            for term in terms:
                if term not in index:
                    index[term] = []
                index[term].append(mem_id)
        return index
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        # 清理文本
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        if HAS_JIEBA:
            # 使用 jieba 中文分词
            return list(jieba.cut_for_search(text))
        else:
            # 简单分词
            return text.split()
    
    def _compute_vector(self, text: str) -> List[float]:
        """计算文本向量（固定维度）"""
        dim = 128  # 固定维度
        vector = [0.0] * dim
        
        # 使用字符级别的哈希
        for i, char in enumerate(text):
            idx = hash(char) % dim
            vector[idx] += 1
        
        # 归一化
        norm = math.sqrt(sum(x**2 for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]
        
        return vector
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """计算余弦相似度"""
        if not HAS_NUMPY:
            # 纯 Python 实现
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(x**2 for x in v1))
            norm2 = math.sqrt(sum(x**2 for x in v2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)
        else:
            # NumPy 加速
            return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    
    def _bm25_score(self, query: str, text: str, k1: float = 1.5, b: float = 0.75) -> float:
        """计算 BM25 分数"""
        query_terms = self._tokenize(query)
        doc_terms = self._tokenize(text)
        
        if not doc_terms:
            return 0.0
        
        doc_len = len(doc_terms)
        avg_doc_len = 50  # 假设平均长度
        
        score = 0.0
        for term in query_terms:
            # 文档频率
            df = len(self.term_index.get(term, []))
            idf = math.log((len(self.memories["memories"]) - df + 0.5) / (df + 0.5) + 1)
            
            # 词频
            tf = doc_terms.count(term)
            
            # BM25 公式
            score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len))
        
        return score
    
    def _time_decay(self, timestamp: int) -> float:
        """计算时间衰减因子"""
        age_days = (datetime.now().timestamp() - timestamp / 1000) / 86400
        half_life = self.config["decay_half_life"]
        return 0.5 + 0.5 * math.exp(-age_days / half_life)
    
    def _should_filter(self, text: str) -> bool:
        """噪声过滤"""
        filters = [
            r"^i don't have",
            r"^我没有",
            r"^hi$|^hello$|^你好$",
            r"^do you remember",
            r"^你记得",
            r"^heartbeat",
        ]
        for pattern in filters:
            if re.search(pattern, text.lower()):
                return True
        return False
    
    def store(self, text: str, category: str = "fact", importance: float = 0.5,
              scope: str = "global", metadata: Optional[Dict] = None) -> str:
        """存储记忆"""
        
        # 噪声过滤
        if self._should_filter(text):
            return ""
        
        # 生成 ID
        mem_id = f"mem_{self.memories['next_id']:08d}"
        self.memories['next_id'] += 1
        
        # 计算向量
        vector = self._compute_vector(text)
        
        # 构建记忆对象
        memory = {
            "id": mem_id,
            "text": text,
            "category": category,
            "importance": importance,
            "scope": scope,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "vector": vector,
            "metadata": metadata or {}
        }
        
        # 保存
        self.memories["memories"][mem_id] = memory
        
        # 更新词频索引
        terms = self._tokenize(text)
        for term in terms:
            if term not in self.term_index:
                self.term_index[term] = []
            if mem_id not in self.term_index[term]:
                self.term_index[term].append(mem_id)
        
        # 持久化
        self._save_index()
        
        return mem_id
    
    def recall(self, query: str, scope: Optional[str] = None, 
               top_k: int = 5, min_score: float = 0.1) -> List[Dict]:
        """检索记忆（混合搜索）"""
        
        query_vector = self._compute_vector(query)
        scope_filter = scope or self.config["default_scope"]
        
        candidates = []
        
        for mem_id, mem in self.memories["memories"].items():
            # 作用域过滤
            if mem["scope"] != scope_filter and mem["scope"] != "global":
                continue
            
            # 向量相似度
            vector_score = self._cosine_similarity(query_vector, mem["vector"])
            
            # BM25 分数
            bm25_score = self._bm25_score(query, mem["text"])
            
            # 融合（加权）
            combined_score = 0.7 * vector_score + 0.3 * min(bm25_score / 10, 1.0)
            
            # 时间衰减
            decay = self._time_decay(mem["timestamp"])
            
            # 重要性加权
            importance_weight = 0.7 + 0.3 * mem["importance"]
            
            # 最终得分
            final_score = combined_score * decay * importance_weight
            
            if final_score >= min_score:
                candidates.append({
                    "id": mem_id,
                    "text": mem["text"],
                    "category": mem["category"],
                    "importance": mem["importance"],
                    "scope": mem["scope"],
                    "timestamp": mem["timestamp"],
                    "score": final_score,
                    "vector_score": vector_score,
                    "bm25_score": bm25_score
                })
        
        # 排序并返回前 k 个
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:top_k]
    
    def delete(self, mem_id: str) -> bool:
        """删除记忆"""
        if mem_id in self.memories["memories"]:
            mem = self.memories["memories"].pop(mem_id)
            
            # 从词频索引中移除
            terms = self._tokenize(mem["text"])
            for term in terms:
                if term in self.term_index and mem_id in self.term_index[term]:
                    self.term_index[term].remove(mem_id)
            
            self._save_index()
            return True
        return False
    
    def stats(self) -> Dict:
        """统计信息"""
        memories = self.memories["memories"]
        return {
            "total": len(memories),
            "by_category": {},
            "by_scope": {},
            "term_index_size": len(self.term_index)
        }

# 全局实例
_memory_instance = None

def get_memory() -> EnhancedMemory:
    """获取全局记忆实例"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = EnhancedMemory()
    return _memory_instance

# 便捷函数
def store_memory(text: str, **kwargs) -> str:
    """存储记忆"""
    return get_memory().store(text, **kwargs)

def recall_memory(query: str, **kwargs) -> List[Dict]:
    """检索记忆"""
    return get_memory().recall(query, **kwargs)

def delete_memory(mem_id: str) -> bool:
    """删除记忆"""
    return get_memory().delete(mem_id)

def memory_stats() -> Dict:
    """记忆统计"""
    return get_memory().stats()

if __name__ == "__main__":
    # 简单测试
    mem = EnhancedMemory()
    
    # 存储测试
    id1 = mem.store("用户喜欢 Python 编程", category="preference", importance=0.8)
    id2 = mem.store("用户住在上海", category="fact", importance=0.6)
    id3 = mem.store("用户每天 9 点起床", category="fact", importance=0.5)
    
    print(f"存储记忆: {id1}, {id2}, {id3}")
    
    # 检索测试
    results = mem.recall("用户的编程爱好", top_k=3)
    print("\n检索结果:")
    for r in results:
        print(f"  [{r['score']:.3f}] {r['text']}")
    
    # 统计
    print(f"\n统计: {mem.stats()}")
