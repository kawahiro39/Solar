# Manual Verification Steps

Due to persistent issues with running Google Maps in a headless browser environment, automated Playwright verification has been unsuccessful. Please use the following steps to manually verify the implemented features in a standard web browser.

## Instructions

1.  **Open the `index.html` File:** Open the `index.html` file directly in a modern web browser (like Chrome, Firefox, or Edge).

2.  **Verify Map View (Step 1 Features):**
    *   **[VERIFY]** The map should load, centered on Tokyo.
    *   **[VERIFY]** The view should be a top-down satellite view. Try to tilt the map; it should not be possible.
    *   Click the "Draw a polygon" button on the map.
    *   **[VERIFY]** Draw one complete, enclosed shape (e.g., a rectangle) on a roof.
    *   **[VERIFY]** The drawing tool should remain active. Draw a second, separate polygon on another roof.
    *   **[VERIFY]** The "設計画面へ" (To Design View) button should now be visible.

3.  **Verify Design View (Step 2, 3, 4 Features):**
    *   Click the "設計画面へ" button.
    *   **[VERIFY]** A new view with a white canvas should appear, replacing the map.
    *   **[VERIFY]** Both polygons you drew should be visible on the canvas, maintaining their relative positions and sizes.
    *   **[VERIFY]** The entire drawing should be rotated so that the geographic North is pointing towards the top of your screen.

4.  **Verify Interaction and Panel Placement (Step 5, 6 Features):**
    *   **[VERIFY]** Click inside one of the polygons. It should become highlighted (a slightly different shade of grey/blue), indicating it's selected. Its vertices should appear as red dots.
    *   **[VERIFY]** Click on one of the edges (not a corner) of the selected polygon. The edge should turn into a thick green line, indicating it has been set as the "eave".
    *   In the "オフセット (m)" input field, ensure the value is `0.2`.
    *   Select a panel model from the dropdown.
    *   Click the "パネルを自動配置" (Auto-place Panels) button.
    *   **[VERIFY]** Solar panels should appear inside the selected roof area.
    *   **[VERIFY]** The panels should be aligned horizontally with the green eave you selected.
    *   **[VERIFY]** The panels should not be placed right up to the edge, but should respect the 0.2m offset (a dashed blue line shows the placement area).
    *   **[VERIFY]** The "設置パネル枚数" and "年間想定発電量" in the results section should update with values greater than 0.

5.  **Verify PDF Report (Step 7 Feature):**
    *   Click the "PDFをダウンロード" (Download PDF) button.
    *   **[VERIFY]** A PDF file named `simulation_report.pdf` should be downloaded.
    *   Open the PDF. It should contain the canvas layout on the first page and a monthly energy production chart on the second page.

If all these verification points pass, the implementation is successful.