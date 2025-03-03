import cv2
import mediapipe as mp
import math
from exercise_classes import (
    ExerciseBase, Squat, NeckFlexionExtension, ShoulderRegion,
    ArmRaiseLateralFront, ThoracicExtension, LumbarSideBendingFlexion,
    HipAbduction, KneeFlexionExtension, LegRaiseStraightLegRaise,
    AbdominalCrunches
)

# MediaPipe için gerekli bileşenler
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

class Exercise:
    def __init__(self):
        self.angle_threshold = 15  # Varsayılan açı eşik değeri
        self.repetition_count = 0
        self.state = "idle"

    def detect_keypoints(self, image):
        """
        Görüntüdeki eklem noktalarını tespit eder.
        :param image: Giriş görüntüsü (BGR formatında).
        :return: Tespit edilen eklem noktaları veya None.
        """
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        if results.pose_landmarks:
            return results.pose_landmarks
        else:
            return None

    def validate_angles(self, keypoints):
        """
        Egzersize özgü açıları kontrol eder ve doğru yapılıp yapılmadığını belirler.
        :param keypoints: MediaPipe tarafından tespit edilen eklem noktaları.
        :return: Egzersiz doğru yapıldıysa True, değilse False.
        """
        raise NotImplementedError("Bu metot alt sınıflar tarafından uygulanmalıdır.")

    def calculate_angle(self, a, b, c):
        """
        Üç nokta arasındaki açıyı hesaplar.
        :param a: Başlangıç noktası (örneğin, omuz).
        :param b: Orta nokta (örneğin, dirsek).
        :param c: Bitiş noktası (örneğin, el).
        :return: Hesaplanan açı (derece cinsinden).
        """
        a = [a.x, a.y]
        b = [b.x, b.y]
        c = [c.x, c.y]
        
        ab = [b[0] - a[0], b[1] - a[1]]
        bc = [b[0] - c[0], b[1] - c[1]]
        
        angle = math.degrees(math.atan2(ab[1], ab[0]) - math.atan2(bc[1], bc[0]))
        return angle + 360 if angle < 0 else angle

    def update_state(self):
        """
        Egzersizin mevcut durumunu günceller (örneğin, "idle", "up", "down").
        """
        raise NotImplementedError("Bu metot alt sınıflar tarafından uygulanmalıdır.")

    def count_repetitions(self):
        """
        Egzersiz tekrarlarını sayar.
        """
        raise NotImplementedError("Bu metot alt sınıflar tarafından uygulanmalıdır.")

class ExerciseDetection:
    def __init__(self):
        """
        ExerciseDetection sınıfını başlatır ve tüm egzersiz sınıflarını oluşturur.
        """
        self.exercises = {
            "squat": Squat(),
            "neck_flexion_extension": NeckFlexionExtension(),
            "shoulder_region": ShoulderRegion(),
            "arm_raise_lateral_front": ArmRaiseLateralFront(),
            "thoracic_extension": ThoracicExtension(),
            "lumbar_side_bending_flexion": LumbarSideBendingFlexion(),
            "hip_abduction": HipAbduction(),
            "knee_flexion_extension": KneeFlexionExtension(),
            "leg_raise_straight_leg_raise": LegRaiseStraightLegRaise(),
            "abdominal_crunches": AbdominalCrunches()
        }
        
    def detect_exercises(self, landmarks):
        """
        Tüm egzersizleri tespit eder ve sonuçları döndürür.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
            
        Returns:
            dict: Egzersiz adları ve durumları
        """
        results = {}
        
        for exercise_name, exercise in self.exercises.items():
            # Egzersiz durumunu güncelle
            exercise.update_state(landmarks)
            
            # Egzersiz durumunu al
            state = exercise.get_state()
                
            # Tekrar sayısını al
            repetition_count = exercise.get_repetition_count()
            
            # Sonuçları kaydet
            results[exercise_name] = f"{state.capitalize()} ({repetition_count} reps)"
            
        return results