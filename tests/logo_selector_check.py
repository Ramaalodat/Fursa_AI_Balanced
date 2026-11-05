from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",args=["--no-sandbox"])
 page=b.new_page(viewport={"width":1440,"height":850})
 page.goto("http://localhost:8502")
 page.get_by_role("button",name="عرض التقييم").wait_for(timeout=50000)
 im=page.locator('[data-testid="stImage"] img').first
 print("parent",im.evaluate("(e)=>e.closest('[data-testid=stColumn]').outerHTML.slice(0,1100)"))
 print("img",im.evaluate("(e)=>e.parentElement.outerHTML.slice(0,1100)"))
 print("headers",page.locator('div[data-testid="stHorizontalBlock"]:has(button[data-testid="stPopoverButton"])').count())
 print("columns",page.locator('div[data-testid="stColumn"]').count())
 b.close()
