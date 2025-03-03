import math
import mediapipe as mp
from exercise_detection import Exercise  # Exercise sınıfını içe aktar
from ExerciseStateMachine import ExerciseStateMachine  # ExerciseStateMachine sınıfını içe aktar

mp_pose = mp.solutions.pose

class NeckFlexionExtension(Exercise):
    def __init__(self):
        super().__init__()
        self.state_machine = ExerciseStateMachine("Neck Flexion Extension", "neck", 20, 10)  # Eşik değerleri ayarlanır

    def detect_keypoints(self, image):
        # ... MediaPipe ile eklem noktalarını tespit etme kodu ...
        pass

    def validate_angles(self, keypoints):
        neck = [keypoints[mp_pose.PoseLandmark.NOSE.value].x,
                keypoints[mp_pose.PoseLandmark.NOSE.value].y]
        shoulder_left = [keypoints[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         keypoints[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        shoulder_right = [keypoints[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          keypoints[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

        # Açı hesaplama
        neck_angle = self.calculate_angle(neck, shoulder_left, shoulder_right)

        # Eşik değerler ile kontrol
        if neck_angle < 20:
            return False  # Yanlış
        elif 20 <= neck_angle <= 30:
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
