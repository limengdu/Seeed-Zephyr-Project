import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

// Opens a previously generated project, checking for its snapshot.json receipt.
// 打开一个之前生成的项目,并检查它的 snapshot.json 收据。
export async function openGenerated(): Promise<void> {
  const folder = await vscode.window.showOpenDialog({
    canSelectFolders: true,
    canSelectFiles: false,
    canSelectMany: false,
    openLabel: "Open generated project",
  });
  if (!folder || folder.length === 0) {
    return;
  }

  const dir = folder[0].fsPath;
  if (!fs.existsSync(path.join(dir, "snapshot.json"))) {
    const proceed = await vscode.window.showWarningMessage(
      "No snapshot.json found. This may not be a seeed-zephyr generated project.",
      "Open Anyway",
    );
    if (proceed !== "Open Anyway") {
      return;
    }
  }

  void vscode.commands.executeCommand("vscode.openFolder", vscode.Uri.file(dir), true);
}
