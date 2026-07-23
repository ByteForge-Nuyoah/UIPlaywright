# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @Desc: 从测试报告中获取测试结果

import os
import json
from loguru import logger
from utils.tools.time_handle import timestamp_strftime


def get_test_results_from_allure_report(allure_html_path):
    """
    从allure生成的html报告的summary.json中，获取测试结果及测试情况
    :param allure_html_path: allure生成的html报告的绝对路径
    """
    try:
        summary_json_path = os.path.join(allure_html_path, "widgets", "summary.json")
        with open(summary_json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        case_count = data['statistic']
        _time = data['time'] or {}
        logger.debug(f"获取到的data是：{data}")
        keep_keys = {"passed", "failed", "broken", "skipped", "total"}
        test_results = {k: v for k, v in data['statistic'].items() if k in keep_keys}

        # 成功率 = 通过数 / 实际执行数（排除 skipped）。
        # 旧实现 (passed+skipped)/total 会把 skipped 算成通过且重复计入分母，导致虚高。
        executed = case_count.get("total", 0) - case_count.get("skipped", 0)
        if executed > 0:
            test_results["pass_rate"] = round(case_count.get("passed", 0) / executed * 100, 2)
        else:
            # 如果未运行用例，则成功率为 0.0
            test_results["pass_rate"] = 0.0

        # 收集用例运行时长（duration 可能为 None，如报告未完整生成时）
        duration = _time.get('duration')
        test_results['run_time'] = round(duration / 1000, 2) if isinstance(duration, (int, float)) else 0.0
        # start/stop 可能为 None
        test_results["start_time"] = timestamp_strftime(_time["start"]) if _time.get("start") else ""
        test_results["stop_time"] = timestamp_strftime(_time["stop"]) if _time.get("stop") else ""

        # 收集重试次数：默认 --reruns=0 时 retry-trend.json 可能不存在，缺失时记为 0
        retry_trend_json_path = os.path.join(allure_html_path, "widgets", "retry-trend.json")
        test_results["rerun"] = _read_retry_count(retry_trend_json_path)

        # 项目环境
        env_json_path = os.path.join(allure_html_path, "widgets", "environment.json")
        with open(env_json_path, 'r', encoding='utf-8') as file:
            env_data = json.load(file)
        for env in env_data:
            test_results[env['name']] = env["values"][0]
        logger.debug(f"获取到的测试结果：{test_results}")
        return test_results
    except FileNotFoundError as e:
        logger.error(f"程序中检查到您未生成allure报告，通常可能导致的原因是allure环境未配置正确，{e}")
        raise FileNotFoundError(
            "程序中检查到您未生成allure报告，"
            "通常可能导致的原因是allure环境未配置正确，"
        ) from e


def _read_retry_count(retry_trend_json_path):
    """读取 retry-trend.json 中的重试次数；文件不存在或结构异常时返回 0。"""
    try:
        with open(retry_trend_json_path, 'r', encoding='utf-8') as file:
            retry_data = json.load(file)
        return retry_data[0]["data"]["retry"]
    except (FileNotFoundError, IndexError, KeyError, TypeError, json.JSONDecodeError):
        return 0
