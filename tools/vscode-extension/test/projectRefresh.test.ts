import * as assert from "node:assert/strict";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { test } from "node:test";
import { openGenerated } from "../src/commands/openGenerated";
import { discoverProjects } from "../src/projectDiscovery";
import { watchProjectFiles } from "../src/projectWatcher";
import { Uri, watchers, window, workspace } from "./mocks/vscode";

test("import rescans an already-open folder after project files appear", async () => {
  const appDir = fs.mkdtempSync(path.join(os.tmpdir(), "seeed-project-import-"));
  workspace.workspaceFolders = [{ uri: Uri.file(appDir) }];
  window.selectedFolders = [Uri.file(appDir)];
  let projects = discoverProjects([appDir]);
  assert.deepEqual(projects, []);

  fs.writeFileSync(path.join(appDir, "snapshot.json"), JSON.stringify({ board: "xiao_stm32c5" }));
  await openGenerated(() => {
    projects = discoverProjects(workspace.workspaceFolders.map((folder) => folder.uri.fsPath));
  });

  assert.deepEqual(projects, [{ appDir, board: "xiao_stm32c5" }]);
  assert.equal(workspace.workspaceFolders.length, 1);
});

test("import refreshes the project list after adding a workspace folder", async () => {
  const appDir = fs.mkdtempSync(path.join(os.tmpdir(), "seeed-project-add-"));
  workspace.workspaceFolders = [];
  window.selectedFolders = [Uri.file(appDir)];
  fs.writeFileSync(path.join(appDir, "snapshot.json"), JSON.stringify({ board: "xiao_rp2350" }));
  let projects = discoverProjects([]);

  await openGenerated(() => {
    projects = discoverProjects(workspace.workspaceFolders.map((folder) => folder.uri.fsPath));
  });

  assert.deepEqual(projects, [{ appDir, board: "xiao_rp2350" }]);
});

test("cancelled import leaves the project list unchanged", async () => {
  window.selectedFolders = undefined;
  let refreshes = 0;
  await openGenerated(() => { refreshes += 1; });
  assert.equal(refreshes, 0);
});

test("project markers appearing, changing and disappearing update discovery", () => {
  const appDir = fs.mkdtempSync(path.join(os.tmpdir(), "seeed-project-markers-"));
  const snapshot = path.join(appDir, "snapshot.json");
  workspace.workspaceFolders = [{ uri: Uri.file(appDir) }];
  let projects = discoverProjects([appDir]);
  const subscription = watchProjectFiles(() => { projects = discoverProjects([appDir]); });
  const watcher = watchers.at(-1)!;

  fs.writeFileSync(snapshot, JSON.stringify({ board: "xiao_stm32c5" }));
  watcher.emit("create", snapshot);
  assert.deepEqual(projects, [{ appDir, board: "xiao_stm32c5" }]);

  fs.writeFileSync(snapshot, JSON.stringify({ board: "xiao_rp2350" }));
  watcher.emit("change", snapshot);
  assert.deepEqual(projects, [{ appDir, board: "xiao_rp2350" }]);

  fs.renameSync(snapshot, path.join(appDir, "snapshot.saved"));
  watcher.emit("delete", snapshot);
  assert.deepEqual(projects, []);
  subscription.dispose();
});

test("plain Zephyr apps appear when both project files become available", () => {
  const appDir = fs.mkdtempSync(path.join(os.tmpdir(), "seeed-project-plain-"));
  workspace.workspaceFolders = [{ uri: Uri.file(appDir) }];
  let projects = discoverProjects([appDir]);
  const subscription = watchProjectFiles(() => { projects = discoverProjects([appDir]); });
  const watcher = watchers.at(-1)!;
  const cmake = path.join(appDir, "CMakeLists.txt");
  const config = path.join(appDir, "prj.conf");

  fs.writeFileSync(cmake, "project(app)");
  watcher.emit("create", cmake);
  assert.deepEqual(projects, []);
  fs.writeFileSync(config, "CONFIG_GPIO=y");
  watcher.emit("create", config);
  assert.deepEqual(projects, [{ appDir, board: undefined }]);
  subscription.dispose();
});

test("build-directory files do not trigger project rescans", () => {
  const appDir = fs.mkdtempSync(path.join(os.tmpdir(), "seeed-project-build-"));
  workspace.workspaceFolders = [{ uri: Uri.file(appDir) }];
  let refreshes = 0;
  const subscription = watchProjectFiles(() => { refreshes += 1; });
  const watcher = watchers.at(-1)!;
  for (const event of ["create", "change", "delete"] as const) {
    watcher.emit(event, path.join(appDir, "build", "CMakeLists.txt"));
  }
  assert.equal(refreshes, 0);
  subscription.dispose();
});

test("the file watcher follows workspace folders added after registration", () => {
  workspace.workspaceFolders = [];
  let projects = discoverProjects([]);
  const subscription = watchProjectFiles(() => {
    projects = discoverProjects(workspace.workspaceFolders.map((folder) => folder.uri.fsPath));
  });
  const appDir = fs.mkdtempSync(path.join(os.tmpdir(), "seeed-project-workspace-"));
  const snapshot = path.join(appDir, "snapshot.json");
  workspace.workspaceFolders = [{ uri: Uri.file(appDir) }];
  fs.writeFileSync(snapshot, JSON.stringify({ board: "xiao_nrf54lm20a" }));
  watchers.at(-1)!.emit("create", snapshot);
  assert.deepEqual(projects, [{ appDir, board: "xiao_nrf54lm20a" }]);
  subscription.dispose();
});

test("disposing the file watcher releases its refresh subscriptions", () => {
  const appDir = fs.mkdtempSync(path.join(os.tmpdir(), "seeed-project-dispose-"));
  workspace.workspaceFolders = [{ uri: Uri.file(appDir) }];
  let refreshes = 0;
  const subscription = watchProjectFiles(() => { refreshes += 1; });
  const watcher = watchers.at(-1)!;
  subscription.dispose();
  watcher.emit("create", path.join(appDir, "snapshot.json"));
  assert.equal(refreshes, 0);
});
