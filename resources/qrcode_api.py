import os
import qrcode
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageDraw

# 載入環境變數
load_dotenv()

# QR Code 圖片儲存路徑
QR_DIR = "qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

def generate_qrcode(data):
    """
    生成帶有圓角和灰色邊框的 QR Code 並返回連結。
    
    :param data: QR Code 中的內容
    :return: 網址連結和內容
    """
    if not data:
        raise ValueError("內容不能為空")

    # 生成唯一檔案名稱
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"qrcode_{timestamp}.png"
    filepath = os.path.join(QR_DIR, filename)

    # 生成 QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # 添加圓角
    img = add_rounded_corners(img, radius=10)

    # 添加灰色邊框
    img = add_gray_border(img, border_size=10, border_color=(169, 169, 169, 255))

    # 儲存圖片
    img.save(filepath)

    # 返回連結
    return os.getenv('website_link') + '/qrcodes/' + filename, data

def add_rounded_corners(img, radius=10):
    """
    為圖片添加圓角。
    
    :param img: 原始圖片
    :param radius: 圓角半徑
    :return: 圓角處理後的圖片
    """
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, img.size[0], img.size[1]), radius=radius, fill=255)
    img.putalpha(mask)
    return img

def add_gray_border(img, border_size=10, border_color=(169, 169, 169, 255)):
    """
    為圖片添加灰色邊框。
    
    :param img: 原始圖片
    :param border_size: 邊框寬度
    :param border_color: 邊框顏色 (RGBA 格式)
    :return: 加邊框後的圖片
    """
    new_size = (img.size[0] + 2 * border_size, img.size[1] + 2 * border_size)
    bordered_img = Image.new("RGBA", new_size, border_color)
    bordered_img.paste(img, (border_size, border_size), img)
    return bordered_img