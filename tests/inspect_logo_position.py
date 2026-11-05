from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",args=["--no-sandbox"])
 page=b.new_page(viewport={"width":1440,"height":850})
 page.goto("http://localhost:8502")
 page.get_by_role("button",name="عرض التقييم").wait_for(timeout=50000)
 page.wait_for_timeout(2600)
 print("images",page.locator('img').count())
 print("loc",page.locator('[data-testid="stImage"] img').first.evaluate("(el)=>({width:el.naturalWidth,rect:el.getBoundingClientRect().toJSON()})"))
 page.screenshot(path=r"C:\Users\Hb\Desktop\Fursa_AI_Balanced\tests\official_logo_ar_final.png",full_page=False)
 b.close()
