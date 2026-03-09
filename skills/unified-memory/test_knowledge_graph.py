#!/usr/bin/env python3
"""
知识图谱模块测试脚本
演示所有核心功能
"""

import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/unified-memory')

from knowledge_graph import KnowledgeGraph, build_graph_from_memories, ENTITY_TYPES, RELATION_TYPES
from pathlib import Path

def test_entity_extraction():
    """测试实体提取功能"""
    print("\n" + "="*60)
    print("测试 1: 实体提取 (extract_entities)")
    print("="*60)
    
    kg = KnowledgeGraph()
    
    # 测试文本
    test_text = """
    今天完成了小龙虾之家项目的开发，使用 Python 和 JavaScript 技术。
    项目部署在腾讯云服务器上，使用 Nginx 作为Web服务器。
    雪子负责整个项目的架构设计和技术选型。
    使用了 OpenClaw 框架和 GitHub 进行版本控制。
    相关的技能包包括 stock-analysis 和 unified-memory。
    主要文件包括 app.py、index.html 和 style.css。
    涉及的概念有储能、光伏、PCS 等。
    中矿资源和赣锋锂业是重要的合作伙伴。
    """
    
    entities = kg.extract_entities(test_text, "test.md")
    
    print(f"✅ 从测试文本中提取了 {len(entities)} 个实体:")
    
    # 按类型分组显示
    by_type = {}
    for e in entities:
        by_type.setdefault(e['type_name'], []).append(e)
    
    for type_name, type_entities in by_type.items():
        print(f"\n  【{type_name}】({len(type_entities)}个):")
        for e in type_entities[:5]:  # 每类最多显示5个
            print(f"    - {e['name']}")
    
    return entities

def test_relation_building(entities):
    """测试关系建立功能"""
    print("\n" + "="*60)
    print("测试 2: 关系建立 (build_relations)")
    print("="*60)
    
    kg = KnowledgeGraph()
    
    test_text = """
    小龙虾之家项目使用 Python 开发，部署在腾讯云服务器上。
    雪子开发了 stock-analysis 技能包，使用 GitHub 进行版本控制。
    项目包含 app.py、index.html 等多个文件。
    储能电站项目依赖于 PCS 和 BMS 技术。
    中矿资源和赣锋锂业使用储能技术。
    """
    
    # 重新提取实体
    entities = kg.extract_entities(test_text, "test.md")
    
    # 建立关系
    relations = kg.build_relations(entities, test_text)
    
    print(f"✅ 建立了 {len(relations)} 个关系:")
    for r in relations[:10]:  # 最多显示10个
        target = r.get('target_name') or r.get('target_id', '?')
        print(f"    - {r['source_name']} → {target} ({r['relation_name']}, 置信度: {r.get('confidence', 0.5)})")
    
    return relations

def test_graph_building():
    """测试从记忆文件构建图谱"""
    print("\n" + "="*60)
    print("测试 3: 从记忆文件构建图谱 (build_graph_from_memories)")
    print("="*60)
    
    memory_dir = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
    kg = build_graph_from_memories(memory_dir, "*.md")
    
    stats = kg.get_stats()
    print(f"\n📊 构建结果:")
    print(f"   实体总数: {stats['total_entities']}")
    print(f"   关系总数: {stats['total_relations']}")
    print(f"\n📊 实体类型分布:")
    for t, c in stats['entity_types'].items():
        print(f"   {t}: {c}")
    
    return kg

def test_graph_query(kg):
    """测试图谱查询功能"""
    print("\n" + "="*60)
    print("测试 4: 图谱查询 (query_graph)")
    print("="*60)
    
    # 测试不同查询
    queries = [
        ("储能", None, 1),
        ("openclaw", None, 2),
        (None, "technology", 1),
    ]
    
    for query_name, query_type, depth in queries:
        print(f"\n🔍 查询: name={query_name}, type={query_type}, depth={depth}")
        results = kg.query_graph(
            entity_name=query_name,
            entity_type=query_type,
            depth=depth
        )
        print(f"   找到 {len(results['entities'])} 个实体")
        for e in results['entities'][:5]:
            print(f"     - {e['name']} ({e['type_name']})")

def test_graph_extension(kg):
    """测试图谱扩展功能"""
    print("\n" + "="*60)
    print("测试 5: 图谱扩展 (extend_graph)")
    print("="*60)
    
    new_memory = """
    今天开发了新的智能分析系统，使用 Python 和 React 技术。
    系统部署在阿里云服务器上，使用 Docker 进行容器化部署。
    实现了数据分析功能和可视化图表展示。
    相关技术栈包括 MySQL 数据库和 Redis 缓存。
    """
    
    result = kg.extend_graph(new_memory, "new_memory.md")
    
    print(f"✅ 图谱扩展结果:")
    print(f"   新增实体: {result['new_entities']}")
    print(f"   新增关系: {result['new_relations']}")
    print(f"   实体总数: {result['total_entities']}")
    print(f"   关系总数: {result['total_relations']}")

def test_simple_visualization(kg):
    """测试简化可视化功能"""
    print("\n" + "="*60)
    print("测试 6: 图谱可视化 (visualize_graph)")
    print("="*60)
    
    output_file = "/Users/zhaoruicn/.openclaw/workspace/memory/knowledge_graph/knowledge_graph.html"
    
    # 检查是否有 pyvis
    try:
        from pyvis.network import Network
        has_pyvis = True
    except ImportError:
        has_pyvis = False
    
    if has_pyvis:
        try:
            result = kg.visualize_graph(output_file)
            print(f"✅ 可视化已生成: {result}")
        except Exception as e:
            print(f"⚠️  可视化生成失败: {e}")
    else:
        # 生成简化版可视化
        print("⚠️  pyvis 未安装，生成简化版可视化...")
        generate_simple_visualization(kg, output_file)
        print(f"✅ 简化可视化已生成: {output_file}")

def generate_simple_visualization(kg, output_file):
    """生成简化的HTML可视化（不依赖 pyvis）"""
    
    # 类型颜色
    type_colors = {
        'project': '#e74c3c',
        'technology': '#3498db',
        'person': '#2ecc71',
        'company': '#f39c12',
        'skill': '#9b59b6',
        'file': '#1abc9c',
        'concept': '#e91e63',
        'tool': '#607d8b'
    }
    
    # 构建节点和边数据
    nodes = []
    for entity_id, entity in kg.entities.items():
        entity_type = entity.get('type', 'unknown')
        color = type_colors.get(entity_type, '#95a5a6')
        nodes.append({
            'id': entity_id,
            'label': entity['name'],
            'type': entity['type_name'],
            'color': color,
            'source': entity.get('source', '')
        })
    
    edges = []
    for source, target, data in kg.graph.edges(data=True):
        edges.append({
            'from': source,
            'to': target,
            'label': data.get('relation_name', '关联')
        })
    
    # 生成HTML
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>统一记忆系统 - 知识图谱</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; background: #1a1a2e; font-family: Arial, sans-serif; }}
        #mynetwork {{ width: 100%; height: 100vh; }}
        .legend {{
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 8px;
            color: white;
        }}
        .legend-item {{ display: flex; align-items: center; margin: 5px 0; }}
        .legend-color {{ width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }}
        .stats {{
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 8px;
            color: white;
            min-width: 150px;
        }}
        .search-box {{
            position: fixed;
            bottom: 10px;
            left: 10px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 8px;
        }}
        .search-box input {{
            width: 200px;
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #555;
            background: #333;
            color: #fff;
        }}
        .search-box button {{
            margin-top: 8px;
            padding: 6px 12px;
            background: #3498db;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div id="mynetwork"></div>
    
    <div class="legend">
        <h4>实体类型</h4>
        {''.join(f'<div class="legend-item"><span class="legend-color" style="background: {color};"></span><span>{ENTITY_TYPES.get(t, t)}</span></div>' for t, color in type_colors.items())}
    </div>
    
    <div class="stats">
        <h4>统计信息</h4>
        <p>实体总数: {len(nodes)}</p>
        <p>关系总数: {len(edges)}</p>
    </div>
    
    <div class="search-box">
        <h4>搜索实体</h4>
        <input type="text" id="searchInput" placeholder="输入实体名称...">
        <button onclick="searchNode()">搜索</button>
    </div>
    
    <script type="text/javascript">
        var nodes = new vis.DataSet({nodes});
        var edges = new vis.DataSet({edges});
        
        var container = document.getElementById('mynetwork');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            nodes: {{
                shape: 'dot',
                size: 20,
                font: {{ size: 14, color: '#ffffff' }},
                borderWidth: 2
            }},
            edges: {{
                width: 2,
                color: {{ color: '#5d6d7e' }},
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
                font: {{ color: '#cccccc', size: 12 }}
            }},
            physics: {{
                stabilization: {{ enabled: true, iterations: 1000 }},
                barnesHut: {{
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 150,
                    springConstant: 0.04,
                    damping: 0.09
                }}
            }}
        }};
        
        var network = new vis.Network(container, data, options);
        
        function searchNode() {{
            var query = document.getElementById('searchInput').value.toLowerCase();
            var found = nodes.get({{
                filter: function(item) {{
                    return item.label.toLowerCase().includes(query);
                }}
            }});
            if (found.length > 0) {{
                network.selectNodes([found[0].id]);
                network.focus(found[0].id, {{scale: 1.5, animation: true}});
            }} else {{
                alert('未找到匹配的实体');
            }}
        }}
        
        document.getElementById('searchInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') searchNode();
        }});
    </script>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    """运行所有测试"""
    print("\n" + "🧠 "*30)
    print("知识图谱构建模块 - 完整测试")
    print("🧠 "*30)
    
    # 测试1: 实体提取
    entities = test_entity_extraction()
    
    # 测试2: 关系建立
    relations = test_relation_building(entities)
    
    # 测试3: 从记忆文件构建图谱
    kg = test_graph_building()
    
    # 测试4: 图谱查询
    test_graph_query(kg)
    
    # 测试5: 图谱扩展
    test_graph_extension(kg)
    
    # 测试6: 可视化
    test_simple_visualization(kg)
    
    print("\n" + "="*60)
    print("✅ 所有测试完成!")
    print("="*60)
    print(f"\n📁 文件位置:")
    print(f"   知识图谱模块: ~/.openclaw/workspace/skills/unified-memory/knowledge_graph.py")
    print(f"   图谱数据: ~/.openclaw/workspace/memory/knowledge_graph/graph_data.json")
    print(f"   可视化页面: ~/.openclaw/workspace/memory/knowledge_graph/knowledge_graph.html")

if __name__ == '__main__':
    main()
