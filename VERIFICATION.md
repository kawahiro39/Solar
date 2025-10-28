# Manual Verification Steps

Please use the following steps to manually verify the implemented features in a standard web browser.

## Instructions

1.  **Open `index.html`:** Open the file in a modern web browser.

2.  **Draw Polygons:**
    *   Use the "Draw a polygon" tool on the map to draw two separate, non-rectangular, rotated polygons on different roof surfaces.
    *   **[VERIFY]** The "設計画面へ" (To Design View) button appears.

3.  **Verify Overview Mode:**
    *   Click the "設計画面へ" button.
    *   **[VERIFY]** The design view opens in "Overview Mode". Both polygons are displayed, preserving their rotation and relative positions from the map. The view is oriented with geographic North facing up.

4.  **Enter and Verify Detail (Expanded) Mode:**
    *   Click inside one of the polygons to select it.
    *   **[VERIFY]** The selected polygon is highlighted, and its vertices (red dots) appear.
    *   Click on one of the edges of the selected polygon.
    *   **[VERIFY]** The view immediately switches to "Detail Mode".
    *   **[VERIFY]** Only the selected polygon is visible.
    *   **[VERIFY]** The polygon has been rotated and moved so that the edge you clicked (the "eave") is now a straight, horizontal line at the bottom of the group of drawn panels.
    *   **[VERIFY]** A "一覧へ戻る" (Back to Overview) button is now visible.

5.  **Test Panel Placement in Detail Mode:**
    *   In the "オフセット (m)" input, enter `0.1`.
    *   Click "パネルを自動配置" (Auto-place Panels).
    *   **[VERIFY]** Panels are placed within the straightened polygon. They are aligned with the horizontal eave and respect the offset boundary (dashed blue line).
    *   **[VERIFY]** The results section updates with a panel count and energy estimate.

6.  **Return to Overview:**
    *   Click the "一覧へ戻る" button.
    *   **[VERIFY]** The view returns to the "Overview Mode", showing both original polygons again.
    *   **[VERIFY]** The panels you just placed should be visible on the corresponding roof, correctly rotated and positioned within the original, un-straightened polygon.

7.  **Verify PDF Report:**
    *   Click "PDFをダウンロード" (Download PDF).
    *   **[VERIFY]** The downloaded PDF contains a screenshot of the **Overview Mode**, showing both roofs (one with panels). The second page should show the aggregated monthly energy data.

If all these points are confirmed, the implementation is successful.