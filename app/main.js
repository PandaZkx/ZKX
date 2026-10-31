const { app, BrowserWindow, ipcMain, shell, Tray, Menu, globalShortcut, nativeImage } = require('electron');
const path = require('path');
let win, tray, normalBounds = null, quitting = false;
if (!app.requestSingleInstanceLock()) { app.quit(); }
app.setAppUserModelId('com.pandazkx.zkx');
const ICON = path.join(__dirname, 'icon.png');

function show(){ if (!win) return; if (win.isMinimized()) win.restore(); win.show(); win.focus(); }
function create(){
  win = new BrowserWindow({
    width: 1400, height: 900, minWidth: 380, minHeight: 480, show: false,
    backgroundColor: '#0d1117', title: 'ZKX', icon: ICON,
    titleBarStyle: 'hidden',
    titleBarOverlay: { color: '#0a0e14', symbolColor: '#e6edf5', height: 34 },
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, sandbox: true, nodeIntegration: false }
  });
  win.removeMenu();
  win.loadFile(path.join(__dirname, 'index.html'));
  win.once('ready-to-show', () => win.show());
  win.webContents.setWindowOpenHandler(({ url }) => { if (/^https?:/.test(url)) shell.openExternal(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (e, url) => { if (/^https?:/.test(url)) { e.preventDefault(); shell.openExternal(url); } });
  win.on('close', e => { if (!quitting && tray) { e.preventDefault(); win.hide();
    if (!app.__hinted) { app.__hinted = true; tray.displayBalloon && tray.displayBalloon({ iconType: 'info', title: 'ZKX tourne toujours', content: 'ZKX reste près de l\'horloge. Clic droit sur l\'icône → Quitter pour le fermer.' }); } } });
}
function makeTray(){
  tray = new Tray(nativeImage.createFromPath(ICON).resize({ width: 16, height: 16 }));
  tray.setToolTip('ZKX · Epic Seven');
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: 'Ouvrir ZKX', click: show },
    { label: 'Mode overlay (Ctrl+Maj+Z)', click: () => { show(); win.webContents.send('toggle-overlay'); } },
    { label: 'Mes captures', click: () => { show(); win.webContents.send('open-captures'); } },
    { type: 'separator' },
    { label: 'Lancer au démarrage de Windows', type: 'checkbox', checked: app.getLoginItemSettings().openAtLogin, click: m => app.setLoginItemSettings({ openAtLogin: m.checked }) },
    { type: 'separator' },
    { label: 'Quitter', click: () => { quitting = true; app.quit(); } }
  ]));
  tray.on('click', show);
}
app.on('second-instance', show);
ipcMain.on('version', e => { e.returnValue = app.getVersion(); });
ipcMain.on('get-login', e => { e.returnValue = app.getLoginItemSettings().openAtLogin; });
ipcMain.on('set-login', (_e, v) => app.setLoginItemSettings({ openAtLogin: !!v }));
ipcMain.on('ontop', (_e, v) => win && win.setAlwaysOnTop(!!v, 'screen-saver'));
ipcMain.on('overlay', (_e, on) => {
  if (!win) return;
  if (on){ if (win.isMaximized()) win.unmaximize(); normalBounds = win.getBounds(); win.setAlwaysOnTop(true, 'screen-saver'); win.setBounds({ width: 420, height: 740 }); }
  else { win.setAlwaysOnTop(false); if (normalBounds) win.setBounds(normalBounds); }
});
ipcMain.on('open', (_e, url) => { if (/^https:\/\/github\.com\//.test(url)) shell.openExternal(url); });
app.whenReady().then(() => {
  create(); makeTray();
  globalShortcut.register('CommandOrControl+Shift+Z', () => { show(); win.webContents.send('toggle-overlay'); });
});
app.on('before-quit', () => { quitting = true; });
app.on('will-quit', () => globalShortcut.unregisterAll());
app.on('window-all-closed', () => app.quit());
