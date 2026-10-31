const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('zkx', {
  version: ipcRenderer.sendSync('version'),
  setOnTop: v => ipcRenderer.send('ontop', !!v),
  overlay: on => ipcRenderer.send('overlay', !!on),
  openExternal: url => ipcRenderer.send('open', String(url))
});
