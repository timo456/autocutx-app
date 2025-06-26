from PIL import Image, ImageDraw, ImageFont


def create_logo_image(text, width=400, height=80, font_size=48):
    """
    建立一張文字型 LOGO 圖片，背景透明。
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # 透明底
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # ✅ 用 textbbox 取代已廢棄的 textsize
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, font=font, fill=(255, 255, 255, 230))
    return img

def create_text_image(text, width=720, height=100, font_size=40):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # 透明背景
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # ✅ 計算文字大小
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))  # 白色字
    return img
