#!/usr/bin/env python3
"""
Generate Draw.io mind map for observability design
使用draw.io原生脑图格式，包含三个主分支：日志、监控、报警
"""
import argparse
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import subprocess
from datetime import datetime


def get_git_branch():
    """Get current git branch name"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
        # Sanitize branch name for filename (remove invalid characters)
        branch = branch.replace('/', '-').replace('\\', '-')
        return branch
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If git command fails or not in a git repo, return default
        return 'default'


def create_mindmap_xml(data):
    """
    Create Draw.io native mind map XML structure

    data format:
    {
        "logging": {
            "Controller层": [
                "[member_index_v6] 请求开始, username=",
                "[member_index_v6] 请求成功, username="
            ],
            ...
        },
        "monitoring": {
            "接口层": [
                "member_index_v6_page_qps",
                "member_index_v6_page_error"
            ],
            ...
        },
        "alerting": {
            "接口层": ["错误率>5%", "耗时P99>3s"],
            ...
        }
    }
    """

    # Create root mxfile element
    mxfile = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': datetime.now().isoformat(),
        'agent': 'Claude Code Observability Design',
        'version': '24.7.17',
        'type': 'device'
    })

    # Create diagram element
    diagram = ET.SubElement(mxfile, 'diagram', {
        'id': 'observability-mindmap',
        'name': '可观测性设计脑图'
    })

    # Create mxGraphModel for mind map
    graph_model = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': '2000',
        'dy': '1500',
        'grid': '1',
        'gridSize': '10',
        'guides': '1',
        'tooltips': '1',
        'connect': '1',
        'arrows': '1',
        'fold': '1',
        'page': '1',
        'pageScale': '1',
        'pageWidth': '2000',
        'pageHeight': '1500',
        'math': '0',
        'shadow': '0'
    })

    # Create root and parent cells
    root = ET.SubElement(graph_model, 'root')
    ET.SubElement(root, 'mxCell', {'id': '0'})
    ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})

    cell_id = 2

    # Center position for root node
    center_x = 1000
    center_y = 750

    # Create root node (可观测性设计) - using mind map style
    root_node = ET.SubElement(root, 'mxCell', {
        'id': str(cell_id),
        'value': '可观测性设计',
        'style': 'ellipse;whiteSpace=wrap;html=1;align=center;newEdgeStyle={"edgeStyle":"entityRelationEdgeStyle","startArrow":"none","endArrow":"none","segment":10,"curved":1,"sourcePerimeterSpacing":0,"targetPerimeterSpacing":0};treeFolding=1;treeMoving=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=18;fontStyle=1;',
        'vertex': '1',
        'parent': '1'
    })
    ET.SubElement(root_node, 'mxGeometry', {
        'x': str(center_x - 100),
        'y': str(center_y - 50),
        'width': '200',
        'height': '100',
        'as': 'geometry'
    })
    root_node_id = cell_id
    cell_id += 1

    # Branch configurations with positions
    branch_configs = [
        {
            'name': '日志',
            'key': 'logging',
            'x': center_x - 600,
            'y': center_y - 400,
            'color': '#fff2cc',
            'stroke': '#d6b656'
        },
        {
            'name': '监控',
            'key': 'monitoring',
            'x': center_x,
            'y': center_y - 500,
            'color': '#d5e8d4',
            'stroke': '#82b366'
        },
        {
            'name': '报警',
            'key': 'alerting',
            'x': center_x + 600,
            'y': center_y - 400,
            'color': '#f8cecc',
            'stroke': '#b85450'
        }
    ]

    for branch_config in branch_configs:
        data_key = branch_config['key']
        if data_key not in data:
            continue

        # Create main branch node
        branch_node = ET.SubElement(root, 'mxCell', {
            'id': str(cell_id),
            'value': branch_config['name'],
            'style': f'whiteSpace=wrap;html=1;rounded=1;arcSize=50;align=center;verticalAlign=middle;strokeWidth=1;autosize=1;spacing=4;treeFolding=1;treeMoving=1;newEdgeStyle={{"edgeStyle":"entityRelationEdgeStyle","startArrow":"none","endArrow":"none","segment":10,"curved":1,"sourcePerimeterSpacing":0,"targetPerimeterSpacing":0}};fillColor={branch_config["color"]};strokeColor={branch_config["stroke"]};fontSize=16;fontStyle=1;',
            'vertex': '1',
            'parent': '1'
        })
        ET.SubElement(branch_node, 'mxGeometry', {
            'x': str(branch_config['x']),
            'y': str(branch_config['y']),
            'width': '120',
            'height': '60',
            'as': 'geometry'
        })
        branch_node_id = cell_id
        cell_id += 1

        # Create edge from root to branch (mind map style)
        edge = ET.SubElement(root, 'mxCell', {
            'id': str(cell_id),
            'value': '',
            'style': 'edgeStyle=entityRelationEdgeStyle;startArrow=none;endArrow=none;segment=10;curved=1;sourcePerimeterSpacing=0;targetPerimeterSpacing=0;rounded=0;strokeWidth=2;',
            'edge': '1',
            'parent': '1',
            'source': str(root_node_id),
            'target': str(branch_node_id)
        })
        ET.SubElement(edge, 'mxGeometry', {
            'relative': '1',
            'as': 'geometry'
        })
        cell_id += 1

        # Add modules and items for this branch
        modules = data[data_key]
        module_y_offset = 0

        for module_name, items in modules.items():
            # Create module node
            module_x = branch_config['x'] + 200
            module_y = branch_config['y'] + module_y_offset

            module_node = ET.SubElement(root, 'mxCell', {
                'id': str(cell_id),
                'value': module_name,
                'style': f'whiteSpace=wrap;html=1;rounded=1;arcSize=50;align=center;verticalAlign=middle;strokeWidth=1;autosize=1;spacing=4;treeFolding=1;treeMoving=1;newEdgeStyle={{"edgeStyle":"entityRelationEdgeStyle","startArrow":"none","endArrow":"none","segment":10,"curved":1,"sourcePerimeterSpacing":0,"targetPerimeterSpacing":0}};fillColor={branch_config["color"]};strokeColor={branch_config["stroke"]};fontSize=14;fontStyle=1;',
                'vertex': '1',
                'parent': '1'
            })
            ET.SubElement(module_node, 'mxGeometry', {
                'x': str(module_x),
                'y': str(module_y),
                'width': '120',
                'height': '50',
                'as': 'geometry'
            })
            module_node_id = cell_id
            cell_id += 1

            # Create edge from branch to module
            edge = ET.SubElement(root, 'mxCell', {
                'id': str(cell_id),
                'value': '',
                'style': 'edgeStyle=entityRelationEdgeStyle;startArrow=none;endArrow=none;segment=10;curved=1;sourcePerimeterSpacing=0;targetPerimeterSpacing=0;rounded=0;',
                'edge': '1',
                'parent': '1',
                'source': str(branch_node_id),
                'target': str(module_node_id)
            })
            ET.SubElement(edge, 'mxGeometry', {
                'relative': '1',
                'as': 'geometry'
            })
            cell_id += 1

            # Add items for this module
            item_y_offset = 0
            for item in items:
                item_x = module_x + 200
                item_y = module_y + item_y_offset

                # Create item node
                item_node = ET.SubElement(root, 'mxCell', {
                    'id': str(cell_id),
                    'value': item,
                    'style': f'whiteSpace=wrap;html=1;rounded=1;arcSize=50;align=center;verticalAlign=middle;strokeWidth=1;autosize=1;spacing=4;treeFolding=1;treeMoving=1;newEdgeStyle={{"edgeStyle":"entityRelationEdgeStyle","startArrow":"none","endArrow":"none","segment":10,"curved":1,"sourcePerimeterSpacing":0,"targetPerimeterSpacing":0}};fillColor={branch_config["color"]};strokeColor={branch_config["stroke"]};fontSize=12;',
                    'vertex': '1',
                    'parent': '1'
                })
                ET.SubElement(item_node, 'mxGeometry', {
                    'x': str(item_x),
                    'y': str(item_y),
                    'width': '200',
                    'height': '40',
                    'as': 'geometry'
                })
                item_node_id = cell_id
                cell_id += 1

                # Create edge from module to item
                edge = ET.SubElement(root, 'mxCell', {
                    'id': str(cell_id),
                    'value': '',
                    'style': 'edgeStyle=entityRelationEdgeStyle;startArrow=none;endArrow=none;segment=10;curved=1;sourcePerimeterSpacing=0;targetPerimeterSpacing=0;rounded=0;',
                    'edge': '1',
                    'parent': '1',
                    'source': str(module_node_id),
                    'target': str(item_node_id)
                })
                ET.SubElement(edge, 'mxGeometry', {
                    'relative': '1',
                    'as': 'geometry'
                })
                cell_id += 1

                item_y_offset += 60

            module_y_offset += max(len(items) * 60, 80)

    return mxfile


def prettify_xml(elem):
    """Return a pretty-printed XML string"""
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')


def main():
    parser = argparse.ArgumentParser(description='Generate Draw.io mind map for observability design')
    parser.add_argument('--output', default=None, help='Output file path (optional, will use branch name if not specified)')
    parser.add_argument('--data', required=True, help='JSON file path or JSON string containing the mind map data')

    args = parser.parse_args()

    # Get git branch name
    branch_name = get_git_branch()

    # Determine output filename
    if args.output:
        # If user specified output, prepend branch name
        output_file = f'{branch_name}-{args.output}'
    else:
        # Use default naming with branch name
        output_file = f'{branch_name}-observability-design.drawio'

    # Parse input data
    try:
        # Try to load as file first
        with open(args.data, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        # If not a file, try to parse as JSON string
        data = json.loads(args.data)

    # Generate XML
    mxfile = create_mindmap_xml(data)

    # Write to file
    xml_string = prettify_xml(mxfile)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_string)

    print(f'Branch: {branch_name}')
    print(f'Output: {output_file}')

    # Count statistics
    log_count = sum(len(items) for items in data.get('logging', {}).values())
    metric_count = sum(len(items) for items in data.get('monitoring', {}).values())
    alert_count = sum(len(items) for items in data.get('alerting', {}).values())

    print(f'  - Logging items: {log_count}')
    print(f'  - Monitoring metrics: {metric_count}')
    print(f'  - Alerting rules: {alert_count}')


if __name__ == '__main__':
    main()
