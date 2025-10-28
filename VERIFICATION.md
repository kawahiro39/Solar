# Manual Verification Steps (Final)

This guide provides the definitive steps to verify that all recent bug fixes and feature changes have been correctly implemented.

## 1. Setup
*   **Open `index.html`** in a modern web browser.
*   Use the map tool to draw a **slightly irregular, 5-sided polygon** on a roof.
*   Draw a **second, irregular 4-sided polygon (quadrilateral)** on another roof nearby.
*   Click the **"設計画面へ"** (To Design View) button.

## 2. Verify New UI Flow and "Unfolded" View
*   **[VERIFY]** The design view should open immediately showing **"Roof 1"** (the 5-sided shape). There is no more "overview".
*   **[VERIFY]** The roof shape is displayed in an "unfolded" view, meaning one of its edges (the default eave) is drawn **horizontally**.
*   **[VERIFY]** Tabs for "Roof 1" and "Roof 2" are visible at the top.
*   Click the "Roof 2" tab.
*   **[VERIFY]** The view should switch to show the unfolded view of your 4-sided shape.
*   Click back to the "Roof 1" tab.

## 3. Verify Auto-Correction (for any polygon)
*   With the 5-sided "Roof 1" displayed, click the **"自動補正"** button.
*   **[VERIFY]** The shape should adjust itself to have crisp, 90-degree angles where appropriate. It should look "cleaner" and more rectilinear. The shape should **not** disappear or become a rectangle.

## 4. Verify Panel Placement and Coordinate Integrity
*   Click on a different edge of the now-corrected "Roof 1" to set a new eave.
*   **[VERIFY]** The view should re-rotate so the new eave is horizontal.
*   In the "オフセット (cm)" input, enter a value like `30`.
*   Click **"パネルを自動配置"**.
*   **[VERIFY]** Panels should fill the shape, aligned with the horizontal eave and respecting the 30cm offset. There should be no errors.
*   Switch to the "Roof 2" tab. **[VERIFY]** You see the empty, unfolded quadrilateral.
*   Switch back to the "Roof 1" tab. **[VERIFY]** The panels are still there, correctly placed on the unfolded shape.

## 5. Verify PDF Report (Panel Position)
*   With panels placed on "Roof 1", click **"PDFをダウンロード"**.
*   Open the generated PDF.
*   **[VERIFY]** The first page should show **both** original roof shapes (Roof 1 and Roof 2) in their correct geographic positions (rotated as they were on the map).
*   **[VERIFY]** Crucially, the solar panels must be rendered **correctly on the rotated "Roof 1" shape**. They should not be centered, misplaced, or overlapping.

If all the above points are confirmed, all reported issues have been successfully resolved.