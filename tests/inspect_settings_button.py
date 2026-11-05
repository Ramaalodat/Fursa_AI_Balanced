from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",args=["--no-sandbox"])
 page=b.new_page(viewport={"width":1450,"height":920})
 page.goto("http://localhost:8502",wait_until="domcontentloaded")
 page.get_by_role("button",name="الإعدادات").wait_for(timeout=45000)
 buttons=page.get_by_role("button",name="الإعدادات")
 print("POP",buttons.count(),buttons.first.evaluate("e=>e.outerHTML.slice(0,3500)"))
 print("parents",buttons.first.evaluate("e=>e.parentElement.outerHTML.slice(0,4200)"))
 page.screenshot(path=r"C:\Users\Hb\Desktop\Fursa_AI_Balanced\tests\settings_before.png")
 b.close()
