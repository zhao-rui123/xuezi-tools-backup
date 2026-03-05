---
name: cad-generator
description: Generate CAD files (DXF format) for 2D drawings, electrical diagrams, and technical schematics. Supports basic shapes, layers, and dimensioning.
---

# CAD Generator - DXF File Creation

Generate 2D CAD drawings in DXF format using Python and ezdxf library.

## Installation

```bash
pip install ezdxf
```

## Quick Start

### Create a Simple DXF File

```python
import ezdxf

# Create new DXF document
doc = ezdxf.new('R2010')  # AutoCAD 2010 format
msp = doc.modelspace()

# Add a line
msp.add_line((0, 0), (100, 100))

# Add a circle
msp.add_circle((50, 50), radius=25)

# Add a rectangle
msp.add_lwpolyline([(0, 0), (100, 0), (100, 50), (0, 50), (0, 0)], close=True)

# Save
doc.saveas('drawing.dxf')
```

## Basic Shapes

### Lines and Polylines
```python
# Single line
msp.add_line(start=(0, 0), end=(100, 0))

# Polyline (connected lines)
points = [(0, 0), (50, 50), (100, 0), (100, 100), (0, 100)]
msp.add_lwpolyline(points, close=True)
```

### Circles and Arcs
```python
# Circle: center (x, y), radius
msp.add_circle((50, 50), radius=25)

# Arc: center, radius, start_angle, end_angle (in degrees)
msp.add_arc((50, 50), radius=25, start_angle=0, end_angle=90)
```

### Rectangles and Polygons
```python
# Rectangle
width, height = 100, 50
msp.add_lwpolyline([
    (0, 0), (width, 0), (width, height), (0, height), (0, 0)
], close=True)

# Regular polygon
def add_polygon(msp, center, radius, sides):
    import math
    points = []
    for i in range(sides):
        angle = 2 * math.pi * i / sides
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    msp.add_lwpolyline(points, close=True)

add_polygon(msp, (50, 50), 30, 6)  # Hexagon
```

## Layers

```python
# Create layers
doc.layers.add("ELECTRICAL", color=1)  # Red
doc.layers.add("DIMENSIONS", color=2)   # Yellow
doc.layers.add("TEXT", color=3)         # Green

# Add entity to specific layer
line = msp.add_line((0, 0), (100, 0))
line.dxf.layer = "ELECTRICAL"
```

## Text and Dimensions

### Add Text
```python
# Simple text
msp.add_text("Hello CAD", height=10, dxfattribs={'insert': (10, 10)})

# Text with style
msp.add_text(
    "Title",
    height=20,
    dxfattribs={
        'insert': (10, 50),
        'style': 'Standard',
        'color': 1
    }
)
```

### Add Dimensions
```python
# Linear dimension
msp.add_linear_dim(
    base=(50, -10),      # Dimension line position
    p1=(0, 0),           # First point
    p2=(100, 0),         # Second point
    angle=0              # Horizontal
).render()
```

## Electrical Diagram Examples

### Simple Circuit Symbol - Resistor
```python
def add_resistor(msp, start, end, width=10):
    """Draw resistor symbol between two points"""
    import math
    
    # Calculate direction
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.sqrt(dx**2 + dy**2)
    angle = math.atan2(dy, dx)
    
    # Resistor body (zigzag)
    zigzag_points = []
    segments = 5
    segment_length = length * 0.6 / segments
    
    # Start connection
    zigzag_points.append((start[0] + dx * 0.2, start[1] + dy * 0.2))
    
    for i in range(segments + 1):
        t = i / segments
        x = start[0] + dx * (0.2 + t * 0.6)
        y = start[1] + dy * (0.2 + t * 0.6)
        
        if i % 2 == 0:
            # Offset perpendicular to line
            offset_x = -dy / length * width
            offset_y = dx / length * width
        else:
            offset_x = dy / length * width
            offset_y = -dx / length * width
        
        if i > 0 and i < segments:
            x += offset_x
            y += offset_y
        
        zigzag_points.append((x, y))
    
    # End connection
    zigzag_points.append((start[0] + dx * 0.8, start[1] + dy * 0.8))
    
    # Draw lines
    msp.add_line(start, (start[0] + dx * 0.2, start[1] + dy * 0.2))
    msp.add_lwpolyline(zigzag_points)
    msp.add_line((start[0] + dx * 0.8, start[1] + dy * 0.8), end)

# Usage
add_resistor(msp, (0, 0), (100, 0))
```

### Battery Symbol
```python
def add_battery(msp, start, end, height=20):
    """Draw battery symbol"""
    import math
    
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    
    # Long line (positive)
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2
    
    # Connection lines
    msp.add_line(start, (mid_x - 10, mid_y))
    msp.add_line((mid_x + 10, mid_y), end)
    
    # Battery plates
    msp.add_line((mid_x - 10, mid_y - height/2), (mid_x - 10, mid_y + height/2))  # Long
    msp.add_line((mid_x + 5, mid_y - height/4), (mid_x + 5, mid_y + height/4))    # Short
    
    # Polarity marks
    msp.add_text("+", height=8, dxfattribs={'insert': (mid_x - 15, mid_y + height/2 + 5)})
    msp.add_text("-", height=8, dxfattribs={'insert': (mid_x + 5, mid_y + height/2 + 5)})

# Usage
add_battery(msp, (0, 50), (100, 50))
```

## Complete Example - Electrical Panel Layout

```python
import ezdxf

def create_electrical_panel(filename):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # Create layers
    doc.layers.add("BORDER", color=7)      # White
    doc.layers.add("COMPONENTS", color=1)  # Red
    doc.layers.add("TEXT", color=3)        # Green
    
    # Panel outline (400x600mm)
    panel_width = 400
    panel_height = 600
    msp.add_lwpolyline([
        (0, 0), (panel_width, 0), 
        (panel_width, panel_height), (0, panel_height), (0, 0)
    ], close=True, dxfattribs={'layer': 'BORDER'})
    
    # Add circuit breakers
    breaker_width = 40
    breaker_height = 80
    spacing = 50
    
    for i in range(6):
        x = 50 + i * spacing
        y = 500
        
        # Breaker rectangle
        msp.add_lwpolyline([
            (x, y), (x + breaker_width, y),
            (x + breaker_width, y - breaker_height), (x, y - breaker_height), (x, y)
        ], close=True, dxfattribs={'layer': 'COMPONENTS'})
        
        # Label
        msp.add_text(f"CB{i+1}", height=10, 
                    dxfattribs={'insert': (x + 5, y - breaker_height - 15), 'layer': 'TEXT'})
    
    # Title
    msp.add_text("Electrical Panel Layout", height=20,
                dxfattribs={'insert': (100, panel_height + 30), 'layer': 'TEXT'})
    
    doc.saveas(filename)
    print(f"Saved: {filename}")

create_electrical_panel('electrical_panel.dxf')
```

## File Operations

### Read Existing DXF
```python
import ezdxf

doc = ezdxf.readfile('existing.dxf')
msp = doc.modelspace()

# List all entities
for entity in msp:
    print(f"{entity.dxftype()}: {entity.dxf.handle}")

# Modify and save
doc.saveas('modified.dxf')
```

### Export to Other Formats
```python
# DXF to SVG (for web display)
# Use: pip install ezdxf[draw]
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.svg import SVGBackend

doc = ezdxf.readfile('drawing.dxf')
msp = doc.modelspace()

backend = SVGBackend()
config = RenderContext(doc)
frontend = Frontend(config, backend)
frontend.draw_layout(msp)

svg_string = backend.get_string()
with open('drawing.svg', 'w') as f:
    f.write(svg_string)
```

## Best Practices

1. **Use layers** - Organize by function (electrical, mechanical, text)
2. **Set units** - Use consistent units (mm or inches)
3. **Add dimensions** - Always include dimensions for manufacturing
4. **Use blocks** - For repeated symbols (create once, use many)
5. **Save versions** - Keep backups of important drawings

## Common Issues

### Issue: File won't open in AutoCAD
- Use older DXF version: `ezdxf.new('R2000')` or `ezdxf.new('R2010')`

### Issue: Text not displaying
- Check text style exists: `doc.styles.new('Standard')`
- Verify font is available on target system

### Issue: Dimensions not showing
- Call `.render()` after creating dimension
- Check dimension style settings
