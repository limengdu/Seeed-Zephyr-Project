import * as path from "node:path";

type FileUri = { fsPath: string };
type Listener = (uri: FileUri) => void;

export class Disposable {
  constructor(private readonly cleanup: () => void = () => {}) {}

  dispose(): void {
    this.cleanup();
  }

  static from(...items: Disposable[]): Disposable {
    return new Disposable(() => items.forEach((item) => item.dispose()));
  }
}

export class FileWatcher extends Disposable {
  readonly listeners = {
    create: new Set<Listener>(),
    change: new Set<Listener>(),
    delete: new Set<Listener>(),
  };

  onDidCreate = (listener: Listener): Disposable => this.subscribe("create", listener);
  onDidChange = (listener: Listener): Disposable => this.subscribe("change", listener);
  onDidDelete = (listener: Listener): Disposable => this.subscribe("delete", listener);

  private subscribe(event: keyof FileWatcher["listeners"], listener: Listener): Disposable {
    this.listeners[event].add(listener);
    return new Disposable(() => this.listeners[event].delete(listener));
  }

  emit(event: keyof FileWatcher["listeners"], file: string): void {
    this.listeners[event].forEach((listener) => listener(Uri.file(file)));
  }

  override dispose(): void {
    Object.values(this.listeners).forEach((listeners) => listeners.clear());
  }
}

export const Uri = {
  file: (file: string): FileUri => ({ fsPath: path.resolve(file) }),
};

export const watchers: FileWatcher[] = [];
export const workspace = {
  workspaceFolders: [] as { uri: FileUri }[],
  updateWorkspaceFolders(start: number, count: number, folder: { uri: FileUri }): boolean {
    workspace.workspaceFolders.splice(start, count, folder);
    return true;
  },
  createFileSystemWatcher(): FileWatcher {
    const watcher = new FileWatcher();
    watchers.push(watcher);
    return watcher;
  },
};

export const window = {
  selectedFolders: undefined as FileUri[] | undefined,
  showOpenDialog: async (): Promise<FileUri[] | undefined> => window.selectedFolders,
  showInformationMessage: async (): Promise<undefined> => undefined,
  showWarningMessage: async (): Promise<undefined> => undefined,
  showErrorMessage: async (): Promise<undefined> => undefined,
};

export const commands = {
  executeCommand: async (): Promise<undefined> => undefined,
};
