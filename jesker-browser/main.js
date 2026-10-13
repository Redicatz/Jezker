const { app, BrowserWindow, shell, ipcMain, dialog, session } = require('electron')
const path = require('path')

function createWindow () {
  const win = new BrowserWindow({
    width: 1000,
    height: 720,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    },
    title: 'Jezker'
  })

  // load the local UI
  win.loadFile(path.join(__dirname, 'index.html'))

  // open external links in default browser
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  // block navigation inside app to other sites
  win.webContents.on('will-navigate', (event, url) => {
    const allowed = url.startsWith('file://')
    if (!allowed) {
      event.preventDefault()
      shell.openExternal(url)
    }
  })

  // block downloads by default
  session.defaultSession.on('will-download', (event, item, webContents) => {
    event.preventDefault()
    dialog.showMessageBox(win, {
      type: 'warning',
      title: 'Download blocked',
      message: 'Jezker blocks downloads by default for safety.'
    })
  })
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})

// simple IPC: show a message from renderer
ipcMain.handle('jezker-info', async (event, arg) => {
  return 'Jezker says hi.'
})
