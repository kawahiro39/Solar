# Manual Verification Steps

Please use the following steps to manually verify all recent changes.

## 1. Setup
*   **Open `index.html`** in a modern web browser.
*   Use the map tool to draw a **slightly irregular, non-rectangular quadrilateral** (a 4-sided shape) on a roof.
*   Draw a **second, more complex polygon (e.g., 5 or 6 sides)** on another roof nearby.
*   Click the **"設計画面へ"** button.

## 2. Verify Offset Fixes
*   In the Design View (Overview Mode), click to select your **irregular quadrilateral**.
*   **[VERIFY]** The "オフセット (cm)" label is displayed, and the default value is "20".
*   Look at the dashed blue line representing the offset. **[VERIFY]** It should be drawn clearly **inside** the polygon.
*   Change the offset value to "50". **[VERIFY]** The dashed line should move further inward.

## 3. Verify Auto-Correction and Drawing Integrity
*   With the irregular quadrilateral still selected, click the **"自動補正"** button.
*   **[VERIFY]** The shape should instantly transform into a **perfect rectangle**.
*   Drag one of the corners of this new rectangle to a new position.
*   Click the **"一覧へ戻る"** button (if you were in detail view) or simply deselect the object.
*   Reselect the same roof object. **[VERIFY]** Your edit should be preserved, and the shape should not be distorted.

## 4. Verify "Unfolded" Detail Mode
*   Click on one of the edges of the corrected rectangle to set it as the eave.
*   **[VERIFY]** The view immediately switches to "Detail Mode".
*   **[VERIFY]** The rectangle is now drawn with the selected eave edge perfectly **horizontal**.
*   Drag a vertex of the rectangle in this mode.
*   Click the **"一覧へ戻る"** button.
*   **[VERIFY]** The main overview is shown again. The rectangle should now have your edited shape, correctly rotated back to its original position. **The shape must not be distorted.**

## 5. Verify Panel Placement
*   Select the corrected rectangle again and click the eave edge to enter "Detail Mode".
*   Click **"パネルを自動配置"**.
*   **[VERIFY]** Panels should fill the rectangle, aligned with the horizontal eave, respecting the 50cm offset.
*   Click **"一覧へ戻る"**.
*   **[VERIFY]** The panels are correctly shown on the rotated rectangle in the overview.

If all these points are confirmed, the implementation is successful.