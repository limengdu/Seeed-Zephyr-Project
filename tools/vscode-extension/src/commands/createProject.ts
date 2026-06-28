import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { Board, Catalog, Example } from "../model/types";
import { locateCli } from "../cli/cliLocator";
import { runCapture } from "../cli/cliBridge";

// Runs the create-project wizard, then calls the CLI to generate the project.
// 运行创建项目向导,然后调用 CLI 生成项目。
export async function createProject(
  repoRoot: string | undefined,
  catalog: Catalog | undefined,
  preset?: { board: Board; example?: Example },
): Promise<void> {
  if (!repoRoot || !catalog) {
    void vscode.window.showErrorMessage("No seeed-zephyr repository found.");
    return;
  }

  const board = preset?.board ?? (await pickBoard(catalog));
  if (!board) {
    return;
  }
  if (board.examples.length === 0) {
    void vscode.window.showErrorMessage(`${board.id} has no examples to create from.`);
    return;
  }
  const example = preset?.example ?? (await pickExample(board));
  if (!example) {
    return;
  }

  const parent = await vscode.window.showOpenDialog({
    canSelectFolders: true,
    canSelectFiles: false,
    canSelectMany: false,
    openLabel: "Select parent folder",
  });
  if (!parent || parent.length === 0) {
    return;
  }

  const name = await vscode.window.showInputBox({
    prompt: "Project folder name",
    value: `${board.id}_${example.demo}`,
  });
  if (!name) {
    return;
  }

  const output = path.join(parent[0].fsPath, name);
  const cli = locateCli(repoRoot);
  const result = await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: `Creating ${name}...` },
    () =>
      runCapture(cli, [
        "create",
        "--from",
        `${board.id}/${example.demo}`,
        "--board",
        board.id,
        "--output",
        output,
      ]),
  );

  if (!result.ok) {
    void vscode.window.showErrorMessage(`Create failed: ${result.message}`);
    return;
  }

  writeProjectSettings(output, repoRoot);

  const choice = await vscode.window.showInformationMessage(
    `Created project at ${output}`,
    "Open in New Window",
    "Add to Workspace",
  );
  if (choice === "Open in New Window") {
    void vscode.commands.executeCommand("vscode.openFolder", vscode.Uri.file(output), true);
  } else if (choice === "Add to Workspace") {
    vscode.workspace.updateWorkspaceFolders(
      vscode.workspace.workspaceFolders?.length ?? 0,
      0,
      { uri: vscode.Uri.file(output) },
    );
  }
}

// Records the source repo in the generated project so its status bar finds the CLI.
// 把来源仓库记录到生成的工程里,让它的状态栏能找到 CLI。
function writeProjectSettings(output: string, repoRoot: string): void {
  try {
    const vscodeDir = path.join(output, ".vscode");
    fs.mkdirSync(vscodeDir, { recursive: true });
    fs.writeFileSync(
      path.join(vscodeDir, "settings.json"),
      `${JSON.stringify({ "seeedZephyr.repoRoot": repoRoot }, null, 2)}\n`,
    );
  } catch {
    // Non-fatal: the user can set seeedZephyr.repoRoot manually.
  }
}

async function pickBoard(catalog: Catalog): Promise<Board | undefined> {
  const pick = await vscode.window.showQuickPick(
    catalog.boards
      .filter((board) => board.examples.length > 0)
      .map((board) => ({ label: board.displayName, description: board.id, board })),
    { placeHolder: "Select a board" },
  );
  return pick?.board;
}

async function pickExample(board: Board): Promise<Example | undefined> {
  const pick = await vscode.window.showQuickPick(
    board.examples.map((example) => ({
      label: example.demo,
      description: example.validationStatus,
      example,
    })),
    { placeHolder: "Select an example" },
  );
  return pick?.example;
}
