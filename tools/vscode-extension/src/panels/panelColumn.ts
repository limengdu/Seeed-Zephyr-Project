import * as vscode from "vscode";

// All Seeed webview panels open in the active editor group, so the detail view and the
// pin configurator appear as normal tabs in the current tab bar.
// 所有 Seeed webview 面板都开在当前编辑组里：详情页与引脚配置器作为当前标签栏里的普通标签页显示。
export const SEEED_PANEL_COLUMN = vscode.ViewColumn.Active;
