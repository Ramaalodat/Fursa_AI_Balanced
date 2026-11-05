from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",args=["--no-sandbox"])
 pg=b.new_page(viewport={"width":1440,"height":900});pg.goto("http://localhost:8502");pg.get_by_role("button",name="عرض التقييم").wait_for(timeout=30000)
 im=pg.locator('[data-testid="stImageContainer"]').first
 print(im.evaluate('e=>{let x=e;return Array.from({length:9},()=>{let v=[x.tagName,x.getAttribute("data-testid"),x.className];x=x.parentElement;return v})}'))
 print(im.evaluate('e=>{let x=e;return Array.from({length:8},()=>{let v=[x.getAttribute("data-testid"),Math.round(x.getBoundingClientRect().width),Math.round(x.getBoundingClientRect().x)];x=x.parentElement;return v})}'))
 print("popover buttons",pg.locator('button[data-testid="stPopoverButton"]').count())
 print("selector",pg.locator('div[data-testid="stHorizontalBlock"]:has(button[data-testid="stPopoverButton"]) [data-testid="stImageContainer"]').count())
 b.close()
