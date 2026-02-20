
import cv2
import time
import tomllib
from pupil_apriltags import Detector
from pypylon import pylon

with open('config.toml', 'rb') as f:
    settings = tomllib.load(f)['ips']

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

camera.ExposureAuto.Value = 'Off'
camera.ExposureTime.Value = settings['exposure']
camera.GainAuto.Value = 'Off'
camera.Gain.Value = settings['gain']
camera.BlackLevel.Value = settings['black_level']

# Doesn't make a huge impact, but there's no point in processing colored images anyways
# Theoretically reduces data transfer by using Mono8 instead of BGR (for example)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_Mono8
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

detector = Detector(
    families='tag36h11',
    nthreads=settings['threads'],
    quad_decimate=settings['quad_decimate'],
    quad_sigma=settings['quad_sigma'],
    refine_edges=settings['refined_edges'],
    decode_sharpening=settings['decode_sharpening'],
)

if settings['DEBUG']:
    WINDOW_NAME = 'IPS Debug Cam'
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 800, 800)

    fps_start = time.time()
    frames = 0
    fps = 0.0

camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
try:
    while camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            image = converter.Convert(grabResult)
            gray_img = image.GetArray()
            detected = detector.detect(gray_img, estimate_tag_pose=True, camera_params=settings['camera_coefficients'], tag_size=settings['tag_size'])

            if settings['DEBUG']:
                display_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
                
                # FPS Calculation
                frames += 1
                if time.time() - fps_start > 1.0:
                    fps = frames / (time.time() - fps_start)
                    frames = 0
                    fps_start = time.time()

                # Status Overlay
                info_color = (0, 255, 0) if len(detected) > 0 else (0, 0, 255)
                cv2.putText(display_img, f"FPS: {fps:.1f}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, info_color, 2)
                cv2.putText(display_img, f"Tags: {len(detected)}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, info_color, 2)
                
                for tag in detected:
                    # Box
                    for idx in range(len(tag.corners)):
                        cv2.line(display_img, tuple(tag.corners[idx-1].astype(int)), tuple(tag.corners[idx].astype(int)), (0, 255, 0), 2)
                    
                    # Arrow
                    center = tuple(tag.center.astype(int))
                    top = tuple(((tag.corners[2] + tag.corners[3]) / 2).astype(int))
                    cv2.arrowedLine(display_img, center, top, (0, 0, 255), 4, tipLength=0.3)

                cv2.imshow(WINDOW_NAME, display_img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        grabResult.Release()
except Exception as e:
    print(f"Error: {e}")
finally:
    camera.StopGrabbing()
    camera.Close()
    cv2.destroyAllWindows()