from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from colorthief import ColorThief
import io


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome!"}


# Function to convert RGB to Hex
def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


@app.post("/dominant-color")
async def get_dominant_color(file: UploadFile = File(...)):
    # Read the uploaded file
    image_data = await file.read()
    image_file = io.BytesIO(image_data)

    # Use ColorThief to get the dominant color
    color_thief = ColorThief(image_file)
    dominant_color = color_thief.get_color(quality=1)

    # Convert RGB to Hexadecimal
    hex_color = rgb_to_hex(dominant_color)

    return {
        "dominant_color_rgb": dominant_color,
        "dominant_color_hex": hex_color
    }


@app.get("/hex-to-rgb")
def hex_to_rgb(hex: str = Query(..., description="HEX color string (e.g., #ff5733)")):
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
def rgb_to_hex(
    r: int = Query(..., ge=0, le=255, description="Red component (0–255)"),
    g: int = Query(..., ge=0, le=255, description="Green component (0–255)"),
    b: int = Query(..., ge=0, le=255, description="Blue component (0–255)")
):
    """Convert RGB to HEX."""
    try:
        # Format RGB as HEX
        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
        return {"rgb": [r, g, b], "hex": hex_color}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
