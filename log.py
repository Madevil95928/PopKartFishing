#!/usr/bin/env python
# coding=utf-8

import logging
import os
import re
import datetime
import sys
from typing import Optional, List
from colorama import init, Style

__all__ = ["logger"]
init()
# MSG_FMT = "%(asctime)s.%(msec)03d[%(levelname)s][%(module)s:%lineno)d]%(message)s"
MSG_FMT = "%(asctime)s.%(msec)03d[%(levelname)s]%(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"
COMMON_COLOR = {
    'red': '#cc0000',
    'green': '#228b22',
    'yellow': '#ffd700',
    'blue': '#6495ed',
    'magenta': '#ff00ff',
    'cyan': '#00ffff',
    'white': '#ffffff',
    'black': '#000000',
    'pink': '#ffc0cb',
    'purple': '#800080',
    'orange': '#ffa500'
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, color: str = 'white'):
        logging.Formatter.__init__(self, MSG_FMT, DATE_FMT)
        self.color = color

    def parse_color(self):
        if self.color in COMMON_COLOR.keys():
            color = COMMON_COLOR[self.color]
        elif re.match('^#[0-9A-Fa-f]{6}$', self.color):
            color = self.color
        elif re.match('^[0-9A-Fa-f]{6}$', self.color):
            color = '#' + self.color
        else:
            color = COMMON_COLOR['white']
        color = color[1:]
        r, g, b = map(lambda x: int(x, 16), (color[:2], color[2:4], color[4:]))
        return f'\033[38;2;{r};{g};{b}m'

    def format(self, record):
        s = ''.join(map(str, (
            self.parse_color(),
            datetime.datetime.fromtimestamp(record.created),
            f'[{record.levelname}]',
            record.getMessage(),
            # '\033[0m',
            Style.RESET_ALL,
        )))
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s


class Log:
    def __init__(self, name=None, level=10, console=True, console_color=True, file: Optional[List[str]] = None):
        self.name = name or 'global_console'
        self._logger = logging.getLogger(self.name)
        # 已存在handler的logger容器直接返回，不再二次定义
        if len(self._logger.handlers) != 0:
            return
        self._logger.setLevel(level)
        self._logger.propagate = False  # 不传递父级
        self.console_color = console_color  # 默认带颜色
        if console:
            if self.console_color:
                self.console_handler = logging.StreamHandler(stream=sys.stdout)
                self.console_handler.setFormatter(ColoredFormatter())
                self._logger.addHandler(self.console_handler)
            else:
                self.console_handler = logging.StreamHandler(stream=sys.stdout)
                self.console_handler.setFormatter(logging.Formatter(MSG_FMT, DATE_FMT))
                self._logger.addHandler(self.console_handler)
        if file:
            for _file in file:
                _file = os.path.abspath(_file)
                try:
                    file_handler = logging.FileHandler(_file)
                except Exception as e:
                    self._logger.error(f'未能正确指定文件流处理器：{_file}；异常详情：{e}')
                    continue
                file_handler.setFormatter(logging.Formatter(MSG_FMT, DATE_FMT))
                self._logger.addHandler(file_handler)

    def reset_console(self, color: str):
        self._logger.removeHandler(self.console_handler)
        self.console_handler.setFormatter(ColoredFormatter(color=color))
        self._logger.addHandler(self.console_handler)

    def debug(self, msg: str, color='blue'):
        if self.console_color:
            self.reset_console(color)
        return self._logger.debug(msg)

    def info(self, msg: str, color='white'):
        if self.console_color:
            self.reset_console(color)
        return self._logger.info(msg)

    def warning(self, msg: str, color='yellow'):
        if self.console_color:
            self.reset_console(color)
        return self._logger.warning(msg)

    def error(self, msg: str, color='red'):
        if self.console_color:
            self.reset_console(color)
        return self._logger.error(msg)


logger = Log()


if __name__ == '__main__':
    logger.debug('调试')
    logger.info('记录')
    logger.info('记录 + 改色', color='green')
    logger.warning('警告')
    logger.error('异常')
