---
name: tesseract-ocr
description: Extract text from images using the Tesseract OCR engine. Supports multiple languages including Chinese, English, and more.
---

# Tesseract OCR - Image Text Extraction

Extract text from images using Tesseract OCR engine.

## Installation

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra
```

### macOS
```bash
brew install tesseract tesseract-lang
```

### Verify Installation
```bash
tesseract --version
```

## Quick Start - When User Sends Image

When a user sends an image and asks to read/extract text:

```bash
# Image is saved to: /root/.openclaw/media/inbound/
# Use the exact filename from the system

tesseract /root/.openclaw/media/inbound/FILENAME.jpg stdout -l chi_sim+eng
```

### Example Workflow
1. User sends image via Feishu/WeChat
2. Image auto-saved to `/root/.openclaw/media/inbound/[uuid].jpg`
3. Run OCR command with appropriate language
4. Return extracted text to user

### Common Image Types
- **Screenshots** → Use `-l chi_sim+eng` (中文+英文)
- **Documents** → Use `--psm 6` (统一文本块)
- **Tables** → Use `tsv` 输出格式
- **Low quality** → Preprocess first (see below)

---

## Basic Usage

### Extract Text from Image
```bash
# Basic extraction
tesseract image.png output

# Specify language (English + Chinese)
tesseract image.png output -l eng+chi_sim

# Output to stdout
tesseract image.png stdout -l chi_sim
```

### Supported Languages
| Language | Code |
|----------|------|
| English | eng |
| Chinese (Simplified) | chi_sim |
| Chinese (Traditional) | chi_tra |
| Japanese | jpn |
| Korean | kor |

## Common Use Cases

### 1. Extract Text from Screenshot
```bash
tesseract screenshot.png result -l chi_sim+eng
cat result.txt
```

### 2. Process Multiple Images
```bash
for img in *.png; do
  tesseract "$img" "output_${img%.png}" -l chi_sim
done
```

### 3. Extract with Bounding Box Info
```bash
tesseract image.png output -l chi_sim tsv
cat output.tsv
```

### 4. Extract from PDF (convert first)
```bash
# Convert PDF to images
pdftoppm document.pdf page -png

# OCR each page
for page in page-*.png; do
  tesseract "$page" "text_${page%.png}" -l chi_sim
done
```

## Python Integration

```python
import pytesseract
from PIL import Image

# Open image
img = Image.open('image.png')

# Extract text
text = pytesseract.image_to_string(img, lang='chi_sim+eng')
print(text)

# Get detailed data (with bounding boxes)
data = pytesseract.image_to_data(img, lang='chi_sim', output_type=pytesseract.Output.DICT)
```

## Image Preprocessing Tips

Better OCR results with preprocessing:

```python
import cv2
import numpy as np
from PIL import Image

def preprocess_for_ocr(image_path):
    # Read image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # Threshold (adaptive for varying lighting)
    binary = cv2.adaptiveThreshold(
        denoised, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Save preprocessed
    cv2.imwrite('preprocessed.png', binary)
    return 'preprocessed.png'
```

## Handling Different Image Types

### Tables/Structured Data
```bash
# Use TSV output for table structure
tesseract table.png output -l chi_sim tsv
```

### Handwritten Text
- Tesseract works best with printed text
- For handwriting, consider specialized models

### Low Quality Images
1. Increase resolution (300 DPI minimum)
2. Enhance contrast
3. Remove noise
4. Straighten skewed text

## Common Issues & Solutions

### Issue: Poor Recognition Quality
**Solutions:**
- Ensure 300+ DPI resolution
- Preprocess: grayscale, denoise, threshold
- Try different PSM modes
```bash
tesseract image.png output --psm 6 -l chi_sim
```

### Issue: Mixed Languages
**Solution:**
```bash
tesseract image.png output -l chi_sim+eng+jpn
```

### Issue: Text Orientation
**Solution:**
```bash
# Auto-orient
tesseract image.png output -l chi_sim --psm 1
```

## Page Segmentation Modes (PSM)

| Mode | Description |
|------|-------------|
| 0 | Orientation and script detection only |
| 1 | Automatic page segmentation with OSD |
| 3 | Fully automatic page segmentation (default) |
| 4 | Assume single column of variable text |
| 6 | Assume uniform block of text |
| 7 | Treat as single text line |
| 8 | Treat as single word |
| 11 | Sparse text - find as much text as possible |

## OCR Engine Modes (OEM)

| Mode | Description |
|------|-------------|
| 0 | Legacy engine only |
| 1 | Neural nets LSTM engine only |
| 2 | Legacy + LSTM engines |
| 3 | Default, based on available |

## Advanced Options

```bash
# Specify multiple languages
tesseract image.png output -l chi_sim+eng+jpn

# Output as PDF (with searchable text)
tesseract image.png output pdf

# Output as hOCR (HTML)
tesseract image.png output hocr

# Custom config
tesseract image.png output -c tessedit_char_whitelist=0123456789
```

## Integration with Workflows

### Extract from Electricity Price Documents
```bash
#!/bin/bash
# Process electricity price PDF/image

INPUT=$1
OUTPUT_DIR="extracted_text"
mkdir -p $OUTPUT_DIR

# Convert to image if PDF
if [[ $INPUT == *.pdf ]]; then
    pdftoppm "$INPUT" "$OUTPUT_DIR/page" -png
    IMAGES="$OUTPUT_DIR/page-*.png"
else
    IMAGES="$INPUT"
fi

# OCR each image
for img in $IMAGES; do
    basename=$(basename "$img" .png)
    tesseract "$img" "$OUTPUT_DIR/$basename" -l chi_sim+eng --psm 6
    echo "Extracted: $OUTPUT_DIR/$basename.txt"
done

# Combine results
cat $OUTPUT_DIR/*.txt > $OUTPUT_DIR/combined.txt
echo "Combined output: $OUTPUT_DIR/combined.txt"
```

## Best Practices

1. **Preprocess images** - Better input = better output
2. **Use correct language** - Improves accuracy significantly
3. **Choose right PSM** - Match to document layout
4. **Verify results** - Always check extracted text
5. **Handle errors** - Some characters may need manual correction

## Limitations

- Best with printed text (not handwriting)
- Requires clear, high-resolution images
- May struggle with complex layouts
- Special characters may need post-processing
