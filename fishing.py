#!/usr/bin/env python
# coding=utf-8

import keyboard
import mss
import cv2
import numpy
import time
import win32api
import win32con
import win32gui
from log import logger


class Fishing:
    def __init__(self):
        self.handle = self.get_handle()
        self.dimensions = {  # 请使用截图工具确认钓鱼部分定位，大概就行
            'left': 738,
            'top': 872,
            'width': 422,
            'height': 93
        }
        self.bingo = cv2.imread('pics/bingo.jpg')  # bingo 敲空格时机截图
        self.confirm = cv2.imread('pics/confirm.jpg')  # 钓完鱼之后的确认按钮截图
        self.rod = cv2.imread('pics/rod.jpg')  # 鱼竿 识别是否处于钓鱼状态截图
        self.h, self.w, self.channel = self.bingo.shape
        self.mss_obj = mss.mss()

    @staticmethod
    def get_handle():
        """获取跑跑卡丁车客户端句柄"""
        handle = win32gui.FindWindow("PopKart Client", None)
        if not handle:
            raise RuntimeError(f'未找到 跑跑卡丁车 句柄')
        return handle

    def send_space_to_handle(self):
        """跑跑卡丁车句柄发送空格事件"""
        space = 0x0020
        win32api.PostMessage(self.handle, win32con.WM_KEYDOWN, space, 0)
        win32api.PostMessage(self.handle, win32con.WM_KEYUP, space, 0)

    def send_enter_to_handle(self):
        """跑跑卡丁车句柄回车空格事件"""
        enter = 0x000D
        win32api.PostMessage(self.handle, win32con.WM_KEYDOWN, enter, 0)
        win32api.PostMessage(self.handle, win32con.WM_KEYUP, enter, 0)

    @staticmethod
    def wait_but_monitor_q(timeout):
        """等待指定时长 并监控按键q是否被点击 有则提前退出
        :arg timeout: int 等待时长
        :return bool 正常等待结束返回False 检测到q则提前返回True
        """
        time_end = time.time() + timeout
        while time.time() < time_end:
            if keyboard.is_pressed('q'):
                return True
        else:
            return False

    def run(self):
        """自动化触发入口"""
        print("按下 's' 触发自动化")
        print("按下 'q' 退出自动化")
        keyboard.wait('s')
        while True:
            screen = numpy.array(self.mss_obj.grab(self.dimensions))
            screen_remove = screen[:, :, :3]
            res1 = cv2.matchTemplate(screen_remove, self.bingo, cv2.TM_CCOEFF_NORMED)
            res2 = cv2.matchTemplate(screen_remove, self.confirm, cv2.TM_CCOEFF_NORMED)
            res3 = cv2.matchTemplate(screen_remove, self.rod, cv2.TM_CCOEFF_NORMED)
            _, max_val1, _, max_loc1 = cv2.minMaxLoc(res1)
            _, max_val2, _, max_loc2 = cv2.minMaxLoc(res2)
            _, max_val3, _, max_loc3 = cv2.minMaxLoc(res3)
            logger.info(f'【敲空格】最佳匹配度：{max_val1}  最佳匹配度坐标值：{max_loc1}')
            logger.info(f'【确认】最佳匹配度：{max_val2}  最佳匹配度坐标值：{max_loc2}')
            logger.info(f'【鱼竿】最佳匹配度：{max_val3}  最佳匹配度坐标值：{max_loc3}')
            if keyboard.is_pressed('q'):
                break
            # 1 敲空格钓鱼时机判断
            if max_val1 > .75:  # 75%属于经验值，请适当微调
                logger.debug(f'--- 准备按下空格bingo ---')
                self.send_space_to_handle()
                continue
            # 2 钓鱼结束敲回车 确认 判断
            if max_val2 > .90:
                logger.debug(f'--- 准备按下回车进行确认 ---')
                if not self.wait_but_monitor_q(3):
                    self.send_enter_to_handle()
                else:
                    break
                if not self.wait_but_monitor_q(3):
                    continue
                else:
                    break
            # 3 开始钓鱼 判断
            if max_val3 < .30:
                logger.debug(f'--- 准备按下空格进入钓鱼 ---')
                if not self.wait_but_monitor_q(3):
                    self.send_space_to_handle()
                else:
                    break
                if not self.wait_but_monitor_q(1.5):
                    continue
                else:
                    break


if __name__ == '__main__':
    fishing = Fishing()
    fishing.run()
