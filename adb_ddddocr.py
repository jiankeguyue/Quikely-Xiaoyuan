import os

import colorama
import ddddocr
from time import sleep
from PIL import Image


# 截图
def shot_screen(path):
    os.system(f'adb shell screencap -p > {path}')

    # 读取截取的屏幕截图并替换行结束符
    with open(path, 'rb') as f:
        return f.read().replace(b'\r\n', b'\n')

# 裁剪
def process_image(image_path, crop_area):
    with Image.open(image_path) as img:
        return img.crop(crop_area)

def extract_text(img):
    """提取图片中的文本。"""
    with open(img, 'rb') as f:
        img_bytes = f.read()
    res = ocr.classification(img_bytes)
    return res.replace(' ', '').replace('\n', '')


def compare_numbers(x, y):
    """比较两个数字并相应地执行滑动操作。"""
    try:
        x = x.replace('o', '0')
        y = y.replace('o', '0')
        x_int, y_int = int(x), int(y)
        if x_int > y_int:
            print(f"{x} > {y}")
            os.system("adb shell input swipe 450 1300 850 1400 1")
            os.system("adb shell input swipe 850 1400 450 1500 1")
        else:
            print(f"{x} < {y}")
            os.system("adb shell input swipe 850 1300 450 1400 1")
            os.system("adb shell input swipe 450 1400 850 1500 1")
    except Exception as e:
        print(colorama.Fore.RED + '[error] 出现故障: {}'.format(e))
        print("数字格式无效。")


def main():
    """主程序逻辑。"""
    screenshot_path = 'screenshot.png'

    # 截取屏幕并保存
    screenshot = shot_screen(screenshot_path)
    with open(screenshot_path, 'wb') as f:
        f.write(screenshot)

    # 定义裁剪区域（左，上，右，下）分别是两个数字在图片中的区域坐标
    crop_areas = [
        (250, 420, 470, 580),
        (603, 420, 830, 580)
    ]

    cropped_images = []
    for i, crop_area in enumerate(crop_areas, start=1):
        cropped_image = process_image(screenshot_path, crop_area)
        cropped_image_path = f"screenshot{i}.png"
        cropped_image.save(cropped_image_path)
        cropped_images.append(cropped_image_path)

    # 从裁剪后的图片中提取文本
    texts = [extract_text(image) for image in cropped_images]

    # 比较提取的数字
    compare_numbers(texts[0], texts[1])


if __name__ == '__main__':
    ocr = ddddocr.DdddOcr(show_ad=False)
    while True:
        main()
        sleep(0.2)