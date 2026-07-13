const vscode = require('vscode');
const { exec } = require('child_process');

function getCliPath() {
    return vscode.workspace.getConfiguration('codecraft').get('cliPath', 'codecraft');
}

function runCodecraft(args) {
    return new Promise((resolve, reject) => {
        const cli = getCliPath();
        const workspace = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath;
        if (!workspace) {
            return reject(new Error('No workspace folder open'));
        }
        const cmd = `${cli} ${args} --json --quiet`;
        exec(cmd, { cwd: workspace }, (err, stdout, stderr) => {
            if (err) {
                reject(new Error(stderr || err.message));
                return;
            }
            try {
                resolve(JSON.parse(stdout));
            } catch {
                resolve(stdout);
            }
        });
    });
}

class ConceptProvider {
    getTreeItem(element) {
        return element;
    }

    async getChildren(element) {
        if (!element) {
            try {
                const data = await runCodecraft('status --json');
                const concepts = data?.concepts || [];
                return concepts.slice(0, 20).map(c => {
                    const item = new vscode.TreeItem(c, vscode.TreeItemCollapsibleState.None);
                    item.tooltip = c;
                    return item;
                });
            } catch {
                return [new vscode.TreeItem('Run scan first')];
            }
        }
        return [];
    }
}

class DebtProvider {
    getTreeItem(element) {
        return element;
    }

    async getChildren(element) {
        if (!element) {
            try {
                const data = await runCodecraft('debt list --json');
                const items = data?.debt_items || [];
                return items.slice(0, 20).map(d => {
                    const item = new vscode.TreeItem(d.pattern || d, vscode.TreeItemCollapsibleState.None);
                    item.tooltip = typeof d === 'string' ? d : `${d.pattern_type}: ${d.file_path}`;
                    return item;
                });
            } catch {
                return [new vscode.TreeItem('No debt items')];
            }
        }
        return [];
    }
}

function activate(context) {
    const conceptProvider = new ConceptProvider();
    const debtProvider = new DebtProvider();

    context.subscriptions.push(
        vscode.window.createTreeView('codecraft.conceptsView', { treeDataProvider: conceptProvider })
    );
    context.subscriptions.push(
        vscode.window.createTreeView('codecraft.debtView', { treeDataProvider: debtProvider })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('codecraft.scanWorkspace', async () => {
            const workspace = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath;
            if (!workspace) {
                vscode.window.showErrorMessage('No workspace folder open');
                return;
            }
            const status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
            status.text = '$(sync~spin) CodeCraft scanning...';
            status.show();

            try {
                const result = await runCodecraft('scan dir --json');
                status.text = `$(check) CodeCraft: scan complete`;
                setTimeout(() => status.dispose(), 5000);
                vscode.window.showInformationMessage(`CodeCraft: Scan complete`);
                vscode.commands.executeCommand('codecraft.showSummary');
            } catch (err) {
                status.text = `$(error) CodeCraft: scan failed`;
                setTimeout(() => status.dispose(), 5000);
                vscode.window.showErrorMessage(`CodeCraft scan failed: ${err.message}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('codecraft.showSummary', async () => {
            try {
                const data = await runCodecraft('status --json');
                const panel = vscode.window.createWebviewPanel(
                    'codecraftSummary',
                    'CodeCraft Summary',
                    vscode.ViewColumn.One,
                    {}
                );
                const conceptCount = data?.concepts?.length || 0;
                const debtCount = data?.debt_items?.length || 0;
                panel.webview.html = `<!DOCTYPE html>
<html>
<body style="font-family: sans-serif; padding: 16px;">
    <h2>CodeCraft Summary</h2>
    <ul>
        <li>Concepts tracked: <strong>${conceptCount}</strong></li>
        <li>Debt items: <strong>${debtCount}</strong></li>
    </ul>
    <p><em>Run "CodeCraft: Scan Workspace" to refresh</em></p>
</body>
</html>`;
            } catch (err) {
                vscode.window.showErrorMessage(`Failed: ${err.message}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('codecraft.debtReport', async () => {
            try {
                const data = await runCodecraft('debt list');
                const output = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
                const doc = await vscode.workspace.openTextDocument({
                    content: output,
                    language: 'markdown'
                });
                vscode.window.showTextDocument(doc);
            } catch (err) {
                vscode.window.showErrorMessage(`Failed: ${err.message}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('codecraft.suggestNext', async () => {
            try {
                const data = await runCodecraft('suggest next');
                const output = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
                vscode.window.showInformationMessage(`CodeCraft: ${output.slice(0, 200)}`);
            } catch (err) {
                vscode.window.showErrorMessage(`Failed: ${err.message}`);
            }
        })
    );

    vscode.window.showInformationMessage('CodeCraft extension activated');
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
