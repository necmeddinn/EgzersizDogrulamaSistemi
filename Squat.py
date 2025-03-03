import math
import mediapipe as mp
from exercise_detection import Exercise  # Exercise sınıfını içe aktar
from ExerciseStateMachine import ExerciseStateMachine  # ExerciseStateMachine sınıfını içe aktar

mp_pose = mp.solutions.pose

class Squat(Exercise):
    def __init__(self):
        super().__init__()
        self.state_machine = ExerciseStateMachine("Squat", "knee", 30, 10)  # Eşik değerleri ayarlanır

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
        knee_angle = self.calculate_angle(hip, knee, ankle)

        # Eşik değerler ile kontrol
        if knee_angle < 90:
            return False  # Squat çok derin
        elif 90 <= knee_angle <= 110:
            return True  # Squat doğru
        else:
            return False  # Daha fazla çömel

    def calculate_angle(self, a, b, c):
        a = [a[0], a[1]]
        b = [b[0], b[1]]
        c = [c[0], c[1]]

        ab = [b[0] - a[0], b[1] - a[1]]
        bc = [b[0] - c[0], b[1] - c[1]]

        cosine_angle = (ab[0] * bc[0] + ab[1] * bc[1]) / (math.sqrt(ab[0]**2 + ab[1]**2) * math.sqrt(bc[0]**2 + bc[1]**2))
        angle = math.degrees(math.acos(cosine_angle))
        return angle

    def update_state(self, keypoints):
        if keypoints is not None:
            print("Keypoints detected:", keypoints)  # Hata ayıklama
            joint_angle = self.validate_angles(keypoints)
            self.state_machine.update_state(joint_angle)  # State machine güncellenir

    def get_repetition_count(self):
        return self.state_machine.get_repetition_count()  # Tekrar sayısını al
