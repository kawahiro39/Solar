from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Get the absolute path to the index.html file
        file_path = os.path.abspath('index.html')

        # Go to the local HTML file
        page.goto(f'file://{file_path}')

        # Wait for the map to be visible
        page.wait_for_selector('#map-container')

        # Take a screenshot of the initial view
        page.screenshot(path='jules-scratch/verification/01_initial_view.png')

        browser.close()

if __name__ == '__main__':
    run()
