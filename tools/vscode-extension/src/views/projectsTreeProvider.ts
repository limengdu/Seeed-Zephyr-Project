import * as path from "path";
import * as fs from "fs";
import * as vscode from "vscode";
import { displayBoard, displayPort } from "../commands/projectSettings";
import { resolveActiveProject } from "../projectDiscovery";
import { detectProjects } from "../statusBar";
import type { ProjectInfo } from "../statusBar";
import { ActionNode, CatalogNode, MessageNode, ProjectNode } from "./treeItems";

const ACTIVE_PROJECT_KEY = "seeedZephyr.activeProject";

export class ProjectsTreeProvider implements vscode.TreeDataProvider<CatalogNode> {
  private readonly _onDidChangeTreeData = new vscode.EventEmitter<void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private projects: ProjectInfo[] = [];
  private activeProjectPath: string | undefined;

  constructor(private readonly context: vscode.ExtensionContext) {
    this.load();
  }

  refresh(): void {
    this.load();
    this._onDidChangeTreeData.fire();
  }

  getActiveProject(): ProjectInfo | undefined {
    return this.findProject(this.activeProjectPath);
  }

  findProject(project: ProjectInfo | undefined): ProjectInfo | undefined;
  findProject(projectPath: string | undefined): ProjectInfo | undefined;
  findProject(projectOrPath: ProjectInfo | string | undefined): ProjectInfo | undefined {
    const projectPath = typeof projectOrPath === "string"
      ? projectOrPath
      : projectOrPath?.appDir;
    if (!projectPath) {
      return undefined;
    }
    return this.projects.find((project) => samePath(project.appDir, projectPath));
  }

  async selectProject(project: ProjectInfo): Promise<ProjectInfo | undefined> {
    const selected = this.findProject(project);
    if (!selected) {
      return undefined;
    }
    this.activeProjectPath = selected.appDir;
    await this.context.workspaceState.update(ACTIVE_PROJECT_KEY, selected.appDir);
    this._onDidChangeTreeData.fire();
    return selected;
  }

  private load(): void {
    const nextProjects = detectProjects();
    const addedProject = this.projects.length > 0
      ? nextProjects.find((project) => !this.findProject(project))
      : undefined;
    const savedProjectPath = this.context.workspaceState.get<string>(ACTIVE_PROJECT_KEY);
    const activeProject = resolveActiveProject(nextProjects, [
      addedProject?.appDir,
      this.activeProjectPath,
      savedProjectPath,
    ]);

    this.projects = nextProjects;
    this.activeProjectPath = activeProject?.appDir;
    void this.context.workspaceState.update(ACTIVE_PROJECT_KEY, this.activeProjectPath);
  }

  getTreeItem(node: CatalogNode): vscode.TreeItem {
    return node;
  }

  getChildren(node?: CatalogNode): CatalogNode[] {
    if (!node) {
      return this.projectNodes();
    }
    if (node instanceof ProjectNode) {
      const board = displayBoard(this.context, node.project);
      const port = displayPort(this.context, node.project);
      const actions: CatalogNode[] = [
        projectAction(
          "Select Board",
          "seeedZephyr.selectProjectBoard",
          "circuit-board",
          node.project,
          board,
        ),
      ];
      if (isGroveProject(node.project.appDir)) {
        actions.push(projectAction(
          "Configure Pins",
          "seeedZephyr.configurePins",
          "symbol-parameter",
          node.project,
        ));
      }
      actions.push(
        projectAction("Build Project", "seeedZephyr.projectBuild", "check", node.project),
        projectAction("Upload Project", "seeedZephyr.projectFlash", "arrow-up", node.project),
        projectAction("Select Port", "seeedZephyr.selectProjectPort", "plug", node.project, port),
        projectAction(
          "Upload and Monitor Project",
          "seeedZephyr.projectFlashMonitor",
          "run-all",
          node.project,
        ),
        projectAction("Monitor Project", "seeedZephyr.projectMonitor", "terminal", node.project),
      );
      return actions;
    }
    return [];
  }

  private projectNodes(): CatalogNode[] {
    const nodes: CatalogNode[] = [
      new ActionNode("Create Project", "seeedZephyr.createProject", "new-folder"),
      new ActionNode("Open Project", "seeedZephyr.openGenerated", "folder-opened"),
    ];
    if (this.projects.length > 0) {
      nodes.push(...this.projects.map((project) =>
        new ProjectNode(
          path.basename(project.appDir),
          project,
          displayBoard(this.context, project),
          displayPort(this.context, project),
          samePath(project.appDir, this.activeProjectPath),
        ),
      ));
    } else {
      nodes.push(new MessageNode("No project in the current workspace."));
    }
    return nodes;
  }
}

function projectAction(
  label: string,
  command: string,
  icon: string,
  project: ProjectInfo,
  description?: string,
): ActionNode {
  return new ActionNode(label, command, icon, description, undefined, [project]);
}

function samePath(left: string, right: string | undefined): boolean {
  return right !== undefined && path.resolve(left) === path.resolve(right);
}

function isGroveProject(appDir: string): boolean {
  const snapshot = path.join(appDir, "snapshot.json");
  if (fs.existsSync(snapshot)) {
    try {
      const data = JSON.parse(fs.readFileSync(snapshot, "utf-8")) as { source_asset?: unknown };
      if (
        typeof data.source_asset === "string" &&
        (data.source_asset.startsWith("grove/") || data.source_asset.includes("/grove/"))
      ) {
        return true;
      }
    } catch {
      return false;
    }
  }
  const example = path.join(appDir, "example.yaml");
  if (!fs.existsSync(example)) {
    return false;
  }
  return fs.readFileSync(example, "utf-8").includes("kind: grove");
}
