import * as path from "path";
import * as vscode from "vscode";

// Watches project markers at the current workspace-folder roots.
// 监听当前工作区根目录中的工程标识文件。
export function watchProjectFiles(onChanged: () => void): vscode.Disposable {
  const watcher = vscode.workspace.createFileSystemWatcher(
    "**/{snapshot.json,CMakeLists.txt,prj.conf}",
  );
  const refresh = (uri: vscode.Uri): void => {
    const parent = path.dirname(uri.fsPath);
    if ((vscode.workspace.workspaceFolders ?? []).some((folder) =>
      path.resolve(folder.uri.fsPath) === path.resolve(parent)
    )) {
      onChanged();
    }
  };
  return vscode.Disposable.from(
    watcher,
    watcher.onDidCreate(refresh),
    watcher.onDidChange(refresh),
    watcher.onDidDelete(refresh),
  );
}
