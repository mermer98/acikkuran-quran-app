const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow () {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  // Next.js local sunucu adresi
  win.loadURL('http://localhost:2018');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
