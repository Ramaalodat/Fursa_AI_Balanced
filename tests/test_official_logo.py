from playwright.sync_api import sync_playwright
from pathlib import Path
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",args=["--no-sandbox"])
 for lang in ("ar","en"):
  page=b.new_page(viewport={"width":1440,"height":900})
  page.goto("http://localhost:8502")
  page.get_by_role("button",name="عرض التقييم").wait_for(timeout=50000)
  if lang=="en":
   page.locator('[data-testid="stSelectbox"]').first.click()
   page.get_by_text("English",exact=True).last.click()
   page.get_by_role("button",name="View assessment").wait_for(timeout=20000)
  page.screenshot(path=rf"C:\Users\Hb\Desktop\Fursa_AI_Balanced\tests\official_logo_{lang}.png",full_page=False)
  print(lang, page.locator("img").count(), page.locator('[data-testid="stException"]').count())
  page.close()
 b.close()
