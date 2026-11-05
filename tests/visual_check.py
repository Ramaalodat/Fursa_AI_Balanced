from pathlib import Path
from playwright.sync_api import sync_playwright
import sys
sys.stdout.reconfigure(encoding="utf-8")
output=Path(__file__).resolve().parent / "previews"
output.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",args=["--no-sandbox"])
    page=browser.new_page(viewport={"width":1440,"height":1000},device_scale_factor=1)
    page_errors=[]
    page.on("pageerror",lambda err:page_errors.append(str(err)))
    page.goto("http://localhost:8502", wait_until="domcontentloaded", timeout=30000)
    page.get_by_role("button",name="عرض التقييم").wait_for(timeout=60000)
    page.wait_for_timeout(700)
    page.screenshot(path=str(output/"desktop.png"),full_page=False)
    page.locator('[data-testid="stNumberInput"]').first.scroll_into_view_if_needed()
    page.screenshot(path=str(output/"inputs.png"),full_page=False)
    print("INPUTS",page.locator('[data-testid="stNumberInput"]').count(),
          "SLIDERS",page.locator('[data-testid="stSlider"]').count(),flush=True)
    page.get_by_role("button",name="عرض التقييم").click()
    page.get_by_text("نتيجة التقييم",exact=True).wait_for(timeout=40000)
    page.locator(".f-result").screenshot(path=str(output/"result.png"))
    page.get_by_role("tab",name="أداء النموذج").click()
    page.get_by_text("أداء النموذج والتحليل").wait_for(timeout=40000)
    page.wait_for_timeout(1000)
    page.screenshot(path=str(output/"evaluation.png"),full_page=False)
    print("CHARTS",page.locator('img').count(),"ERRORS",page.locator('[data-testid="stException"]').count(), "JS",page_errors[:2],flush=True)
    mobile=browser.new_page(viewport={"width":390,"height":845},device_scale_factor=1)
    mobile.goto("http://localhost:8502",wait_until="domcontentloaded",timeout=30000)
    mobile.get_by_role("button",name="عرض التقييم").wait_for(timeout=60000)
    mobile.wait_for_timeout(600)
    mobile.screenshot(path=str(output/"mobile.png"),full_page=False)
    print("MOBILE",mobile.evaluate("({scroll:document.documentElement.scrollWidth,window:innerWidth})"),
          "ERRORS",mobile.locator('[data-testid="stException"]').count(),flush=True)
    browser.close()
