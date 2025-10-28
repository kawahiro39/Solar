
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Set a common user agent to avoid being flagged as an unsupported browser
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Capture console messages
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))

        # Load the application
        import os
        file_path = os.path.abspath('index.html')
        await page.goto(f'file://{file_path}', wait_until='networkidle')

        print("Waiting for map to initialize...")
        try:
            # Wait for the map's internal canvas to be visible
            await page.wait_for_selector('div[aria-label="Map"] canvas', state='visible', timeout=15000)
            print("Map canvas is visible.")
        except Exception as e:
            print(f"Error waiting for map canvas: {e}")
            await page.screenshot(path='jules-scratch/verification/99_error_state.png')
            await browser.close()
            return

        # 1. Simulate drawing a polygon on the map
        print("Drawing polygon on map...")
        await page.click('button[title="Draw a polygon"]', timeout=5000)

        map_canvas_selector = 'div[aria-label="Map"]'
        await page.click(map_canvas_selector, position={'x': 300, 'y': 300})
        await page.wait_for_timeout(100)
        await page.click(map_canvas_selector, position={'x': 500, 'y': 300})
        await page.wait_for_timeout(100)
        await page.click(map_canvas_selector, position={'x': 500, 'y': 500})
        await page.wait_for_timeout(100)
        await page.click(map_canvas_selector, position={'x': 300, 'y': 500})
        await page.wait_for_timeout(100)
        await page.click(map_canvas_selector, position={'x': 300, 'y': 300})

        await page.wait_for_selector('#to-design-btn', state='visible')
        print("Polygon drawn.")
        await page.screenshot(path='jules-scratch/verification/02_polygon_drawn.png')
        print("Screenshot taken: 02_polygon_drawn.png")

        print("Switching to Design View...")
        await page.click('#to-design-btn')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='jules-scratch/verification/03_design_view.png')
        print("Screenshot taken: 03_design_view.png")

        print("Auto-correcting shape...")
        await page.click('#auto-correct-btn')
        await page.wait_for_timeout(500)
        await page.screenshot(path='jules-scratch/verification/04_auto_corrected.png')
        print("Screenshot taken: 04_auto_corrected.png")

        print("Placing panels...")
        await page.select_option('#panel-select', 'CS6.2-48TM-455')
        await page.click('#auto-place-btn')

        print("Waiting for simulation results...")
        await page.wait_for_selector('#results-list:has-text("kWh")', timeout=20000)
        print("Results are visible.")
        await page.screenshot(path='jules-scratch/verification/05_panels_placed.png')
        print("Screenshot taken: 05_panels_placed.png")

        print("Clicking Download PDF button...")
        await page.click('#download-pdf-btn')
        await page.wait_for_timeout(2000)

        print("Verification script finished successfully.")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
