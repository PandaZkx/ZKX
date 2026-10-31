const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('zkx', {
  version: ipcRenderer.sendSync('version'),
  setOnTop: v => ipcRenderer.send('ontop', !!v),
  overlay: on => ipcRenderer.send('overlay', !!on),
  openExternal: url => ipcRenderer.send('open', String(url)),
  getLogin: () => ipcRenderer.sendSync('get-login'),
  setLogin: v => ipcRenderer.send('set-login', !!v),
  onToggleOverlay: cb => ipcRenderer.on('toggle-overlay', () => cb()),
  onOpenCaptures: cb => ipcRenderer.on('open-captures', () => cb())
});
