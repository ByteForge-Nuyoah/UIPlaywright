# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : faker_handle.py
# @Software: PyCharm
# @Desc: 测试数据生成类

import re
import random
import string
from faker import Faker
from datetime import datetime, date, timedelta



class FakerData:
    """
    测试数据生成类
    官方文档：https://faker.readthedocs.io/en/master/index.html
    """

    def __init__(self):
        self.fk_zh = Faker(locale='zh_CN')
        self.faker = Faker()

    @classmethod
    def generate_random_int(cls, *args) -> int:
        """
        :return: 随机数
        """
        # 检查是否传入了参数
        if not args:
            # 没有传参，就从5000内随机取一个整数返回
            return random.randint(0, 5000)

        # 排序参数并获取最小值和最大值
        min_val = min(args)
        max_val = max(args)

        # 生成并返回随机整数
        return random.randint(min_val, max_val)

    def generate_catch_phrase(self) -> str:
        """
        :return: 生成妙句(口号) （输出结果都是英文）
        """
        return self.faker.catch_phrase()

    def generate_phone(self, lan="en") -> str:
        """
        随机生成手机号码
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :return:
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        return faker_generator.phone_number()

    def generate_id_number(self, lan="en") -> str:
        """
        随机生成身份证号码
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :return:
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        return faker_generator.ssn()

    def generate_female_name(self, lan="en") -> str:
        """
        随机生成女生姓名
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :return:
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        return faker_generator.name_female()

    def generate_male_name(self, lan="en") -> str:
        """
        随机生成男生姓名
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :return:
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        return faker_generator.name_male()

    def generate_name(self, lan="en") -> str:
        """
        随机生成人名
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :return:
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        return faker_generator.name()

    def generate_company_name(self, lan: str = "en", fix: str = None) -> str:
        """
        生成公司名
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :param fix: 前后缀，可选pre， suf； pre表示公司前缀，suf标识公司后缀
        :return:
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        if fix == "pre":
            name = faker_generator.company_prefix()
        elif fix == "suf":
            name = faker_generator.company_suffix()
        else:
            name = faker_generator.company()

        return name

    def generate_paragraph(self, lan: str = "en", nb: int = 3) -> str:
        """
        随机生成生成段落
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :param nb: 段落个数，默认是3个
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        return faker_generator.paragraph(nb_sentences=nb, variable_nb_sentences=True, ext_word_list=None)

    def generate_words(self, lan: str = "en", nb: int = 1) -> str:

        """
        随机生成词语
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :param nb: 词语个数，默认是1个
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        # Generate words
        if nb < 1:
            nb = 1  # Ensure nb is at least 1 to avoid infinite loops or errors

        if nb == 1:
            text = faker_generator.word(ext_word_list=None)
        else:
            text = "-".join(faker_generator.words(nb=nb, ext_word_list=None))

        return text

    def generate_email(self, lan="en") -> str:
        """
        随机生成邮箱
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :return:
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        return faker_generator.email()

    @classmethod
    def generate_identifier(cls, char_len=8) -> str:
        """
        :return:生成随机标识，满足要求：长度为2~100（这里长度通过传参控制，默认为8）， 只能包含数字，字母，下划线(_)，中划线(-)，英文句号(.)，必须以数字和字母开头，不能以下划线/中划线/英文句号开头和结尾
        """
        while True:
            identifier = ''.join(
                random.choices(string.ascii_letters + string.digits + '_.-', k=char_len))  # 生成指定长度的随机标识

            if (
                    re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,98}[a-zA-Z0-9]$', identifier) and
                    not (identifier.startswith('_') or identifier.startswith('-') or identifier.startswith('.')) and
                    not (identifier.endswith('_') or identifier.startswith('-') or identifier.endswith('.'))
            ):
                return identifier

    def generate_city(self, lan="en", full: bool = True) -> str:
        """
        随机生成城市名
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :param full: 城市全名，默认是开启
        :return:
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        if full:
            city = faker_generator.city()
        else:
            city = faker_generator.city_name()

        return city

    def generate_province(self, lan="en") -> str:
        """
        随机生成城市名
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :return:
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        return faker_generator.province()

    def generate_address(self, lan="en") -> str:
        """
        随机生成地址
        :param lan: 语言类型，可选：en, zh； zh表示中文，en表示英文，默认是en
        :return:
        """
        if lan not in ("en", "zh"):
            raise ValueError("Language must be 'en' or 'zh'")

        # Initialize the faker or fk_zh object based on the language
        faker_generator = self.faker if lan == "en" else self.fk_zh

        return faker_generator.address()

    @classmethod
    def generate_time(cls, fmt='%Y-%m-%d %H:%M:%S', days=0) -> str:
        """
        根据传入的天数，返回当前时间加上或减去这些天数后的日期和时间，或者仅返回当前时间。
        :return:
        """
        # 获取当前时间
        current_time = datetime.now()
        # 计算增加或减少天数后的时间
        if days != 0:
            future_time = current_time + timedelta(days=days)
        else:
            future_time = current_time
        # 格式化时间
        return future_time.strftime(fmt)

    @classmethod
    def generate_today_date(cls, fmt='%Y-%m-%d'):
        """获取今日0点整时间"""
        today = datetime.now().date()
        if fmt == '%Y-%m-%d %H:%M:%S':
            return today.strftime(fmt) + " 00:00:00"
        return today.strftime(fmt)

    @classmethod
    def generate_time_after_week(cls, fmt='%Y-%m-%d'):
        """获取一周后12点整的时间"""
        if fmt == '%Y-%m-%d %H:%M:%S':
            return (date.today() + timedelta(days=+6)).strftime(fmt) + " 00:00:00"
        return (date.today() + timedelta(days=+6)).strftime(fmt)

    @classmethod
    def remove_special_characters(cls, target: str):
        """
        移除字符串中的特殊字符。
        在Python中用replace()函数操作指定字符
        常用字符unicode的编码范围：
        数字：\u0030-\u0039
        汉字：\u4e00-\u9fa5
        大写字母：\u0041-\u005a
        小写字母：\u0061-\u007a
        英文字母：\u0041-\u007a
        """
        pattern = r'([^\u4e00-\u9fa5])'
        result = re.sub(pattern, '', target)
        return result

    def generate_hex_color(self):
        """生成随机颜色数据"""
        return self.faker.hex_color()
