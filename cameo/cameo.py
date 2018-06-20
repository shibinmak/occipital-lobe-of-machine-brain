from managers import WindowManager,CaptureManager
import cv2


class Cameo(object):
    def __init__(self):
        self._windowManager = WindowManager('mak', keyPressCallback = self.onKeypress)
        self._captureManager = CaptureManager(cv2.VideoCapture('http://192.168.0.101:8003/video'),
                                              self._windowManager, True)

    def run(self):

        self._windowManager.createWindow()
        while self._windowManager.iswindowCreated:
            self._captureManager.enterFrame()
            frame = self._captureManager.frame

            if frame is not None:
                pass


            self._captureManager.exitFrame()
            self._windowManager.processEvents()

    def onKeypress(self, keycode):

        if keycode == 32:  # space
            self._captureManager.writeImage('screenshot.png')
        elif keycode == 9:  # tab
            if not self._captureManager.startWritingVideo('screencast.avi'):
                self._captureManager.stopWritingVideo()
        elif keycode == 27:  # escape
            self._windowManager.destroyWindow()


if __name__ == "__main__":
    Cameo().run()
