import math
import mediapipe as mp
from exercise_detection import Exercise  # Exercise sınıfını içe aktar
from ExerciseStateMachine import ExerciseStateMachine  # ExerciseStateMachine sınıfını içe aktar

# Initialize the MediaPipe pose module
mp_pose = mp.solutions.pose

class ShoulderRegion(Exercise):
    def __init__(self):
        super().__init__()
        self.state_machine = ExerciseStateMachine("Shoulder Region", "shoulder", 15, 10)  # Eşik değerleri ayarlanır

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
        shoulder_angle = self.calculate_angle(shoulder, elbow, wrist)

        # Eşik değerler ile kontrol
        if shoulder_angle < 15:
            return False  # Yanlış
        elif 15 <= shoulder_angle <= 25:
            return True  # Doğru
        else:
            return False  # Yanlış

    def calculate_angle(self, a, b, c):
        # Açı hesaplama fonksiyonu
        a = [a[0], a[1]]
        b = [b[0], b[1]]
        c = [c[0], c[1]]
        
        ab = [b[0] - a[0], b[1] - a[1]]
        bc = [b[0] - c[0], b[1] - c[1]]
        
        angle = math.degrees(math.atan2(ab[1], ab[0]) - math.atan2(bc[1], bc[0]))
        return angle + 360 if angle < 0 else angle

    def update_state(self, keypoints):
        joint_angle = self.validate_angles(keypoints)
        self.state_machine.update_state(joint_angle)  # State machine güncellenir

    def get_repetition_count(self):
        return self.state_machine.get_repetition_count()  # Tekrar sayısını al
