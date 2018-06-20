import cv2
import numpy
import time

class ImageFrameWriter(object):
    def __init__(self):
        self._imageFileName = None
        self._new = False
    def writeImageFrame(self, frame):
        if not self._new: return
        cv2.imwrite(self._imageFileName, frame)
        self._new = False
    def newWrite(self, filename):
        self._imageFileName = filename
        self._new = True

class VideoFrameWriter(object):
    def __init__(self):
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
        self._capture = None
        self._writing = None

    def writeVideoFrame(self, frame, fpsEstimate):
        if not self._writing: return
        if self._videoWriter is None:
            fps = self._capture.get(cv2.CAP_PROP_FPS)
            fps = fpsEstimate.estimate(fps)

            if fps<=0.0:
                return
            size = (int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self._videoWriter =cv2.VideoWriter(self._videoFilename,self._videoEncoding,fps,(720,480))
        self._videoWriter.write(frame)

    def startWrite(self, fileName, encoding):
        self._videoFilename = fileName
        self._videoEncoding =encoding
        self._writing =True

    def stop(self):
        self._videoFilename =None
        self._videoEncoding = None
        self._videoWriter = None
        self._new =False

    def isWriting(self):
        return self._writing

class FpsEstimate(object):
    def __init__(self):
        self._startTime = None
        self._frameElapsed = 0
        self._fpsEstimate = None

    def update(self):
        if self._frameElapsed == 0:
            self._startTime = time.time()
        else:
            timeElapsed = time.time() - self._startTime
            self._fpsEstimate = self._frameElapsed / timeElapsed
        self._frameElapsed += 1

    def estimate(self, fps):
        if fps <= 0.0:
            return fps
        else:
            self._fpsEstimate
        return fps

class CaptureManager(object):
    def __init__(self, capture, previewWindowManager = None, MirrorPreview = False):

        self.previewWindowManager = previewWindowManager
        self.MirrorPreview = MirrorPreview

        self._capture = capture
        self._channel = 0
        self._enteredFrame = False
        self._frame = None

        self._imageFrameWriter = ImageFrameWriter()
        self._videoFrameWriter = VideoFrameWriter()
        self._fpsEstimate = FpsEstimate()



    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if self._channel != value:
            self._channel = value
            self._frame = None

    @property
    def frame(self):
        if self._enteredFrame and self._frame is None:
            _, self._frame = self._capture.retrieve()
        return self._frame



    def enterFrame(self):
        assert not self._enteredFrame
        if self._capture is not None:
            self._enteredFrame = self._capture.grab()

    def exitFrame(self):
        if self._frame is None:
            self._enteredFrame = False
            return
        self._fpsEstimate.update()

        if self.previewWindowManager is not None:
            if self.MirrorPreview:
                mirroredFrame = numpy.fliplr(self._frame).copy()
                self.previewWindowManager.show(mirroredFrame)
            else:
                self.previewWindowManager.show(self._frame)
        self._imageFrameWriter.writeImageFrame(self._frame)
        self._videoFrameWriter.writeVideoFrame(self._frame,self._fpsEstimate)

        self._frame = None
        self._enteredFrame = None

    def writeImage(self,filename):
        self._imageFrameWriter.newWrite(filename)

    def startWritingVideo(self,filename, encoding = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')):
        if not self._videoFrameWriter.isWriting() : return True
        self._videoFrameWriter.startWrite(filename, encoding)
        return False

    def stopWritngVideo(self):
        self._videoFrameWriter.stop()


class WindowManager(object):
     def __init__(self,windowName, keyPressCallback = None):
         self._windowName = windowName
         self.keyPressCallback = keyPressCallback
         self._isWindowCreated = False
     @property
     def iswindowCreated(self):
         return self._isWindowCreated

     def createWindow(self):
         cv2.namedWindow(self._windowName)
         self._isWindowCreated = True

     def show(self,frame):
         cv2.imshow(self._windowName, frame)

     def destroyWindow(self):
         cv2.destroyWindow(self._windowName)
         self._isWindowCreated = False

     def processEvents(self):
        keyCode = cv2.waitKey(1)
        if self.keyPressCallback is not None and keyCode !=-1:
            keyCode &=0xff
            self.keyPressCallback(keyCode)


