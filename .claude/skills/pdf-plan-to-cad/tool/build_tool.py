#!/usr/bin/env python3
"""Builds the web tool from plan_area_template.html:
  plan-area.html            page body only (what the Artifact tool publishes; it adds <html>/<head>)
  plan-area-standalone.html full document to open locally with a double click (needs internet for pdf.js)
The example plan (sample_plan.pdf, made by make_sample.py) is embedded as base64.

    python3 build_tool.py            # run from this folder
"""
import base64
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    sample = os.path.join(HERE, "sample_plan.pdf")
    if not os.path.exists(sample):
        subprocess.check_call([sys.executable, os.path.join(HERE, "make_sample.py"), sample])
    b64 = base64.b64encode(open(sample, "rb").read()).decode()
    tpl = open(os.path.join(HERE, "plan_area_template.html"), encoding="utf-8").read()
    assert "__SAMPLE_PDF_BASE64__" in tpl
    body = tpl.replace("__SAMPLE_PDF_BASE64__", b64)
    with open(os.path.join(HERE, "plan-area.html"), "w", encoding="utf-8") as f:
        f.write(body)
    full = ('<!doctype html>\n<html lang="ar" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '</head>\n<body>\n' + body + '\n</body>\n</html>\n')
    with open(os.path.join(HERE, "plan-area-standalone.html"), "w", encoding="utf-8") as f:
        f.write(full)
    print("wrote plan-area.html and plan-area-standalone.html", len(body) // 1024, "KB")


if __name__ == "__main__":
    main()
