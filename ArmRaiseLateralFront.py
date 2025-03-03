import mediapipe as mp
from exercise_detection import Exercise  # Exercise sınıfını içe aktar
import math

# Initialize the MediaPipe pose module
mp_pose = mp.solutions.pose

class ArmRaiseLateralFront(Exercise):
    def __init__(self):
        super().__init__()
        self.angle_threshold = 25  # Kol açısı için eşik değeri
        self.repetition_count = 0
        self.state = "idle"

    def detect_keypoints(self, image):
        # ... MediaPipe ile eklem noktalarını tespit etme kodu ...
        pass

    def validate_angles(self, keypoints):
        shoulder = [keypoints[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    keypoints[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [keypoints[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 keypoints[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [keypoints[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 keypoints[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        # Açı hesaplama
        arm_angle = self.calculate_angle(shoulder, elbow, wrist)

        # Eşik değerler ile kontrol
        if arm_angle < 25:
            return False  # Yanlış
        elif 25 <= arm_angle <= 45:
            return True  # Doğru
        else:
            return False  # Yanlış

    def calculate_angle(self, a, b, c):
        # Açı hesaplama fonksiyonu
        a = [a.x, a.y]
        b = [b.x, b.y]
        c = [c.x, c.y]
        
        ab = [b[0] - a[0], b[1] - a[1]]
        bc = [b[0] - c[0], b[1] - c[1]]
        
        angle = math.degrees(math.atan2(ab[1], ab[0]) - math.atan2(bc[1], bc[0]))
        return angle + 360 if angle < 0 else angle

    def update_state(self, keypoints):
        joint_angle = self.validate_angles(keypoints)
        self.state_machine.update_state(joint_angle)  # State machine güncellenir

    def get_repetition_count(self):
        return self.state_machine.get_repetition_count()  # Tekrar sayısını al
