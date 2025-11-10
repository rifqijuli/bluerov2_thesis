import torch
import torch.nn as nn
import torchvision.transforms as T
import numpy as np
import cv2
import gi
from ultralytics import YOLO

from nets.funiegan import GeneratorFunieGAN as Generator  # adjust import path to match your repo

gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Load the YOLO11 model
model = YOLO("yolo11n.pt")

#!/usr/bin/env python
"""
BlueRov video capture class
"""


class Video():
    """BlueRov video capture class constructor

    Attributes:
        port (int): Video UDP port
        video_codec (string): Source h264 parser
        video_decode (string): Transform YUV (12bits) to BGR (24bits)
        video_pipe (object): GStreamer top-level pipeline
        video_sink (object): Gstreamer sink element
        video_sink_conf (string): Sink configuration
        video_source (string): Udp source ip and port
        latest_frame (np.ndarray): Latest retrieved video frame
    """

    def __init__(self, port=5601):
        """Summary

        Args:
            port (int, optional): UDP port
        """

        Gst.init(None)

        self.port = port
        self.latest_frame = self._new_frame = None

        # [Software component diagram](https://www.ardusub.com/software/components.html)
        # UDP video stream (:5600)
        self.video_source = 'udpsrc port={5601}'#.format(self.port)
        # [Rasp raw image](http://picamera.readthedocs.io/en/release-0.7/recipes2.html#raw-image-capture-yuv-format)
        # Cam -> CSI-2 -> H264 Raw (YUV 4-4-4 (12bits) I420)
        self.video_codec = '! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264'
        # Python don't have nibble, convert YUV nibbles (4-4-4) to OpenCV standard BGR bytes (8-8-8)
        self.video_decode = \
            '! decodebin ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert'
        # Create a sink to get data
        self.video_sink_conf = \
            '! appsink emit-signals=true sync=false max-buffers=2 drop=true'

        self.video_pipe = None
        self.video_sink = None

        self.run()

    def start_gst(self, config=None):
        """ Start gstreamer pipeline and sink
        Pipeline description list e.g:
            [
                'videotestsrc ! decodebin', \
                '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                '! appsink'
            ]

        Args:
            config (list, optional): Gstreamer pileline description list
        """

        if not config:
            config = \
                [
                    'videotestsrc ! decodebin',
                    '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                    '! appsink'
                ]

        command = ' '.join(config)
        self.video_pipe = Gst.parse_launch(command)
        self.video_pipe.set_state(Gst.State.PLAYING)
        self.video_sink = self.video_pipe.get_by_name('appsink0')

    @staticmethod
    def gst_to_opencv(sample):
        """Transform byte array into np array

        Args:
            sample (TYPE): Description

        Returns:
            TYPE: Description
        """
        buf = sample.get_buffer()
        caps_structure = sample.get_caps().get_structure(0)
        array = np.ndarray(
            (
                caps_structure.get_value('height'),
                caps_structure.get_value('width'),
                3
            ),
            buffer=buf.extract_dup(0, buf.get_size()), dtype=np.uint8)
        return array

    def frame(self):
        """ Get Frame

        Returns:
            np.ndarray: latest retrieved image frame
        """
        if self.frame_available:
            self.latest_frame = self._new_frame
            # reset to indicate latest frame has been 'consumed'
            self._new_frame = None
        return self.latest_frame

    def frame_available(self):
        """Check if a new frame is available

        Returns:
            bool: true if a new frame is available
        """
        return self._new_frame is not None

    def run(self):
        """ Get frame to update _new_frame
        """

        self.start_gst(
            [
                self.video_source,
                self.video_codec,
                self.video_decode,
                self.video_sink_conf
            ])

        self.video_sink.connect('new-sample', self.callback)

    def callback(self, sink):
        sample = sink.emit('pull-sample')
        self._new_frame = self.gst_to_opencv(sample)

        return Gst.FlowReturn.OK


if __name__ == '__main__':
    # Create the video object
    # Add port= if is necessary to use a different one
    video = Video()
    
    # --- Load pretrained FUnIE-GAN model ---
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_path = "funie_generator.pth"  # change if different
    G = Generator().to(device)
    G.load_state_dict(torch.load(model_path, map_location=device))
    G.eval()

    # --- Define transforms ---
    to_tensor = T.Compose([
        T.ToPILImage(),
        T.Resize((256, 256)),
        T.ToTensor()
    ])
    to_image = T.ToPILImage()

    print('Initialising stream...')
    waited = 0
    while not video.frame_available():
        waited += 1
        print('\r  Frame not available (x{})'.format(waited), end='')
        cv2.waitKey(30)
    print('\nSuccess!\nStarting streaming - press "q" to quit.')

    while True:
        # Wait for the next frame to become available
        if video.frame_available():
            # Only retrieve and display a frame if it's new
            frame = video.frame()
            frame = cv2.resize(frame, (640, 480))
            
            # Convert frame (BGR->RGB)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            inp = to_tensor(rgb).unsqueeze(0).to(device)

            # Run enhancement
            with torch.no_grad():
                out = G(inp)

            # Convert back to OpenCV format
            out_np = out.squeeze(0).cpu().permute(1, 2, 0).numpy()
            out_np = np.clip(out_np * 255, 0, 255).astype(np.uint8)
            out_bgr = cv2.cvtColor(out_np, cv2.COLOR_RGB2BGR)

            # Resize for display
            out_bgr = cv2.resize(out_bgr, (frame.shape[1], frame.shape[0]))

            # Run YOLO11 tracking on the frame, persisting tracks between frames
            results_original = model.track(frame, persist=True)
            results_enhanced = model.track(out_bgr, persist=True)

            # Visualize the results on the frame
            annotated_frame_original = results_original[0].plot()
            annotated_frame_enhanced = results_enhanced[0].plot()

            # Show both
            cv2.imshow("Original", frame)
            cv2.imshow("Enhanced", out_bgr)
            cv2.imshow("YOLO11 Tracking Original", annotated_frame_original)
            cv2.imshow("YOLO11 Tracking Enhanced", annotated_frame_enhanced)
        # Allow frame to display, and check if user wants to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()