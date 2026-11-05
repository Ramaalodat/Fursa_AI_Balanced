from playwright.sync_api import sync_playwright
from pathlib import Path
out=Path(__file__).resolve().parent
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",args=["--no-sandbox"])
 for w in [1440,390]:
  page=b.new_page(viewport={"width":w,"height":900})
  page.goto("http://localhost:8502",wait_until="domcontentloaded")
  page.get_by_role("button",name="عرض التقييم").wait_for(timeout=45000)
  page.get_by_role("button",name="عرض التقييم").click()
  page.get_by_text("نتيجة التقييم",exact=True).wait_for(timeout=45000)
  page.get_by_role("tab",name="خطة التطوير").click()
  page.get_by_role("checkbox").first.wait_for(timeout=35000)
  for i in range(page.get_by_role("checkbox").count()):
   page.get_by_role("checkbox").nth(i).check(force=True)
  panel=page.locator(".f-completion-card")
  panel.wait_for(timeout=25000)
  panel.scroll_into_view_if_needed()
  page.wait_for_timeout(450)
  page.screenshot(path=str(out/f"progress_complete_{w}.png"))
  print("w",w,"count",page.get_by_role("checkbox").count(),
        "banner",panel.count(),"overflow",page.evaluate("document.documentElement.scrollWidth-innerWidth"),
        "errors",page.locator('[data-testid="stException"]').count())
  page.close()
 b.close()
