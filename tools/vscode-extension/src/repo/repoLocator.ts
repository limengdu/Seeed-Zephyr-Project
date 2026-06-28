import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

// Returns true when a directory looks like the seeed-zephyr repository root.
// 当目录看起来像 seeed-zephyr 仓库根时返回 true。
export function isRepoRoot(dir: string): boolean {
  try {
    return fs.statSync(path.join(dir, "metadata", "boards")).isDirectory();
  } catch {
    return false;
  }
}

// Locates the repository root from configuration or open workspace folders.
// 从配置或打开的工作区文件夹中定位仓库根。
export function locateRepoRoot(): string | undefined {
  const configured = vscode.workspace
    .getConfiguration("seeedZephyr")
    .get<string>("repoRoot");
  if (configured && isRepoRoot(configured)) {
    return configured;
  }

  const folders = vscode.workspace.workspaceFolders ?? [];
  // Prefer a folder that also carries examples/ (a full repository clone).
  // 优先选择同时含 examples/ 的文件夹(完整仓库克隆)。
  for (const folder of folders) {
    const root = folder.uri.fsPath;
    if (isRepoRoot(root) && fs.existsSync(path.join(root, "examples", "boards"))) {
      return root;
    }
  }
  for (const folder of folders) {
    if (isRepoRoot(folder.uri.fsPath)) {
      return folder.uri.fsPath;
    }
  }
  return undefined;
}
