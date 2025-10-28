
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        import os
        file_path = os.path.abspath('index.html')
        await page.goto(f'file://{file_path}', wait_until='networkidle')

        print("Waiting for map to initialize...")
        await page.wait_for_selector('div[aria-label="Map"] canvas', state='visible', timeout=15000)
        print("Map canvas is visible.")

        # 1. Draw two polygons
        print("Drawing polygons...")
        await page.click('button[title="Draw a polygon"]', timeout=5000)
        map_canvas_selector = 'div[aria-label="Map"]'

        # Polygon 1
        await page.click(map_canvas_selector, position={'x': 200, 'y': 200})
        await page.click(map_canvas_selector, position={'x': 400, 'y': 200})
        await page.click(map_canvas_selector, position={'x': 400, 'y': 400})
        await page.click(map_canvas_selector, position={'x': 200, 'y': 400})
        await page.click(map_canvas_selector, position={'x': 200, 'y': 200})

        # Polygon 2
        await page.click(map_canvas_selector, position={'x': 500, 'y': 500})
        await page.click(map_canvas_selector, position={'x': 700, 'y': 500})
        await page.click(map_canvas_selector, position={'x': 700, 'y': 700})
        await page.click(map_canvas_selector, position={'x': 500, 'y': 700})
        await page.click(map_canvas_selector, position={'x': 500, 'y': 500})

        await page.wait_for_selector('#to-design-btn', state='visible')

        # 2. Switch to Design View
        print("Switching to Design View...")
        await page.click('#to-design-btn')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='jules-scratch/verification/01_design_view_rotated.png')
        print("Screenshot 1 taken: Design view with rotated polygons.")

        # 3. Select first roof, set eave, place panels
        print("Interacting with the first roof...")
        # Click on the first roof (approximating its new position after rotation)
        await page.click('#design-canvas', position={'x': 300, 'y': 300})
        # Click on an edge to set it as the eave (approximating)
        await page.click('#design-canvas', position={'x': 300, 'y': 400})

        await page.fill('#offset-input', '0.1')
        await page.click('#auto-place-btn')

        # Wait for simulation (a simple timeout is often enough for local processing)
        await page.wait_for_timeout(1500)

        await page.screenshot(path='jules-scratch/verification/02_panels_placed.png')
        print("Screenshot 2 taken: Panels placed on the selected roof.")

        print("Verification script finished successfully.")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
