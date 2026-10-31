const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
let win, normalBounds = null;
if (!app.requestSingleInstanceLock()) app.quit();
function create(){
  win = new BrowserWindow({
    width: 1400, height: 900, minWidth: 360, minHeight: 480,
    backgroundColor: '#0b0b0e', title: 'ZKX', icon: path.join(__dirname, 'icon.png'),
    autoHideMenuBar: true,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, sandbox: true, nodeIntegration: false }
  });
  win.removeMenu();
  win.loadFile(path.join(__dirname, 'index.html'));
  win.webContents.setWindowOpenHandler(({ url }) => { if (/^https?:/.test(url)) shell.openExternal(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (e, url) => { if (/^https?:/.test(url)) { e.preventDefault(); shell.openExternal(url); } });
}
app.on('second-instance', () => { if (win){ if (win.isMinimized()) win.restore(); win.focus(); } });
ipcMain.on('ontop', (_e, v) => win && win.setAlwaysOnTop(!!v, 'screen-saver'));
ipcMain.on('overlay', (_e, on) => {
  if (!win) return;
  if (on){ if (win.isMaximized()) win.unmaximize(); normalBounds = win.getBounds(); win.setAlwaysOnTop(true, 'screen-saver'); win.setBounds({ width: 420, height: 720 }); }
  else { win.setAlwaysOnTop(false); if (normalBounds) win.setBounds(normalBounds); }
});
ipcMain.on('version', e => { e.returnValue = app.getVersion(); });
ipcMain.on('open', (_e, url) => { if (/^https:\/\/github\.com\//.test(url)) shell.openExternal(url); });
app.whenReady().then(create);
app.on('window-all-closed', () => app.quit());
