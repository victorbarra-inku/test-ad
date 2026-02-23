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

```bash
# Basic usage
node index.js example.json

# With custom output path
node index.js example.json --output result.png

# With custom dimensions
node index.js example.json --width 1200 --height 800

# Export as JPEG
node index.js example.json --format jpeg --output result.jpg

# Using short flags
node index.js example.json -o output.png -w 1000 -h 600 -f png
```

### Programmatic Usage

```javascript
import { fabricJsonToImage } from './index.js';

// From JSON object
await fabricJsonToImage({
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
  format: 'png'
});

// From JSON file
await fabricJsonToImage('example.json', {
  outputPath: 'output.png'
});
```

## Features

- ✅ Renders Fabric.js JSON to PNG/JPEG images
- ✅ Supports all Fabric.js shapes, text, images, gradients, and filters
- ✅ No headless browser required (uses node-canvas with Cairo)
- ✅ Simple CLI and programmatic API
- ✅ Customizable canvas dimensions and output format

## Notes

- **Custom Fonts**: Register fonts with node-canvas before rendering:
  ```javascript
  import { registerFont } from 'canvas';
  registerFont('./fonts/MyFont.ttf', { family: 'MyFont' });
  ```

- **Remote Images**: Ensure image URLs are accessible from your server, or pre-load images as buffers

- **Text Rendering**: May have subtle differences from browser rendering due to Pango text engine

## Example

The `example.json` file contains a sample Fabric.js JSON with rectangles, circles, text, and triangles. Run:

```bash
node index.js example.json
```

This will generate `output.png` with the rendered canvas.
