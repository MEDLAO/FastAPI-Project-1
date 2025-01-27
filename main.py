from fastapi import FastAPI, File, UploadFile
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
