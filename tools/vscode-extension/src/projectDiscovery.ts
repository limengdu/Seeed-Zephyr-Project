import * as fs from "fs";
import * as path from "path";

export interface ProjectInfo {
  appDir: string;
  board: string | undefined;
}

export interface ProjectFileReader {
  exists(file: string): boolean;
  readText(file: string): string;
}

const localFiles: ProjectFileReader = {
  exists: (file) => fs.existsSync(file),
  readText: (file) => fs.readFileSync(file, "utf-8"),
};

// Returns every Zephyr project found at the supplied workspace-folder roots.
// 返回在给定工作区根目录中发现的全部 Zephyr 项目。
export function discoverProjects(
  directories: readonly string[],
  files: ProjectFileReader = localFiles,
): ProjectInfo[] {
  return directories.flatMap((dir) => {
    const project = discoverProject(dir, files);
    return project ? [project] : [];
  });
}

// Selects the first project matching the preferred paths, then falls back to the first project.
// 按路径优先级选择项目；没有匹配项时使用列表中的第一个项目。
export function resolveActiveProject(
  projects: readonly ProjectInfo[],
  preferredPaths: readonly (string | undefined)[],
): ProjectInfo | undefined {
  for (const preferredPath of preferredPaths) {
    if (!preferredPath) {
      continue;
    }
    const project = projects.find((candidate) =>
      path.resolve(candidate.appDir) === path.resolve(preferredPath)
    );
    if (project) {
      return project;
    }
  }
  return projects[0];
}

function discoverProject(
  dir: string,
  files: ProjectFileReader,
): ProjectInfo | undefined {
  const snapshot = path.join(dir, "snapshot.json");
  if (files.exists(snapshot)) {
    return { appDir: dir, board: readSnapshotBoard(snapshot, files) };
  }
  if (
    files.exists(path.join(dir, "CMakeLists.txt")) &&
    files.exists(path.join(dir, "prj.conf"))
  ) {
    return { appDir: dir, board: undefined };
  }
  return undefined;
}

function readSnapshotBoard(
  file: string,
  files: ProjectFileReader,
): string | undefined {
  try {
    const data = JSON.parse(files.readText(file)) as { board?: unknown };
    return typeof data.board === "string" ? data.board : undefined;
  } catch {
    return undefined;
  }
}
