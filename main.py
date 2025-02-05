from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Request
from colorthief import ColorThief
from fastapi.responses import JSONResponse
import io
import os
import colorsys


app = FastAPI()


RAPIDAPI_SECRET = os.getenv("RAPIDAPI_SECRET")


@app.middleware("http")
async def enforce_rapidapi_usage(request: Request, call_next):
    rapidapi_proxy_secret = request.headers.get("X-RapidAPI-Proxy-Secret")

    if rapidapi_proxy_secret != RAPIDAPI_SECRET:
        return JSONResponse(status_code=403, content={"error": "Access restricted to RapidAPI users only."})

    return await call_next(request)


@app.get("/")
def read_root():
    welcome_message = (
        "Welcome!"
        "¡Bienvenido!"
        "欢迎!"
        "नमस्ते!"
        "مرحبًا!"
        "Olá!"
        "Здравствуйте!"
        "Bonjour!"
        "বাংলা!"
        "こんにちは!"
    )
    return {"message": welcome_message}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Function to convert RGB to Hex
def rgb_to_hex(rgb):
    """Convert an RGB list [r, g, b] to HEX format."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


@app.post("/dominant-color")
async def get_dominant_color(file: UploadFile = File(...)):
    """
    Extract the dominant color from an uploaded image.
    """
    # Read the uploaded file
    image_data = await file.read()
    image_file = io.BytesIO(image_data)

    # Use ColorThief to get the dominant color
    color_thief = ColorThief(image_file)
    dominant_color = color_thief.get_color(quality=1)

    # Convert RGB to Hexadecimal
    hex_color = rgb_to_hex(dominant_color)
    print(type(hex_color))
    print(hex_color)

    return {
        "dominant_color_rgb": dominant_color,
        "dominant_color_hex": hex_color
    }


@app.post("/extract-colors")
async def extract_colors(
    file: UploadFile = File(...),
    count: int = Query(3, ge=1, le=10, description="Number of dominant colors to extract (1-10)")
):
    """
    Extract multiple dominant colors from an image.
    """
    try:
        # Read the uploaded file
        image_data = await file.read()
        image_file = io.BytesIO(image_data)

        # Use ColorThief to get the dominant color palette
        color_thief = ColorThief(image_file)
        palette = color_thief.get_palette(color_count=count, quality=1)

        palette = palette[:count]

        # Convert RGB colors to HEX
        colors = [{"rgb": color, "hex": rgb_to_hex(color)} for color in palette]

        return {
            "colors_extracted": len(colors),
            "colors": colors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/hex-to-rgb")
def convert_hex_to_rgb(hex: str = Query(..., description="HEX color string (e.g., #ff5733)")):
    """Convert HEX to RGB."""
    try:
        # Remove the leading "#" if present
        hex = hex.lstrip("#")
        if len(hex) != 6:
            raise ValueError("HEX color must be 6 characters.")

        # Convert HEX to RGB
        rgb = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
        return {"hex": f"#{hex}", "rgb": list(rgb)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/rgb-to-hex")
def convert_rgb_to_hex(
    r: int = Query(..., ge=0, le=255, description="Red component (0–255)"),
    g: int = Query(..., ge=0, le=255, description="Green component (0–255)"),
    b: int = Query(..., ge=0, le=255, description="Blue component (0–255)")
):
    """Convert RGB to HEX."""
    try:
        # Format RGB as HEX
        hex_color = rgb_to_hex([r, g, b])
        return {"rgb": [r, g, b], "hex": hex_color}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def hex_to_hsl(hex_color):
    """Convert HEX to HSL (Hue, Saturation, Lightness)."""
    hex_color = hex_color.lstrip("#")  # Remove '#' if present
    if len(hex_color) != 6:
        raise ValueError("HEX color must be 6 characters.")

    # Convert HEX → RGB (0-255 range)
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

    # Convert RGB → HSL (0-1 range)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l  # Hue, Saturation, Lightness


def hsl_to_hex(h, s, l):
    """Convert HSL back to HEX."""
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


def generate_harmonious_colors(hex_color, harmony_type):
    """Generate harmonious colors based on color harmony rules."""
    h, s, l = hex_to_hsl(hex_color)  # Convert to HSL

    if harmony_type == "analogous":
        # Shift hue by ±30° (~0.08 in 0-1 scale)
        colors = [hsl_to_hex((h - 0.08) % 1, s, l), hsl_to_hex((h + 0.08) % 1, s, l)]

    elif harmony_type == "complementary":
        # Shift hue by 180° (~0.5 in 0-1 scale)
        colors = [hsl_to_hex((h + 0.5) % 1, s, l)]

    elif harmony_type == "triadic":
        # Shift hue by 120° & 240° (~1/3 and 2/3 in 0-1 scale)
        colors = [hsl_to_hex((h + 1/3) % 1, s, l), hsl_to_hex((h + 2/3) % 1, s, l)]

    else:
        raise ValueError("Invalid harmony type. Choose from: analogous, complementary, triadic.")

    return colors


@app.get("/harmonious-colors")
def harmonious_colors(
    hex: str = Query(..., description="Base color in HEX format (e.g., #ff5733)"),
    type: str = Query("analogous", description="Harmony type: analogous, complementary, triadic")
):
    """
    Return harmonious colors with explanations.

    This endpoint generates color combinations based on color theory.
    It applies different harmony rules (analogous, complementary, triadic)
    to suggest aesthetically pleasing color palettes.
    """
    try:
        colors = generate_harmonious_colors(hex, type)

        # Provide explanations for each harmony type
        explanations = {
            "analogous": "Analogous colors are next to each other on the color wheel. They create a smooth, natural look.",
            "complementary": "Complementary colors are opposite on the color wheel. They create strong contrast and make each other stand out.",
            "triadic": "Triadic colors are evenly spaced on the color wheel. This creates a dynamic and well-balanced palette."
        }

        return {
            "base_color": hex,
            "harmony_type": type,
            "colors": colors,
            "explanation": explanations.get(type, "Invalid harmony type.")
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
