import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

// Opens a project folder and offers the same window choices used after creation.
// 打开项目文件夹,并提供与创建完成后相同的窗口选择。
export async function openGenerated(): Promise<void> {
  const folder = await vscode.window.showOpenDialog({
    canSelectFolders: true,
    canSelectFiles: false,
    canSelectMany: false,
    openLabel: "Open project",
  });
  if (!folder || folder.length === 0) {
    return;
  }

  const dir = folder[0].fsPath;
  if (!isKnownProjectFolder(dir)) {
    const proceed = await vscode.window.showWarningMessage(
      "No generated project receipt or Zephyr app files were found. This folder may still be opened.",
      "Continue",
    );
    if (proceed !== "Continue") {
      return;
    }
  }

  await openProjectFolder(dir);
}

function isKnownProjectFolder(dir: string): boolean {
  return (
    fs.existsSync(path.join(dir, "snapshot.json")) ||
    (
      fs.existsSync(path.join(dir, "CMakeLists.txt")) &&
      fs.existsSync(path.join(dir, "prj.conf"))
    )
  );
}

async function openProjectFolder(dir: string): Promise<void> {
  const choice = await vscode.window.showInformationMessage(
    `Open project at ${dir}`,
    "Open in New Window",
    "Add to Workspace",
  );
  if (choice === "Open in New Window") {
    void vscode.commands.executeCommand("vscode.openFolder", vscode.Uri.file(dir), true);
  } else if (choice === "Add to Workspace") {
    const inserted = vscode.workspace.updateWorkspaceFolders(
      vscode.workspace.workspaceFolders?.length ?? 0,
      0,
      { uri: vscode.Uri.file(dir) },
    );
    if (!inserted) {
      void vscode.window.showErrorMessage("Project folder could not be added to this workspace.");
    }
  }
}
