#!/usr/bin/env python3
"""
知识图谱 - 构建知识图谱，实体关系提取，图谱可视化
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from config import get_config

logger = logging.getLogger('memory-suite')


class KnowledgeGraph:
    """知识图谱"""

    def __init__(self, config=None):
        self._config = config or get_config()
        self._knowledge_dir = self._config.get_path('knowledge')
        self._graph_dir = self._knowledge_dir / "graph"
        self._graph_file = self._graph_dir / "graph.json"
        self._entries_file = self._knowledge_dir / "entries.json"

        self._graph_dir.mkdir(parents=True, exist_ok=True)

    def build(self) -> Optional[Dict[str, Any]]:
        """
        构建知识图谱

        Returns:
            图谱构建结果
        """
        logger.info("构建知识图谱...")

        try:
            if not self._entries_file.exists():
                logger.warning("知识条目文件不存在")
                return {"entities": 0, "relations": 0, "graph_path": str(self._graph_file)}

            with open(self._entries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            entries = data.get("entries", [])

            entities = set()
            relations = []

            for entry in entries:
                category = entry.get("category")
                if category:
                    entities.add(f"category:{category}")

                for tag in entry.get("tags", []):
                    entities.add(f"tag:{tag}")

                entry_id = entry.get("id", "")
                if entry_id:
                    entities.add(f"entry:{entry_id}")

                    if category:
                        relations.append({
                            "from": f"entry:{entry_id}",
                            "to": f"category:{category}",
                            "type": "belongs_to"
                        })

                    for tag in entry.get("tags", []):
                        relations.append({
                            "from": f"entry:{entry_id}",
                            "to": f"tag:{tag}",
                            "type": "tagged_with"
                        })

            category_entities = [e for e in entities if e.startswith("category:")]
            tag_entities = [e for e in entities if e.startswith("tag:")]
            entry_entities = [e for e in entities if e.startswith("entry:")]

            graph = {
                "built_at": datetime.now().isoformat(),
                "entities": list(entities),
                "relations": relations,
                "stats": {
                    "total_entities": len(entities),
                    "total_relations": len(relations),
                    "categories": len(category_entities),
                    "tags": len(tag_entities),
                    "entries": len(entry_entities)
                }
            }

            with open(self._graph_file, 'w', encoding='utf-8') as f:
                json.dump(graph, f, ensure_ascii=False, indent=2)

            result = {
                "entities": len(entities),
                "relations": len(relations),
                "graph_path": str(self._graph_file)
            }

            logger.info(f"知识图谱构建完成：{len(entities)} 实体，{len(relations)} 关系")
            return result

        except PermissionError as e:
            logger.error(f"知识图谱构建失败 - 权限不足：{e}")
            return None
        except Exception as e:
            logger.error(f"知识图谱构建失败：{e}")
            return None

    def visualize(self, output_format: str = "json") -> Optional[Dict[str, Any]]:
        """
        可视化知识图谱

        Args:
            output_format: 输出格式 (json/dot)

        Returns:
            可视化结果
        """
        if not self._graph_file.exists():
            self.build()

        try:
            with open(self._graph_file, 'r', encoding='utf-8') as f:
                graph = json.load(f)

            output_path = self._graph_dir / f"graph_viz.{output_format}"

            if output_format == "dot":
                dot_content = "digraph KnowledgeGraph {\n"
                dot_content += '  rankdir=LR;\n'
                dot_content += '  node [shape=box, style=rounded];\n'

                for entity in graph.get("entities", []):
                    entity_clean = entity.replace(":", "_")
                    dot_content += f'  "{entity_clean}" [label="{entity}"];\n'

                for rel in graph.get("relations", []):
                    from_clean = rel["from"].replace(":", "_")
                    to_clean = rel["to"].replace(":", "_")
                    dot_content += f'  "{from_clean}" -> "{to_clean}" [label="{rel["type"]}"];\n'

                dot_content += "}"

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(dot_content)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(graph, f, ensure_ascii=False, indent=2)

            return {
                "nodes": len(graph.get("entities", [])),
                "edges": len(graph.get("relations", [])),
                "output_path": str(output_path)
            }

        except Exception as e:
            logger.error(f"图谱可视化失败：{e}")
            return None

    def get_graph_data(self) -> Optional[Dict[str, Any]]:
        """获取图谱数据"""
        try:
            if not self._graph_file.exists():
                self.build()

            with open(self._graph_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"获取图谱数据失败：{e}")
            return None

    def get_related_entries(self, entry_id: str) -> List[str]:
        """获取相关条目"""
        try:
            graph = self.get_graph_data()
            if not graph:
                return []

            related = []
            for rel in graph.get("relations", []):
                if rel["from"] == f"entry:{entry_id}":
                    related.append(rel["to"])
                elif rel["to"] == f"entry:{entry_id}":
                    related.append(rel["from"])

            return related

        except Exception:
            return []
