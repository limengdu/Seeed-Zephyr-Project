import * as vscode from "vscode";

// All Seeed webview panels open in this one editor group, so the detail view and the
// pin configurator appear as tabs in the same tab bar (switch between them), instead of
// separate columns or new windows.
// 所有 Seeed webview 面板都开在这一个编辑组里：详情页与引脚配置器成为同一条标签栏上的
// 标签页（点击切换），而不是各占一栏或新开窗口。
export const SEEED_PANEL_COLUMN = vscode.ViewColumn.Two;
