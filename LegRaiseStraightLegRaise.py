import mediapipe as mp
from exercise_detection import Exercise  # Exercise sınıfını içe aktar
from ExerciseStateMachine import ExerciseStateMachine  # ExerciseStateMachine sınıfını içe aktar

# Initialize the MediaPipe pose module
mp_pose = mp.solutions.pose

class LegRaiseStraightLegRaise(Exercise):
    def __init__(self):
        super().__init__()
        self.state_machine = ExerciseStateMachine("Leg Raise Straight Leg Raise", "leg", 20, 10)  # Eşik değerleri ayarlanır

    def detect_keypoints(self, image):
        # ... MediaPipe ile eklem noktalarını tespit etme kodu ...
        pass

    def validate_angles(self, keypoints):
        hip = [keypoints[mp_pose.PoseLandmark.LEFT_HIP.value].x,
               keypoints[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        knee = [keypoints[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                keypoints[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        ankle = [keypoints[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                 keypoints[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

        # Açı hesaplama
        leg_angle = self.calculate_angle(hip, knee, ankle)

        # Eşik değerler ile kontrol
        if leg_angle < 30:
            return False  # Yanlış
        elif 30 <= leg_angle <= 45:
            return True  # Doğru
        else:
            return False  # Yanlış

    def calculate_angle(self, a, b, c):
        # Açı hesaplama fonksiyonu
        import math
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
