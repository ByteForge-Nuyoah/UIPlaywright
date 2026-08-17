# -*- coding: utf-8 -*-
"""
一次性探测脚本：用 Playwright 打开 https://app.dev.surgsmart.com/login，
抓取 input/button/form/iframe 等结构，输出 JSON 报告 + 截图，供后续
写 Page Object 时使用。
"""
import json
import os
import sys
import time
from playwright.sync_api import sync_playwright

URL = "https://app.dev.surgsmart.com/login"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs", "probe_surgsmart")
OUT_DIR = os.path.abspath(OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)


def _slim(el, page):
    """提取一个元素的精简描述（tag + 属性 + 文本），用于定位器选择。"""
    info = el.evaluate(
        """(node) => {
            const attrs = {};
            for (const a of node.attributes || []) attrs[a.name] = a.value;
            return {
                tag: node.tagName.toLowerCase(),
                type: node.getAttribute('type'),
                name: node.getAttribute('name'),
                id: node.getAttribute('id'),
                placeholder: node.getAttribute('placeholder'),
                ariaLabel: node.getAttribute('aria-label'),
                role: node.getAttribute('role'),
                autocomplete: node.getAttribute('autocomplete'),
                className: (node.getAttribute('class') || '').slice(0, 200),
                text: (node.innerText || '').trim().slice(0, 80),
                value: node.getAttribute('value'),
                href: node.getAttribute('href'),
                title: node.getAttribute('title'),
                dataTestId: node.getAttribute('data-testid'),
            };
        }"""
    )
    return info


def probe():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda exc: console_msgs.append(f"[pageerror] {exc}"))

        print(f"--> goto {URL}")
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"!! goto error: {e}")

        # 给 SPA/异步渲染 8s 缓冲
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        time.sleep(3)

        final_url = page.url
        title = page.title()
        html_path = os.path.join(OUT_DIR, "page.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
        shot_path = os.path.join(OUT_DIR, "page.png")
        page.screenshot(path=shot_path, full_page=True)

        report = {
            "url": final_url,
            "title": title,
            "inputs": [],
            "buttons": [],
            "forms": [],
            "iframes": [],
            "console": console_msgs[-30:],
            "snapshot_html_excerpt": "",
        }

        for handle in page.query_selector_all("input"):
            try:
                report["inputs"].append(_slim(handle, page))
            except Exception as e:
                print(f"input inspect error: {e}")

        for handle in page.query_selector_all("button"):
            try:
                report["buttons"].append(_slim(handle, page))
            except Exception as e:
                print(f"button inspect error: {e}")

        for handle in page.query_selector_all("form"):
            try:
                info = handle.evaluate(
                    """(node) => ({
                        action: node.getAttribute('action'),
                        method: node.getAttribute('method'),
                        id: node.getAttribute('id'),
                        className: (node.getAttribute('class') || '').slice(0, 200),
                    })"""
                )
                report["forms"].append(info)
            except Exception as e:
                print(f"form inspect error: {e}")

        for handle in page.query_selector_all("iframe"):
            try:
                info = handle.evaluate(
                    """(node) => ({
                        src: node.getAttribute('src'),
                        name: node.getAttribute('name'),
                        id: node.getAttribute('id'),
                    })"""
                )
                report["iframes"].append(info)
            except Exception as e:
                print(f"iframe inspect error: {e}")

        # 截取 body 内层可见文本片段（去掉大量空白）
        try:
            text = page.evaluate(
                "() => document.body ? document.body.innerText.replace(/\\s+/g, ' ').slice(0, 1500) : ''"
            )
            report["snapshot_html_excerpt"] = text
        except Exception:
            pass

        out_json = os.path.join(OUT_DIR, "report.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"--> report saved: {out_json}")
        print(f"--> screenshot:    {shot_path}")
        print(f"--> page html:     {html_path}")
        print(f"--> title={title!r} url={final_url}")
        print(f"--> inputs={len(report['inputs'])}  buttons={len(report['buttons'])}  forms={len(report['forms'])}  iframes={len(report['iframes'])}")

        browser.close()


if __name__ == "__main__":
    try:
        probe()
    except Exception as e:
        print(f"!! probe fatal: {e}", file=sys.stderr)
        raise
