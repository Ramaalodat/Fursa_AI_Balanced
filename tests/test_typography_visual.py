from playwright.sync_api import sync_playwright
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding="utf-8")
root=Path(__file__).resolve().parent
out=root/"previews"
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",args=["--no-sandbox"])
    for lang in ("ar",):
        page=browser.new_page(viewport={"width":1450,"height":1050},device_scale_factor=1)
        page.goto("http://localhost:8502",wait_until="domcontentloaded",timeout=30000)
        submit=page.get_by_role("button",name="عرض التقييم")
        submit.wait_for(timeout=55000)
        if lang=="en":
            # Select language from the top-right control.
            page.locator('[data-testid="stSelectbox"]').first.click()
            page.get_by_text("English",exact=True).last.click()
            submit=page.get_by_role("button",name="View assessment")
            submit.wait_for(timeout=30000)
        submit.click()
        if lang=="ar":
            page.get_by_text("نتيجة التقييم",exact=True).wait_for(timeout=35000)
        else:
            page.get_by_text("Assessment result",exact=True).wait_for(timeout=35000)
        page.locator(".f-grid").screenshot(path=str(out/f"stats_{lang}.png"))
        print(lang,"STAT FONT",page.locator(".f-stat > span").first.evaluate("x=>getComputedStyle(x).fontSize"))
        print(lang,"NUMBER FONT",page.locator(".f-stat strong span").first.evaluate("x=>getComputedStyle(x).fontSize"))
        page.get_by_role("tab",name=("خطة التطوير" if lang=="ar" else "Development plan")).click()
        page.locator(".f-action").first.wait_for(timeout=30000)
        page.locator(".f-action").first.screenshot(path=str(out/f"action_{lang}.png"))
        print(lang,"ACTION FONT",page.locator(".f-action p").first.evaluate("x=>getComputedStyle(x).fontSize"))
        page.get_by_role("tab",name=("أداء النموذج" if lang=="ar" else "Model performance")).click()
        page.get_by_text(("مقارنة الخوارزميات" if lang=="ar" else "Algorithm comparison"),exact=True).scroll_into_view_if_needed()
        page.locator(".f-chart-axis-label").wait_for(timeout=35000)
        page.locator(".f-chart-axis-label").scroll_into_view_if_needed()
        page.screenshot(path=str(out/f"chart_{lang}.png"),full_page=False)
        print(lang,"LABEL",page.locator(".f-chart-axis-label").inner_text())
        print(lang,"ERRORS",page.locator('[data-testid="stException"]').count())
        page.close()
    mobile=browser.new_page(viewport={"width":390,"height":850},device_scale_factor=1)
    mobile.goto("http://localhost:8502")
    mobile.get_by_role("button",name="عرض التقييم").wait_for(timeout=45000)
    mobile.get_by_role("button",name="عرض التقييم").click()
    mobile.get_by_text("نتيجة التقييم",exact=True).wait_for(timeout=35000)
    mobile.locator(".f-grid").screenshot(path=str(out/"stats_mobile.png"))
    print("MOBILE", mobile.evaluate("({scroll:document.documentElement.scrollWidth,view:innerWidth})"))
    browser.close()
