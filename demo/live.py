from __future__ import print_function
import torch
from torch.autograd import Variable
import cv2
import time
from imutils.video import FPS, WebcamVideoStream
import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Single Shot MultiBox Detection')
parser.add_argument('--weights', default='weights/ssd_300_VOC0712.pth',
                    type=str, help='Trained state_dict file path')
parser.add_argument('--cuda', default=False, type=bool,
                    help='Use cuda in live demo')
args = parser.parse_args()

COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
FONT = cv2.FONT_HERSHEY_SIMPLEX

def cv2_demo(net, transform):
    def predict(frame):
        height, width = frame.shape[:2]
        x = torch.from_numpy(transform(frame)[0]).permute(2, 0, 1)
        x = Variable(x.unsqueeze(0))
        y = net(x)  # forward pass
        detections = y.data
        # scale each detection back up to the image
        scale = torch.Tensor([width, height, width, height])
        for i in range(detections.size(1)):
            j = 0
            while detections[0, i, j, 0] >= 0.6:
                pt = (detections[0, i, j, 1:] * scale).cpu().numpy()
                cv2.rectangle(frame,
                              (int(pt[0]), int(pt[1])),
                              (int(pt[2]), int(pt[3])),
                              COLORS[i % 3], 2)
                cv2.putText(frame, labelmap[i - 1], (int(pt[0]), int(pt[1])),
                            FONT, 2, (255, 255, 255), 2, cv2.LINE_AA)
                j += 1
        return frame


    vid_path, vid_writer = None, None
    # start video stream thread, allow buffer to fill
    print("[INFO] starting threaded video stream...")
    # stream = WebcamVideoStream(src=0).start()  # default camera
    cap = cv2.VideoCapture("/home/hyphen/Downloads/Problem 1.mp4")
    time.sleep(1.0)
    # start fps timer
    # loop over frames from the video file stream
    while True:
        # grab next frame
        ret, frame = cap.read()
        # print(frame[0])
        # print(frame[1])
        # print(frame.shape)
        # import pdb; pdb.set_trace()
        key = cv2.waitKey(1) & 0xFF

        # update FPS counter
        fps.update()
        frame = predict(frame)

        # keybindings for display
        # if key == ord('p'):  # pause
        #     while True:
        #         key2 = cv2.waitKey(1) or 0xff
        #         cv2.imshow('frame', frame)
        #         if key2 == ord('p'):  # resume
        #             break

        # added for saving video

        # if isinstance(vid_writer, cv2.VideoWriter):
        #     vid_writer.release()  # release previous video writer

        save_path = "output.mp4"

        if vid_path != save_path:  # new video
            vid_path = save_path
            if isinstance(vid_writer, cv2.VideoWriter):
                vid_writer.release()  # release previous video writer

            fourcc = 'mp4v'  # output video codec
            fps1 = cap.get(cv2.CAP_PROP_FPS)
            h,w,_= frame.shape
            vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*fourcc), fps1, (w, h))
        vid_writer.write(frame)


        # cv2.imshow('frame', frame)
        
        if key == 27:  # exit
            break


if __name__ == '__main__':

    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

    from data import BaseTransform, VOC_CLASSES as labelmap
    from ssd import build_ssd

    net = build_ssd('test', 300, 21)    # initialize SSD
    net.load_state_dict(torch.load(args.weights))
    transform = BaseTransform(net.size, (104/256.0, 117/256.0, 123/256.0))

    fps = FPS().start()
    cv2_demo(net.eval(), transform)
    # stop the timer and display FPS information
    fps.stop()

    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # cleanup
    cv2.destroyAllWindows()
    stream.stop()
