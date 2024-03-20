from DeviceControl import DeviceController
from WindowApp import WindowApp
if __name__ == '__main__':
    controller = DeviceController()
    app = WindowApp(controller)
    app.mainloop()








    