const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('zkx', {
  version: ipcRenderer.sendSync('version'),
  setOnTop: v => ipcRenderer.send('ontop', !!v),
  overlay: on => ipcRenderer.send('overlay', !!on),
  openExternal: url => ipcRenderer.send('open', String(url)),
  getLogin: () => ipcRenderer.sendSync('get-login'),
  setLogin: v => ipcRenderer.send('set-login', !!v),
  onToggleOverlay: cb => ipcRenderer.on('toggle-overlay', () => cb()),
  onOpenCaptures: cb => ipcRenderer.on('open-captures', () => cb()),
  checkUpdate: () => ipcRenderer.send('upd-check'),
  installUpdate: () => ipcRenderer.send('upd-install'),
  onUpdate: cb => ipcRenderer.on('upd', (_e, d) => cb(d)),
  fribbelsPick: () => ipcRenderer.invoke('fb-pick'),
  fribbelsGet: () => ipcRenderer.sendSync('fb-get'),
  fribbelsOff: () => ipcRenderer.send('fb-off'),
  fribbelsReady: () => ipcRenderer.send('fb-ready'),
  onFribbels: cb => ipcRenderer.on('fb', (_e, d) => cb(d)),
  ocrGet: () => ipcRenderer.sendSync('ocr-get'),
  ocrSet: v => ipcRenderer.send('ocr-set', !!v),
  ocrReady: () => ipcRenderer.send('ocr-ready'),
  onOcr: cb => ipcRenderer.on('ocr', (_e, d) => cb(d))
});
