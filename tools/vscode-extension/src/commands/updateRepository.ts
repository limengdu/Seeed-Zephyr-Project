import { spawn } from "child_process";
import * as vscode from "vscode";

interface GitResult {
  ok: boolean;
  stdout: string;
  stderr: string;
  message: string;
}

// Updates the repository currently used by the catalog, then refreshes the view.
// 更新目录当前使用的仓库，然后刷新视图。
export async function updateRepository(
  repoRoot: string | undefined,
  onUpdated: () => void,
): Promise<void> {
  if (!repoRoot) {
    void vscode.window.showErrorMessage("No seeed-zephyr repository found.");
    return;
  }

  const check = await runGit(repoRoot, ["rev-parse", "--is-inside-work-tree"]);
  if (!check.ok || check.stdout.trim() !== "true") {
    void vscode.window.showErrorMessage(`Not a Git repository: ${repoRoot}`);
    return;
  }

  // A detached checkout is a pinned release; Switch Version moves it to another one.
  // 游离签出表示固定在某个发布版本；用 Switch Version 切换到其他版本。
  const branch = await runGit(repoRoot, ["symbolic-ref", "-q", "HEAD"]);
  if (!branch.ok) {
    const tag = await runGit(repoRoot, ["describe", "--tags", "--exact-match"]);
    const pinned = tag.ok ? tag.stdout.trim() : "a fixed commit";
    void vscode.window.showInformationMessage(
      `The repository is pinned to ${pinned}. Use Switch Version to move to the latest release.`,
    );
    return;
  }

  const result = await vscode.window.withProgress<GitResult>(
    {
      location: vscode.ProgressLocation.Notification,
      title: "Updating Seeed Zephyr repository",
      cancellable: false,
    },
    () => runGit(repoRoot, ["pull", "--no-ff"]),
  );

  if (!result.ok) {
    void vscode.window.showErrorMessage(`Update failed: ${result.message}`);
    return;
  }

  onUpdated();
  void vscode.window.showInformationMessage("Repository updated. Catalog refreshed.");
}

// Runs one Git command in the repository and captures its output.
// 在仓库内运行一个 Git 命令并捕获输出。
function runGit(repoRoot: string, args: string[]): Promise<GitResult> {
  return new Promise((resolve) => {
    const child = spawn("git", args, { cwd: repoRoot });
    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", (error) => {
      resolve({ ok: false, stdout, stderr, message: error.message });
    });
    child.on("close", (code) => {
      const ok = code === 0;
      const message = ok
        ? stdout.trim() || stderr.trim()
        : firstUsefulLine(stderr) ||
          firstUsefulLine(stdout) ||
          `Exited with code ${code ?? "unknown"}`;
      resolve({ ok, stdout, stderr, message });
    });
  });
}

function firstUsefulLine(output: string): string {
  return output
    .split("\n")
    .map((line) => line.trim())
    .find((line) => line.length > 0) ?? "";
}
