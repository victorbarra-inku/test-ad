# Fabric.js JSON to Image Converter

A simple Node.js project that converts Fabric.js JSON to image files using node-canvas.

## Prerequisites

### Install Native Dependencies

**macOS:**
```bash
brew install pkg-config cairo pango libpng jpeg giflib librsvg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev
```

**Fedora:**
```bash
sudo dnf install cairo-devel pango-devel libjpeg-turbo-devel giflib-devel librsvg2-devel
```

## Installation

```bash
npm install
```

## Usage

### Command Line

#### Basic Commands

```bash
# Basic usage (saves to output.png, returns dataUrl by default)
node index.js example.json

# Save image locally and get file path
node index.js example.json --return-format filepath
# or short form:
node index.js example.json -r filepath

# With custom output path
node index.js example.json --output result.png -r filepath
# or short form:
node index.js example.json -o result.png -r filepath

# With custom dimensions
node index.js example.json --width 1200 --height 800 -r filepath

# Export as JPEG
node index.js example.json --format jpeg --output result.jpg -r filepath
# or short form:
node index.js example.json -f jpeg -o result.jpg -r filepath

# Using short flags
node index.js example.json -o output.png -w 1000 -h 600 -f png -r filepath
```

#### Return Format Options

The `--return-format` (or `-r`) option controls what the function returns:

```bash
# Get data URL (ready for HTML/CSS embedding)
node index.js example.json -r dataUrl

# Get base64 string (good for JSON APIs)
node index.js example.json -r base64

# Get Buffer (most efficient, raw binary)
node index.js example.json -r buffer

# Get file path (default for saving files)
node index.js example.json -r filepath
```

#### Command Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output file path | `output.png` |
| `--width` | `-w` | Canvas width | `800` |
| `--height` | `-h` | Canvas height | `600` |
| `--format` | `-f` | Image format (`png` or `jpeg`) | `png` |
| `--return-format` | `-r` | Return format (`buffer`, `base64`, `dataUrl`, `filepath`) | `dataUrl` |

### Programmatic Usage

```javascript
import { fabricJsonToImage } from './index.js';

// From JSON object - save file and get file path
const filePath = await fabricJsonToImage({
  version: "6.0.0",
  objects: [
    {
      type: "rect",
      left: 100,
      top: 100,
      width: 200,
      height: 150,
      fill: "#3498db"
    }
  ]
}, {
  outputPath: 'my-image.png',
  width: 800,
  height: 600,
  format: 'png',
  returnFormat: 'filepath'
});

// Get data URL (ready for HTML embedding)
const dataUrl = await fabricJsonToImage('example.json', {
  returnFormat: 'dataUrl'
});
// Result: "data:image/png;base64,iVBORw0KGgo..."

// Get base64 string (for JSON APIs)
const base64 = await fabricJsonToImage('example.json', {
  returnFormat: 'base64'
});

// Get Buffer (most efficient, raw binary)
const buffer = await fabricJsonToImage('example.json', {
  returnFormat: 'buffer'
});

// Skip file writing, just get data
const imageData = await fabricJsonToImage('example.json', {
  outputPath: null,  // Don't save to file
  returnFormat: 'dataUrl'
});
```

## Return Formats

The function supports multiple return formats:

| Format | Type | Size | Best For |
|--------|------|------|----------|
| **`buffer`** | `Buffer` | Smallest (raw binary) | File operations, HTTP binary responses, efficient storage |
| **`base64`** | `string` | ~33% larger | JSON APIs, text-based storage, web services |
| **`dataUrl`** | `string` | Same as base64 + prefix | HTML/CSS embedding (`<img src="data:image/png;base64,...">`) |
| **`filepath`** | `string` | N/A | CLI usage, when you need the saved file location |

**Example sizes for a typical image:**
- Buffer: ~50KB
- Base64: ~67KB (33% overhead)
- DataUrl: ~67KB + small prefix

## Features

- ✅ Renders Fabric.js JSON to PNG/JPEG images
- ✅ Supports all Fabric.js shapes, text, images, gradients, and filters
- ✅ No headless browser required (uses node-canvas with Cairo)
- ✅ Simple CLI and programmatic API
- ✅ Customizable canvas dimensions and output format
- ✅ Multiple return formats (Buffer, Base64, DataURL, File Path)

## Notes

- **Custom Fonts**: Register fonts with node-canvas before rendering:
  ```javascript
  import { registerFont } from 'canvas';
  registerFont('./fonts/MyFont.ttf', { family: 'MyFont' });
  ```

- **Remote Images**: Ensure image URLs are accessible from your server, or pre-load images as buffers

- **Text Rendering**: May have subtle differences from browser rendering due to Pango text engine

## Examples

The `example.json` file contains a sample Fabric.js JSON with rectangles, circles, text, and triangles.

### Save Image Locally

```bash
# Save to default output.png and get file path
node index.js example.json -r filepath

# Save to custom location
node index.js example.json -o images/result.png -r filepath

# Save as JPEG
node index.js example.json -o result.jpg -f jpeg -r filepath
```

### Get Image Data (No File)

```bash
# Get data URL (default)
node index.js example.json -r dataUrl

# Get base64 string
node index.js example.json -r base64

# Get buffer info
node index.js example.json -r buffer
```

All commands will still save the image file by default (unless `outputPath` is set to `null`). The `returnFormat` option only controls what value is returned.
