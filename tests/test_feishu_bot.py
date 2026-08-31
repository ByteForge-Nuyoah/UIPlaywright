from utils.notify_utils.feishu_bot import FeishuBot


def test_feishu_sign_matches_custom_bot_protocol():
    bot = FeishuBot("https://example.com/hook", "test-secret")

    assert bot._build_sign("1700000000") == "mbm4Y4oluIPQ00qlBIhX8vAZ0EKv3nw0LuTb91jPL84="
