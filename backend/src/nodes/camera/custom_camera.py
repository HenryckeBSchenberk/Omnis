from bson import ObjectId
from src.manager.camera_manager import CameraManager
from cv2 import error
from api import logger, exception
from api.decorators import for_all_methods
# from vidgear.gears import CamGear #! BREAKING CHANGES
from cv2 import cvtColor, COLOR_BGR2GRAY, arcLength, VideoWriter_fourcc
from .roi_aruco import ROI_ARUCO as ROI

from cv2.aruco import (
    DetectorParameters_create,
    Dictionary_get,
    detectMarkers,
    # drawAxis,
    drawDetectedMarkers,
    estimatePoseSingleMarkers,
)

from numpy import mean
from src.utility.image_processing.guess_aruco_type import ARUCO_DICT


@for_all_methods(exception(logger))
#! BREAKING CHANGES - START
# class Camera(CamGear):
class Camera():
#! BREAKING CHANGES - END
    """
        CamGear supports a diverse range of video streams which can handle/control video stream almost any IP/USB Cameras, multimedia video file format (upto 4k tested),
        any network stream URL such as http(s), rtp, rstp, rtmp, mms, etc. It also supports Gstreamer's RAW pipelines.

        CamGear API provides a flexible, high-level multi-threaded wrapper around OpenCV's VideoCapture API with direct access to almost all of its available parameters.
        It relies on Threaded Queue mode for threaded, error-free and synchronized frame handling.

        CamGear internally implements `yt_dlp` backend class for seamlessly pipelining live video-frames and metadata from various streaming services like YouTube, Dailymotion,
        Twitch, and [many more ➶](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md#supported-sites)
    """

    def __init__(
        self,
        _id=None,
        name="WebcamVideoStream",
        source=0,
        **options,
    ):

        """
        This constructor method initializes the object state and attributes of the CamGear class.

        Parameters:
            source (based on input): defines the source for the input stream, eg. '/dev/video0' or '-1'
            options (dict): provides ability to alter Source Tweak Parameters.
        """
        self._id = ObjectId(_id)
        self.name = name
        self.source = source
        self.opt = options
        self.last_c, self.last_i = None, None
        self.config = options.get("config")
        self.aruco_parms = DetectorParameters_create()
        self.aruco_dict = Dictionary_get(ARUCO_DICT.get(self.config.get("marker_type")))
        self.valid_source = False
        if self.opt.get("props", {}).get("CAP_PROP_FOURCC"):
            self.opt["props"]["CAP_PROP_FOURCC"] = VideoWriter_fourcc(
                *options["props"]["CAP_PROP_FOURCC"][:4]
            )
        
        for s in self.source:
            try:
                super().__init__(s, **self.opt.get("props"))
                logger.debug(f"Camera {self.name} initialized with source {s}")
                self.valid_source = True
                break
            except ValueError:
                # self.stop()
                pass
            except (error, RuntimeError):
                logger.debug("Camera source: {} fail".format(s))
                
        # if self.valid_source:
        self.start()
        c, i, _ = self.detect_markers()
        CameraManager.add(self)

    def read(self):
        # if self.marker_len:
        #     return undistort(super().read(), self.mtx, self.dist, None) #? Too slow for 4K. Maybe use a smaller image?
        c, i, _ = self.detect_markers()
        if i is not None and len(i.flatten())==4:
            self.last_c, self.last_i = c, i
        return ROI(super().read(), self.aruco_dict, self.aruco_parms, corners=self.last_c, ids=self.last_i)[0]

    def remove(self):
        CameraManager.remove(self)

    def get_scale(self):
        corners, _, _ = self.detect_markers()
        return self.estimate_pixel_cm_ratio(corners, self.config.get("marker_size"))

    def detect_markers(self):
        return detectMarkers(
            cvtColor(super().read(), COLOR_BGR2GRAY),
            self.aruco_dict,
            parameters=self.aruco_parms,
        )

    # def draw_markers(self, size_of_marker=0.010):
    #     corners, ids, rejected = self.detect_markers()
    #     rvecs, tvecs, _ = estimatePoseSingleMarkers(
    #         corners, size_of_marker, self.mtx, self.dist
    #     )
    #     length_of_axis = size_of_marker / 2
    #     frame = drawDetectedMarkers(self.read().copy(), corners, ids)
        
    #     if tvecs is not None:
    #         for r, t in zip(rvecs, tvecs):
    #             frame = drawAxis(
    #                 frame,
    #                 self.mtx,
    #                 self.dist,0000000000
    #                 r,
    #                 t,
    #                 length_of_axis,
    #             )
    #     return frame

    @staticmethod
    def estimate_pixel_cm_ratio(corners, aruco_size):
        """
        Estimate the pixel to cm ratio of the aruco marker.
        :param corners: corners of the aruco marker
        :param aruco_size: size of the aruco marker
        :return: pixel to cm ratio
        """
        print(arcLength(corners[0], True)/4)

        return mean([arcLength(corner, True) / (aruco_size * 4) for corner in corners])

    def to_dict(self):
        """
        Returns a dictionary representation of the camera.
        """
        return {
            "_id": str(self._id),
            "src": self.source,
            "name": self.name,
            "properties": self.opt,
        }

    def __str__(self) -> str:
        return str(self.to_dict())

    def __dell__(self):
        self.stop()