const { app, BrowserWindow, ipcMain, shell, Tray, Menu, globalShortcut, nativeImage, dialog } = require('electron');
const fs = require('fs');
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
/* ---- Import Fribbels automatique : surveille le dossier de la sauvegarde choisie ---- */
const CFG = () => path.join(app.getPath('userData'), 'zkx-config.json');
let cfg = null, fbTimer = null, fbLast = '';
function loadCfg(){ if (cfg) return cfg; try { cfg = JSON.parse(fs.readFileSync(CFG(), 'utf8')); } catch (e) { cfg = {}; } return cfg; }
function saveCfg(){ try { fs.writeFileSync(CFG(), JSON.stringify(cfg)); } catch (e) {} }
function fbNewest(){
  const f = loadCfg().fribbels; if (!f) return null;
  let best = null;
  try { const st = fs.statSync(f); best = { p: f, m: st.mtimeMs }; } catch (e) {}
  try {
    const dir = path.dirname(f);
    for (const n of fs.readdirSync(dir)){
      if (!/\.json$/i.test(n)) continue;
      const p = path.join(dir, n); let st; try { st = fs.statSync(p); } catch (e) { continue; }
      if (!best || st.mtimeMs > best.m) best = { p, m: st.mtimeMs };
    }
  } catch (e) {}
  return best;
}
function fbCheck(force){
  if (!win || !loadCfg().fribbels) return;
  const b = fbNewest();
  if (!b){ win.webContents.send('fb', { s: 'missing', path: cfg.fribbels }); return; }
  const key = b.p + '|' + b.m; if (!force && key === fbLast) return;
  fs.readFile(b.p, 'utf8', (e, txt) => {
    if (e || !/"heroes"|"items"/.test(txt.slice(0, 2000000))) return;
    fbLast = key;
    if (b.p !== cfg.fribbels){ cfg.fribbels = b.p; saveCfg(); }
    win.webContents.send('fb', { s: 'data', path: b.p, mtime: b.m, text: txt });
  });
}
function fbWatch(){ clearInterval(fbTimer); fbTimer = null; if (loadCfg().fribbels) fbTimer = setInterval(() => fbCheck(false), 4000); }
ipcMain.handle('fb-pick', async () => {
  const r = await dialog.showOpenDialog(win, { title: 'Choisis ta sauvegarde Fribbels (.json)', defaultPath: loadCfg().fribbels || app.getPath('documents'),
    filters: [{ name: 'Sauvegarde Fribbels', extensions: ['json'] }], properties: ['openFile'] });
  if (r.canceled || !r.filePaths[0]) return null;
  cfg.fribbels = r.filePaths[0]; saveCfg(); fbLast = ''; fbWatch(); fbCheck(true); return cfg.fribbels;
});
ipcMain.on('fb-get', e => { e.returnValue = loadCfg().fribbels || null; });
ipcMain.on('fb-off', () => { delete loadCfg().fribbels; saveCfg(); clearInterval(fbTimer); fbTimer = null; });
ipcMain.on('fb-ready', () => { fbLast = ''; fbWatch(); fbCheck(true); });
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
