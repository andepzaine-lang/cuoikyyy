import cv2
import time
import datetime
import numpy as np
import os
import smtplib
from email.message import EmailMessage
from ultralytics import YOLO

# ================== TẠO THƯ MỤC LƯU ẢNH ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(BASE_DIR, "alerts")
os.makedirs(SAVE_DIR, exist_ok=True)

# ================== CẤU HÌNH ==================
MODEL = "yolov8n.pt"
CONFIDENCE = 0.5

# ===== EMAIL (GMAIL) =====
EMAIL_SENDER = "andepzaine@gmail.com"
EMAIL_PASSWORD = "eerk qhhq umeb cpnv"   # 🔥 dùng App Password
EMAIL_RECEIVER = "andepzaine@gmail.com"

# ===== VÙNG CẤM =====
FORBIDDEN_ZONE = [(200, 150), (600, 150), (600, 450), (200, 450)]

# ===== COOLDOWN =====
last_alert_time = 0
ALERT_COOLDOWN = 20

# ================== LOAD MODEL ==================
print("🚀 Đang tải model YOLOv8...")
model = YOLO(MODEL)
print("✅ Model đã sẵn sàng")

# ================== HÀM GỬI EMAIL ==================
def send_email_alert(img_path, message):
    try:
        msg = EmailMessage()
        msg['Subject'] = "CANH BAO XAM NHAP"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg.set_content(message)

        # Đính kèm ảnh
        with open(img_path, 'rb') as f:
            img_data = f.read()
            msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename='alert.jpg')

        # Gửi mail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print("✅ Đã gửi email!")

    except Exception as e:
        print("❌ Lỗi gửi email:", e)

# ================== CAMERA ==================
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 1280)
cap.set(4, 720)

if not cap.isOpened():
    print("❌ Không mở được webcam!")
    exit()

print("🎥 Hệ thống đang chạy...")
print("Nhấn 'q' để thoát")

prev_state = False  # tránh spam

# ================== LOOP ==================
while True:
    success, frame = cap.read()
    if not success:
        print("❌ Không đọc được camera")
        break

    results = model(frame, conf=CONFIDENCE, verbose=False)

    person_in_zone = False

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if cls == 0:  # person
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(frame, f"Person {conf:.2f}", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                if (FORBIDDEN_ZONE[0][0] < cx < FORBIDDEN_ZONE[2][0] and 
                    FORBIDDEN_ZONE[0][1] < cy < FORBIDDEN_ZONE[2][1]):
                    person_in_zone = True

    # Vẽ vùng cấm
    pts = np.array(FORBIDDEN_ZONE, np.int32).reshape((-1, 1, 2))
    cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
    cv2.putText(frame, "KHU VUC CAM",
                (FORBIDDEN_ZONE[0][0]+10, FORBIDDEN_ZONE[0][1]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # ================== CẢNH BÁO ==================
    if person_in_zone and not prev_state:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        img_path = os.path.join(SAVE_DIR, f"alert_{timestamp}.jpg")

        # Lưu ảnh
        if cv2.imwrite(img_path, frame):
            print("📸 Đã lưu:", img_path)

            send_email_alert(
                img_path,
                f"Phat hien xam nhap luc {timestamp}"
            )
        else:
            print("❌ Lưu ảnh thất bại")

    prev_state = person_in_zone

    # Hiển thị
    cv2.imshow("Security System - YOLOv8", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ================== KẾT THÚC ==================
cap.release()
cv2.destroyAllWindows()
print("🛑 Hệ thống đã dừng")