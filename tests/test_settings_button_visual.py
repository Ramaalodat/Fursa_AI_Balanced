from playwright.sync_api import sync_playwright
from pathlib import Path
output=Path(r"C:\Users\Hb\Desktop\Fursa_AI_Balanced\tests")
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",args=["--no-sandbox"])
 for width in (1450,390):
  page=b.new_page(viewport={"width":width,"height":900})
  page.goto("http://localhost:8502",wait_until="domcontentloaded")
  button=page.get_by_role("button",name="الإعدادات")
  button.wait_for(timeout=45000)
  page.wait_for_timeout(800)
  button.screenshot(path=str(output/f"settings_button_{width}.png"))
  print("SIZE",width,"visible",button.is_visible(),"text",button.inner_text(),
    "icon",button.locator('[data-testid="stIconMaterial"]').count())
  if button.locator('[data-testid="stIconMaterial"]').count():
   print("icon_display",button.locator('[data-testid="stIconMaterial"]').first.evaluate("e=>getComputedStyle(e).display"))
  print("OVERFLOW",page.evaluate("({doc:document.documentElement.scrollWidth,win:innerWidth})"))
  button.click()
  page.get_by_text("تفضيلات العرض",exact=True).wait_for(timeout=15000)
  print("OPENED",page.get_by_text("تفضيلات العرض",exact=True).is_visible())
  page.screenshot(path=str(output/f"settings_open_{width}.png"),full_page=False)
  page.close()
 b.close()
