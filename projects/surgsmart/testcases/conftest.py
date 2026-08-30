def pytest_configure(config):
    config.addinivalue_line("markers", "login: SurgSmart login cases")
    config.addinivalue_line("markers", "recordings: converted Playwright recordings")
