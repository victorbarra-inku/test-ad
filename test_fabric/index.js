import { StaticCanvas } from 'fabric/node';
import fs from 'fs';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';
import { loadImage } from 'canvas';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Extracts dimensions from a base64 backgroundImage in Fabric.js JSON
 * @param {Object|string} fabricJson - Fabric.js JSON object or path to JSON file
 * @returns {Promise<{width: number, height: number}|null>} Image dimensions or null if no backgroundImage
 */
async function getBackgroundImageDimensions(fabricJson) {
  // Load JSON from file if string path provided
  let json;
  if (typeof fabricJson === 'string') {
    const jsonPath = path.isAbsolute(fabricJson) 
      ? fabricJson 
      : path.join(__dirname, fabricJson);
    const jsonContent = fs.readFileSync(jsonPath, 'utf8');
    json = JSON.parse(jsonContent);
  } else {
    json = fabricJson;
  }

  // Check if backgroundImage exists
  if (!json.backgroundImage || !json.backgroundImage.src) {
    return null;
  }

  try {
    // Load the image from the data URL
    const image = await loadImage(json.backgroundImage.src);
    return {
      width: image.width,
      height: image.height
    };
  } catch (error) {
    console.error('Error extracting backgroundImage dimensions:', error.message);
    return null;
  }
}

/**
 * Converts Fabric.js JSON to an image file or returns image data
 * @param {Object|string} fabricJson - Fabric.js JSON object or path to JSON file
 * @param {Object} options - Rendering options
 * @param {string} options.outputPath - Output file path (default: 'output.png'). Set to null to skip file writing
 * @param {number} options.width - Canvas width (default: 800)
 * @param {number} options.height - Canvas height (default: 600)
 * @param {string} options.format - Image format: 'png' or 'jpeg' (default: 'png')
 * @param {string} options.returnFormat - Return format: 'buffer', 'base64', 'dataUrl', or 'filepath' (default: 'filepath')
 * @returns {Promise<Buffer|string>} Image data in requested format:
 *   - 'buffer': Returns Buffer (most efficient, raw binary)
 *   - 'base64': Returns base64 string (good for JSON APIs)
 *   - 'dataUrl': Returns data URL string (ready for HTML/CSS: "data:image/png;base64,...")
 *   - 'filepath': Returns file path string (default)
 */
async function fabricJsonToImage(fabricJson, options = {}) {
  const {
    outputPath = 'output.png',
    width = 800,
    height = 600,
    format = 'png',
    returnFormat = 'filepath' // 'buffer', 'base64', 'dataUrl', or 'filepath'
  } = options;

  // Load JSON from file if string path provided
  let json;
  if (typeof fabricJson === 'string') {
    const jsonPath = path.isAbsolute(fabricJson) 
      ? fabricJson 
      : path.join(__dirname, fabricJson);
    const jsonContent = fs.readFileSync(jsonPath, 'utf8');
    json = JSON.parse(jsonContent);
  } else {
    json = fabricJson;
  }

  // Always extract and display backgroundImage dimensions if present
  if (json.backgroundImage && json.backgroundImage.src) {
    try {
      const dimensions = await getBackgroundImageDimensions(json);
      if (dimensions) {
        console.log(`\n📐 BackgroundImage Dimensions:`);
        console.log(`   Width: ${dimensions.width}px`);
        console.log(`   Height: ${dimensions.height}px`);
        console.log(`   Aspect Ratio: ${(dimensions.width / dimensions.height).toFixed(2)}`);
      }
    } catch (error) {
      // Silently fail if dimensions can't be extracted
    }
  }

  // Use canvas dimensions from JSON if available, otherwise use provided/default dimensions
  const canvasWidth = json.width || width;
  const canvasHeight = json.height || height;

  // Create canvas with correct dimensions
  const canvas = new StaticCanvas(null, { width: canvasWidth, height: canvasHeight });

  // Load Fabric.js JSON
  await canvas.loadFromJSON(json);

  // Render the canvas
  canvas.renderAll();

  // Export as image - get data URL first
  const dataUrl = canvas.toDataURL({ format: format });
  
  // Extract base64 data from data URL (remove "data:image/png;base64," prefix)
  const base64Data = dataUrl.split(',')[1];
  
  // Convert base64 string to Buffer (most efficient format)
  const buffer = Buffer.from(base64Data, 'base64');
  
  // Write buffer to file if outputPath is provided
  if (outputPath) {
    fs.writeFileSync(outputPath, buffer);
    console.log(`✅ Image saved to: ${outputPath}`);
  }
  
  // Return in requested format
  switch (returnFormat) {
    case 'buffer':
      return buffer; // Most efficient - raw binary data
    case 'base64':
      return base64Data; // Base64 string (no data URL prefix)
    case 'dataUrl':
      return dataUrl; // Full data URL (ready for HTML/CSS embedding)
    case 'filepath':
    default:
      return outputPath || 'output.png'; // File path
  }

//   // Export as image using stream
//   return new Promise((resolve, reject) => {
//     const out = fs.createWriteStream(outputPath);
//     const stream = canvas.createPNGStream();
    
//     stream.on('data', function(chunk) {
//       out.write(chunk);
//     });
    
//     stream.on('end', function() {
//       out.end();
//       console.log(`✅ Image saved to: ${outputPath}`);
//       resolve(outputPath);
//     });
    
//     stream.on('error', function(err) {
//       out.destroy();
//       reject(err);
//     });
    
//     out.on('error', function(err) {
//       stream.destroy();
//       reject(err);
//     });
//   });
}

// CLI usage
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
Usage: node index.js <fabric-json-file> [options]

Options:
  --output, -o         Output file path (default: output.png)
  --width, -w          Canvas width (default: 800)
  --height, -h         Canvas height (default: 600)
  --format, -f         Image format: png or jpeg (default: png)
  --return-format, -r  Return format: buffer, base64, dataUrl, or filepath (default: filepath)
  --dimensions, -d     Extract and display backgroundImage dimensions only (no rendering)

Examples:
  node index.js fabric-data.json
  node index.js fabric-data.json --output result.png --width 1200 --height 800
  node index.js fabric-data.json -o result.jpg -f jpeg
  node index.js fabric-data.json -r dataUrl
  node index.js fabric-data.json --return-format base64
  node index.js fabric-data.json --dimensions
    `);
    process.exit(0);
  }

  const inputFile = args[0];
  const options = {};

  // Check for dimensions flag first
  if (args.includes('--dimensions') || args.includes('-d')) {
    try {
      const dimensions = await getBackgroundImageDimensions(inputFile);
      if (dimensions) {
        console.log(`\n📐 BackgroundImage Dimensions:`);
        console.log(`   Width: ${dimensions.width}px`);
        console.log(`   Height: ${dimensions.height}px`);
        console.log(`   Aspect Ratio: ${(dimensions.width / dimensions.height).toFixed(2)}`);
      } else {
        console.log('\n⚠️  No backgroundImage found in JSON');
      }
    } catch (error) {
      console.error('❌ Error:', error.message);
      process.exit(1);
    }
    return;
  }

  // Parse command line arguments
  for (let i = 1; i < args.length; i += 2) {
    const flag = args[i];
    const value = args[i + 1];

    switch (flag) {
      case '--output':
      case '-o':
        options.outputPath = value;
        break;
      case '--width':
      case '-w':
        options.width = parseInt(value, 10);
        break;
      case '--height':
      case '-h':
        options.height = parseInt(value, 10);
        break;
      case '--format':
      case '-f':
        options.format = value.toLowerCase();
        break;
      case '--return-format':
      case '-r':
        options.returnFormat = value.toLowerCase();
        break;
    }
  }

  try {
    const result = await fabricJsonToImage(inputFile, options);
    
    // Display result based on return format
    if (options.returnFormat === 'dataUrl' || options.returnFormat === 'base64') {
      // For dataUrl/base64, show first 100 chars + "..."
      const preview = result.length > 100 
        ? result.substring(0, 100) + '...' 
        : result;
      console.log(`\n📦 Result (${options.returnFormat || 'dataUrl'}):`);
      console.log(preview);
      console.log(`\n📏 Total length: ${result.length} characters`);
    } else if (options.returnFormat === 'buffer') {
      console.log(`\n📦 Result (buffer):`);
      console.log(`Buffer size: ${result.length} bytes`);
      console.log(`First 50 bytes: ${result.slice(0, 50).toString('hex')}...`);
    } else {
      // filepath (default)
      console.log(`\n📁 Result: ${result}`);
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Export for programmatic use
export { fabricJsonToImage, getBackgroundImageDimensions };

// Run CLI if executed directly
const isMainModule = process.argv[1] && 
  pathToFileURL(process.argv[1]).href === import.meta.url;
if (isMainModule) {
  main();
}