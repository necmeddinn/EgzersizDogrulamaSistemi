import math
import mediapipe as mp
from exercise_detection import Exercise  # Exercise sınıfını içe aktar
from ExerciseStateMachine import ExerciseStateMachine  # ExerciseStateMachine sınıfını içe aktar

# Initialize the MediaPipe pose module
mp_pose = mp.solutions.pose

class ThoracicExtension(Exercise):
    def __init__(self):
        super().__init__()
        self.state_machine = ExerciseStateMachine("Thoracic Extension", "thoracic", 30, 10)  # Eşik değerleri ayarlanır

    def detect_keypoints(self, image):
        # ... MediaPipe ile eklem noktalarını tespit etme kodu ...
        pass

    def validate_angles(self, keypoints):
        shoulder_left = [keypoints[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         keypoints[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        shoulder_right = [keypoints[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          keypoints[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        hip = [keypoints[mp_pose.PoseLandmark.LEFT_HIP.value].x,
               keypoints[mp_pose.PoseLandmark.LEFT_HIP.value].y]

        # Açı hesaplama
        thoracic_angle = self.calculate_angle(shoulder_left, hip, shoulder_right)

        # Eşik değerler ile kontrol
        if thoracic_angle < 30:
            return False  # Yanlış
        elif 30 <= thoracic_angle <= 45:
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
