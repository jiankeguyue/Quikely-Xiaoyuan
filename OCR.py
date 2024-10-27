import sys

import cv2
import pytesseract
import numpy as np
import re
import pyautogui
import time
import threading
from threading import Thread, Lock
import pynput
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener
import colorama

# 如果 Tesseract 没有在环境变量中，设置 Tesseract 可执行文件的路径
pytesseract.pytesseract.tesseract_cmd = r'D:\OCR\tesseract.exe'

# 初始化鼠标控制器
mouse = Controller()
# 全局变量
running = False  # 标志变量，控制任务的运行
lock = Lock()  # 定义锁
draw_y = 800  # ROI 的底部加上 300 像素
num = 0


# 定义绘图函数，并限制在0.1秒左右完成
def draw_symbol(symbol):
    start_time = time.time()  # 记录开始时间

    screen_width, screen_height = pyautogui.size()
    x = 850  # 水平居中
    y = draw_y + 300  # 使用新的 y 坐标
    duration = 0.1  # 每条线的持续时间，设定为 0.1 秒以保持绘制时间

    print(colorama.Fore.GREEN + f"[info] 当前鼠标位置: ({x}, {y})")

    mouse.position = (x, y)  # 将鼠标移动到起始位置
    mouse.press(Button.left)

    if symbol == '>':
        # 绘制 ">" 符号
        mouse.move(screen_width * 0.03, screen_height * 0.03)  # 右下斜线（缩短）
        time.sleep(duration)
        # 增加转弯处的形状
        mouse.move(screen_width * 0.01, 0)  # 横向移动
        time.sleep(duration)
        mouse.move(0, screen_height * 0.15)  # 右上斜线（缩短）
        time.sleep(0.2)

    elif symbol == '<':
        # 绘制 "<" 符号
        mouse.move(-screen_width * 0.03, screen_height * 0.03)  # 左下斜线（缩短）
        time.sleep(duration)
        # 增加转弯处的形状
        mouse.move(-screen_width * 0.01, 0)  # 横向移动
        time.sleep(duration)
        mouse.move(0, -screen_height * 0.15)  # 左上斜线（缩短）
        time.sleep(0.2)

    elif symbol == '=':
        # 绘制 "=" 符号
        mouse.move(-screen_width * 0.02, 0)  # 向左移动一点
        mouse.release(Button.left)
        mouse.press(Button.left)
        mouse.move(screen_width * 0.03, 0)  # 第一条横线（缩短）
        time.sleep(duration)
        mouse.release(Button.left)

        mouse.position = (x - screen_width * 0.02, y + screen_height * 0.02)  # 向下移动一点
        mouse.press(Button.left)
        mouse.move(screen_width * 0.03, 0)  # 第二条横线（缩短）
        time.sleep(duration)
        mouse.release(Button.left)
    else:
        print("无法绘制该符号")

    mouse.release(Button.left)  # 确保释放鼠标按键
    end_time = time.time()  # 记录结束时间
    print(colorama.Fore.GREEN + f"[info] 绘图 '{symbol}' 完成，耗时: {end_time - start_time:.4f} 秒")





def process_questions():
    global running
    i = 0
    previous_result = None
    previous_numbers = (None, None)  # 新增，用于存储前一题的数字
    stable_count = 0
    stable_threshold = 1  # 可以将阈值设为1，因为我们已经检测题目变化
    num = 0

    while running:
        start_time = time.time()  # 开始时间

        # 获取屏幕截图
        screenshot_start_time = time.time()
        image = pyautogui.screenshot()
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        screenshot_end_time = time.time()

        print(colorama.Fore.GREEN + f"截图耗时: {screenshot_end_time - screenshot_start_time:.4f} 秒")

        # 提取需要识别的区域（根据实际情况调整坐标）
        roi = image[350:460, 700:1050]


        # 图像预处理
        processing_start_time = time.time()
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        roi_contrast = cv2.convertScaleAbs(roi_gray, alpha=2.0, beta=0)  # 增强对比度
        roi_blur = cv2.GaussianBlur(roi_contrast, (5, 5), 0)
        _, roi_thresh = cv2.threshold(roi_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processing_end_time = time.time()

        print(colorama.Fore.GREEN + f"图像处理耗时: {processing_end_time - processing_start_time:.4f} 秒")

        # OCR 识别
        ocr_start_time = time.time()
        custom_config = r'--oem 3 --psm 6'
        roi_text = pytesseract.image_to_string(roi_thresh, config=custom_config)
        ocr_end_time = time.time()

        print(colorama.Fore.GREEN + f"OCR 识别耗时: {ocr_end_time - ocr_start_time:.4f} 秒")

        # 提取数字并判断大小
        matches = re.findall(r'\d+',
                             roi_text)

        if len(matches) >= 2:
            num1, num2 = int(matches[0]), int(matches[1])
            print(colorama.Fore.YELLOW + f"第{i + 1}题识别到的数字：{num1}, {num2}")

            # 检查是否为新题目
            if (num1, num2) == previous_numbers:
                print("检测到重复的题目，跳过处理")
                time.sleep(0.1)


            else:
                # 更新前一题的数字
                previous_numbers = (num1, num2)

                # 判断大小
                if num1 < num2:
                    result = '<'
                elif num1 > num2:
                    result = '>'
                else:
                    result = '='
                print(f"判断结果：{num1} {result} {num2}")


                draw_symbol(result)
                # 绘制符号
                # draw_start_time = time.time()
                # # 启动绘图线程
                # draw_thread = Thread(target=draw_symbol, args=(result,))
                #
                #
                # draw_thread.start()
                # draw_thread.join()  # 等待绘图完成
                # draw_end_time = time.time()
                # time.sleep(0.1)
                # print(f"绘图耗时: {draw_end_time - draw_start_time:.4f} 秒")

        else:
            print(f"第{i + 1}题未能识别出足够的数字")

        # 等待一小段时间以确保下一题加载
        i += 1
        end_time = time.time()
        print(colorama.Fore.GREEN + f"第{i}题处理总耗时: {end_time - start_time:.4f} 秒\n")


def toggle_running(key):
    global running
    if key == pynput.keyboard.Key.enter:
        if not running:
            running = True
            print("任务已启动")
            process_questions()
        else:
            running = False
            print("任务已停止")


# 监听键盘输入
with Listener(on_press=toggle_running) as listener:
    listener.join()
