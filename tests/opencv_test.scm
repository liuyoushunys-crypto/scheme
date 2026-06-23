; ============================================================
; OpenCV 4.13.0 集成验证
; ============================================================

(import cv2)
(import numpy as np)

(display "=== OpenCV 4.13.0 Integration ===\n")
(newline)

; --- 1. 创建测试图像（numpy 数组） ---
(display "1. Create test image (numpy): ")
(define img (np.zeros '(100 100 3) :dtype np.uint8))
(display (np.shape img))
(newline)

; --- 2. 绘制图形 ---
(display "2. Drawing: ")
; cv2.rectangle 直接调用
(cv2.rectangle img '(10 10) '(90 90) '(0 255 0) 2)
(cv2.circle img '(50 50) 30 '(0 0 255) 1)
(cv2.putText img "CAS" '(30 55) cv2.FONT_HERSHEY_SIMPLEX 0.7 '(255 255 255) 2)
(display "drawn OK")
(newline)

; --- 3. 图像处理 ---
(display "3. Image processing: ")
(define gray (cv2.cvtColor img cv2.COLOR_BGR2GRAY))
(display "gray: ")
(display (np.shape gray))
(newline)

(display "4. GaussianBlur: ")
(define blurred (cv2.GaussianBlur gray '(5 5) 1.5))
(display (np.shape blurred))
(newline)

(display "5. Canny edge detection: ")
(define edges (cv2.Canny blurred 50 150))
(display (np.shape edges))
(newline)

; --- 4. resize ---
(display "6. Resize: ")
(define resized (cv2.resize img '(200 200)))
(display (np.shape resized))
(newline)

; --- 5. 图像信息 ---
(display "7. Image info: ")
(display "dtype: ")
(display (py-str img.dtype))
(newline)

; --- 6. 写入文件 ---
(display "8. imwrite: ")
(cv2.imwrite "/tmp/cas_test.png" img)
(display "written OK")
(newline)

; --- 7. 读回文件验证 ---
(display "9. imread verification: ")
(define img2 (cv2.imread "/tmp/cas_test.png"))
(display (np.shape img2))
(newline)

; --- 8. Feature detection ---
(display "10. ORB feature detection: ")
(define orb (cv2.ORB_create))
(define kps (orb.detect img))
(display "keypoints: ")
(display (py-len kps))
(newline)

; --- 9. 颜色转换链 ---
(display "11. Color conversions: ")
(define hsv (cv2.cvtColor img cv2.COLOR_BGR2HSV))
(display "hsv: ")
(display (np.shape hsv))
(newline)

; --- 10. 阈值处理 ---
(display "12. Threshold: ")
(define ret_thresh (cv2.threshold gray 127 255 cv2.THRESH_BINARY))
; threshold 返回 (retval, thresh_img)
(display "thresh shape: ")
(display (np.shape (py-get ret_thresh 1)))
(newline)

(display "\n=== OpenCV Integration Complete ===")
(newline)