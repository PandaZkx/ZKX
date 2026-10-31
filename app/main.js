const { app, BrowserWindow, ipcMain, shell, Tray, Menu, globalShortcut, nativeImage } = require('electron');
const path = require('path');
let autoUpdater = null;
try { ({ autoUpdater } = require('electron-updater')); } catch (e) { autoUpdater = null; }
let win, tray, normalBounds = null, quitting = false;
if (!app.requestSingleInstanceLock()) { app.quit(); }
app.setAppUserModelId('com.pandazkx.zkx');
const ICON = path.join(__dirname, 'icon.png');

function show(){ if (!win) return; if (win.isMinimized()) win.restore(); win.show(); win.focus(); }
function create(){
  win = new BrowserWindow({
    width: 1400, height: 900, minWidth: 380, minHeight: 480, show: false,
    backgroundColor: '#09060d', title: 'ZKX', icon: ICON,
    titleBarStyle: 'hidden',
    titleBarOverlay: { color: '#07040b', symbolColor: '#efe9f7', height: 34 },
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
function setupUpdater(){
  const send = (s, x) => { if (win) win.webContents.send('upd', Object.assign({ s }, x || {})); };
  ipcMain.on('upd-check', () => { if (!autoUpdater || !app.isPackaged) return send('dev'); autoUpdater.checkForUpdates().catch(e => send('error', { m: String(e && e.message || e) })); });
  ipcMain.on('upd-install', () => { if (!autoUpdater) return; quitting = true; setImmediate(() => autoUpdater.quitAndInstall(true, true)); });
  if (!autoUpdater || !app.isPackaged) return;
  autoUpdater.autoDownload = true;
  autoUpdater.autoInstallOnAppQuit = true;
  autoUpdater.on('checking-for-update', () => send('checking'));
  autoUpdater.on('update-available', i => send('available', { v: i.version }));
  autoUpdater.on('update-not-available', () => send('none', { v: app.getVersion() }));
  autoUpdater.on('download-progress', p => send('progress', { p: Math.round(p.percent || 0) }));
  autoUpdater.on('update-downloaded', i => {
    send('ready', { v: i.version });
    if (tray && tray.displayBalloon) tray.displayBalloon({ iconType: 'info', title: 'ZKX ' + i.version + ' est prête', content: "La mise à jour s'installera à la fermeture de ZKX (ou tout de suite depuis ⚙ → Application)." });
  });
  autoUpdater.on('error', e => send('error', { m: String(e && e.message || e) }));
  const check = () => autoUpdater.checkForUpdates().catch(() => {});
  setTimeout(check, 8000);
  setInterval(check, 4 * 3600 * 1000);
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
  create(); makeTray(); setupUpdater();
  globalShortcut.register('CommandOrControl+Shift+Z', () => { show(); win.webContents.send('toggle-overlay'); });
});
app.on('before-quit', () => { quitting = true; });
app.on('will-quit', () => globalShortcut.unregisterAll());
app.on('window-all-closed', () => app.quit());
