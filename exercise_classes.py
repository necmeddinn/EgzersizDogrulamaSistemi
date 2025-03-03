import cv2
import mediapipe as mp
import numpy as np

class ExerciseBase:
    def __init__(self):
        self.keypoints = None
        self.repetition_count = 0
        self.state = "up"  # Başlangıç durumu
        self.confidence_threshold = 0.7  # Güven eşiği
        self.stable_frames = 0  # Kararlı kare sayısı
        self.required_stable_frames = 5  # Gerekli kararlı kare sayısı
        self.previous_angle = None  # Önceki açı değeri
        self.in_progress = False  # Egzersiz devam ediyor mu?

    def update_state(self, landmarks):
        """
        Egzersiz durumunu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Bu metod alt sınıflar tarafından override edilmelidir
        pass

    def check_repetition(self):
        """
        Tekrar sayısını kontrol eder ve günceller.
        """
        # Bu metod alt sınıflar tarafından override edilmelidir
        pass

    def get_repetition_count(self):
        """
        Tekrar sayısını döndürür.
        
        Returns:
            int: Tekrar sayısı
        """
        return self.repetition_count

    def calculate_angle(self, a, b, c):
        """
        Üç nokta arasındaki açıyı hesaplar.
        
        Args:
            a: Birinci nokta (landmark)
            b: İkinci nokta (landmark)
            c: Üçüncü nokta (landmark)
            
        Returns:
            float: Açı değeri (derece)
        """
        # Noktaların koordinatlarını al
        a_x, a_y = a.x, a.y
        b_x, b_y = b.x, b.y
        c_x, c_y = c.x, c.y
        
        # Vektörleri hesapla
        ba_x, ba_y = a_x - b_x, a_y - b_y
        bc_x, bc_y = c_x - b_x, c_y - b_y
        
        # Açıyı hesapla
        cosine_angle = (ba_x * bc_x + ba_y * bc_y) / (np.sqrt(ba_x**2 + ba_y**2) * np.sqrt(bc_x**2 + bc_y**2))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        # Radyandan dereceye çevir
        angle = np.degrees(angle)
        
        return angle
    
    def is_stable(self, current_angle):
        """
        Açının kararlı olup olmadığını kontrol eder.
        
        Args:
            current_angle: Mevcut açı değeri
            
        Returns:
            bool: Açı kararlı ise True, değilse False
        """
        if self.previous_angle is None:
            self.previous_angle = current_angle
            return False
        
        # Açı değişimi çok küçükse, kararlı kabul et
        if abs(current_angle - self.previous_angle) < 5:
            self.stable_frames += 1
        else:
            self.stable_frames = 0
            
        self.previous_angle = current_angle
        
        return self.stable_frames >= self.required_stable_frames
    
    def get_state(self):
        """
        Mevcut durumu döndürür.
        
        Returns:
            str: Mevcut durum ("up" veya "down")
        """
        return self.state

class Squat(ExerciseBase):
    def __init__(self):
        super().__init__()
        self.threshold_angle = 120  # Squat için eşik açısı
        self.min_angle = 90  # Minimum açı (tam squat)
        self.max_angle = 170  # Maksimum açı (tam dik)
        
    def update_state(self, landmarks):
        """
        Squat egzersizi için durumu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Kalça, diz ve ayak bileği noktalarını al
        hip = landmarks[23]  # Sol kalça
        knee = landmarks[25]  # Sol diz
        ankle = landmarks[27]  # Sol ayak bileği
        
        # Diz açısını hesapla
        angle = self.calculate_angle(hip, knee, ankle)
        
        # Açı kararlı mı kontrol et
        if not self.is_stable(angle):
            return
        
        # Egzersiz başlamadıysa ve kullanıcı dik durumdaysa, egzersizi başlat
        if not self.in_progress and angle > self.max_angle - 10:
            self.in_progress = True
            self.state = "up"
            return
        
        # Egzersiz devam ediyorsa
        if self.in_progress:
            # Durumu güncelle
            if angle < self.threshold_angle and self.state == "up":
                self.state = "down"
            elif angle > self.max_angle - 20 and self.state == "down":
                self.state = "up"
                self.repetition_count += 1

class NeckFlexionExtension(ExerciseBase):
    def __init__(self):
        super().__init__()
        self.threshold_angle = 150  # Boyun fleksiyon/ekstansiyon için eşik açısı
        self.min_angle = 130  # Minimum açı (tam fleksiyon)
        self.max_angle = 170  # Maksimum açı (tam ekstansiyon)
        
    def update_state(self, landmarks):
        """
        Boyun fleksiyon/ekstansiyon egzersizi için durumu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Burun, boyun ve omuz noktalarını al
        nose = landmarks[0]  # Burun
        neck = landmarks[11]  # Boyun (omuz ortası)
        shoulder = landmarks[12]  # Sağ omuz
        
        # Boyun açısını hesapla
        angle = self.calculate_angle(nose, neck, shoulder)
        
        # Açı kararlı mı kontrol et
        if not self.is_stable(angle):
            return
        
        # Egzersiz başlamadıysa ve kullanıcı dik durumdaysa, egzersizi başlat
        if not self.in_progress and angle > self.max_angle - 10:
            self.in_progress = True
            self.state = "up"
            return
        
        # Egzersiz devam ediyorsa
        if self.in_progress:
            # Durumu güncelle
            if angle < self.threshold_angle and self.state == "up":
                self.state = "down"
            elif angle > self.max_angle - 20 and self.state == "down":
                self.state = "up"
                self.repetition_count += 1

class ShoulderRegion(ExerciseBase):
    def __init__(self):
        super().__init__()
        self.threshold_angle = 100  # Omuz bölgesi için eşik açısı
        self.min_angle = 80  # Minimum açı
        self.max_angle = 160  # Maksimum açı
        
    def update_state(self, landmarks):
        """
        Omuz bölgesi egzersizi için durumu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Omuz, dirsek ve bilek noktalarını al
        shoulder = landmarks[11]  # Sol omuz
        elbow = landmarks[13]  # Sol dirsek
        wrist = landmarks[15]  # Sol bilek
        
        # Omuz açısını hesapla
        angle = self.calculate_angle(shoulder, elbow, wrist)
        
        # Açı kararlı mı kontrol et
        if not self.is_stable(angle):
            return
        
        # Egzersiz başlamadıysa ve kullanıcı kolları aşağıdaysa, egzersizi başlat
        if not self.in_progress and angle > self.max_angle - 10:
            self.in_progress = True
            self.state = "down"
            return
        
        # Egzersiz devam ediyorsa
        if self.in_progress:
            # Durumu güncelle
            if angle < self.threshold_angle and self.state == "down":
                self.state = "up"
            elif angle > self.max_angle - 20 and self.state == "up":
                self.state = "down"
                self.repetition_count += 1

class ArmRaiseLateralFront(ExerciseBase):
    def __init__(self):
        super().__init__()
        self.threshold_angle = 90  # Kol kaldırma için eşik açısı
        self.min_angle = 30  # Minimum açı
        self.max_angle = 150  # Maksimum açı
        
    def update_state(self, landmarks):
        """
        Kol kaldırma egzersizi için durumu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Omuz, kalça ve dirsek noktalarını al
        shoulder = landmarks[11]  # Sol omuz
        hip = landmarks[23]  # Sol kalça
        elbow = landmarks[13]  # Sol dirsek
        
        # Kol açısını hesapla
        angle = self.calculate_angle(hip, shoulder, elbow)
        
        # Açı kararlı mı kontrol et
        if not self.is_stable(angle):
            return
        
        # Egzersiz başlamadıysa ve kullanıcı kolları aşağıdaysa, egzersizi başlat
        if not self.in_progress and angle < self.min_angle + 10:
            self.in_progress = True
            self.state = "down"
            return
        
        # Egzersiz devam ediyorsa
        if self.in_progress:
            # Durumu güncelle
            if angle > self.threshold_angle and self.state == "down":
                self.state = "up"
            elif angle < self.min_angle + 20 and self.state == "up":
                self.state = "down"
                self.repetition_count += 1

class ThoracicExtension(ExerciseBase):
    def __init__(self):
        super().__init__()
        self.threshold_angle = 160  # Torasik ekstansiyon için eşik açısı
        self.min_angle = 140  # Minimum açı
        self.max_angle = 180  # Maksimum açı
        
    def update_state(self, landmarks):
        """
        Torasik ekstansiyon egzersizi için durumu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Omuz, kalça ve diz noktalarını al
        shoulder = landmarks[11]  # Sol omuz
        hip = landmarks[23]  # Sol kalça
        knee = landmarks[25]  # Sol diz
        
        # Sırt açısını hesapla
        angle = self.calculate_angle(shoulder, hip, knee)
        
        # Açı kararlı mı kontrol et
        if not self.is_stable(angle):
            return
        
        # Egzersiz başlamadıysa ve kullanıcı dik durumdaysa, egzersizi başlat
        if not self.in_progress and angle > self.max_angle - 10:
            self.in_progress = True
            self.state = "up"
            return
        
        # Egzersiz devam ediyorsa
        if self.in_progress:
            # Durumu güncelle
            if angle < self.threshold_angle and self.state == "up":
                self.state = "down"
            elif angle > self.max_angle - 20 and self.state == "down":
                self.state = "up"
                self.repetition_count += 1

class LumbarSideBendingFlexion(ExerciseBase):
    def __init__(self):
        super().__init__()
        self.threshold_angle = 160  # Lumbar yan eğilme için eşik açısı
        self.min_angle = 140  # Minimum açı
        self.max_angle = 180  # Maksimum açı
        
    def update_state(self, landmarks):
        """
        Lumbar yan eğilme egzersizi için durumu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Omuz, kalça ve ayak bileği noktalarını al
        shoulder = landmarks[11]  # Sol omuz
        hip = landmarks[23]  # Sol kalça
        ankle = landmarks[27]  # Sol ayak bileği
        
        # Yan eğilme açısını hesapla
        angle = self.calculate_angle(shoulder, hip, ankle)
        
        # Açı kararlı mı kontrol et
        if not self.is_stable(angle):
            return
        
        # Egzersiz başlamadıysa ve kullanıcı dik durumdaysa, egzersizi başlat
        if not self.in_progress and angle > self.max_angle - 10:
            self.in_progress = True
            self.state = "up"
            return
        
        # Egzersiz devam ediyorsa
        if self.in_progress:
            # Durumu güncelle
            if angle < self.threshold_angle and self.state == "up":
                self.state = "down"
            elif angle > self.max_angle - 20 and self.state == "down":
                self.state = "up"
                self.repetition_count += 1

class HipAbduction(ExerciseBase):
    def __init__(self):
        super().__init__()
        self.threshold_angle = 30  # Kalça abduksiyonu için eşik açısı
        self.min_angle = 10  # Minimum açı
        self.max_angle = 45  # Maksimum açı
        
    def update_state(self, landmarks):
        """
        Kalça abduksiyonu egzersizi için durumu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Kalça, diz ve ayak bileği noktalarını al
        hip_left = landmarks[23]  # Sol kalça
        hip_right = landmarks[24]  # Sağ kalça
        knee_left = landmarks[25]  # Sol diz
        
        # Kalça açısını hesapla
        angle = self.calculate_angle(hip_right, hip_left, knee_left)
        
        # Açı kararlı mı kontrol et
        if not self.is_stable(angle):
            return
        
        # Egzersiz başlamadıysa ve kullanıcı bacakları kapalıysa, egzersizi başlat
        if not self.in_progress and angle < self.min_angle + 10:
            self.in_progress = True
            self.state = "closed"
            return
        
        # Egzersiz devam ediyorsa
        if self.in_progress:
            # Durumu güncelle
            if angle > self.threshold_angle and self.state == "closed":
                self.state = "open"
            elif angle < self.min_angle + 10 and self.state == "open":
                self.state = "closed"
                self.repetition_count += 1

class KneeFlexionExtension(ExerciseBase):
    def __init__(self):
        super().__init__()
        self.threshold_angle = 120  # Diz fleksiyon/ekstansiyon için eşik açısı
        self.min_angle = 90  # Minimum açı
        self.max_angle = 170  # Maksimum açı
        
    def update_state(self, landmarks):
        """
        Diz fleksiyon/ekstansiyon egzersizi için durumu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Kalça, diz ve ayak bileği noktalarını al
        hip = landmarks[23]  # Sol kalça
        knee = landmarks[25]  # Sol diz
        ankle = landmarks[27]  # Sol ayak bileği
        
        # Diz açısını hesapla
        angle = self.calculate_angle(hip, knee, ankle)
        
        # Açı kararlı mı kontrol et
        if not self.is_stable(angle):
            return
        
        # Egzersiz başlamadıysa ve kullanıcı bacak düzse, egzersizi başlat
        if not self.in_progress and angle > self.max_angle - 10:
            self.in_progress = True
            self.state = "extended"
            return
        
        # Egzersiz devam ediyorsa
        if self.in_progress:
            # Durumu güncelle
            if angle < self.threshold_angle and self.state == "extended":
                self.state = "flexed"
            elif angle > self.max_angle - 20 and self.state == "flexed":
                self.state = "extended"
                self.repetition_count += 1

class LegRaiseStraightLegRaise(ExerciseBase):
    def __init__(self):
        super().__init__()
        self.threshold_angle = 45  # Bacak kaldırma için eşik açısı
        self.min_angle = 10  # Minimum açı
        self.max_angle = 60  # Maksimum açı
        
    def update_state(self, landmarks):
        """
        Bacak kaldırma egzersizi için durumu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Kalça, diz ve ayak bileği noktalarını al
        hip = landmarks[23]  # Sol kalça
        knee = landmarks[25]  # Sol diz
        ankle = landmarks[27]  # Sol ayak bileği
        
        # Bacak açısını hesapla
        angle = 180 - self.calculate_angle(hip, knee, ankle)  # 180 derece çıkarıyoruz çünkü açı ters yönde
        
        # Açı kararlı mı kontrol et
        if not self.is_stable(angle):
            return
        
        # Egzersiz başlamadıysa ve kullanıcı bacak aşağıdaysa, egzersizi başlat
        if not self.in_progress and angle < self.min_angle + 10:
            self.in_progress = True
            self.state = "down"
            return
        
        # Egzersiz devam ediyorsa
        if self.in_progress:
            # Durumu güncelle
            if angle > self.threshold_angle and self.state == "down":
                self.state = "up"
            elif angle < self.min_angle + 10 and self.state == "up":
                self.state = "down"
                self.repetition_count += 1

class AbdominalCrunches(ExerciseBase):
    def __init__(self):
        super().__init__()
        self.threshold_angle = 130  # Karın egzersizi için eşik açısı
        self.min_angle = 100  # Minimum açı
        self.max_angle = 170  # Maksimum açı
        
    def update_state(self, landmarks):
        """
        Karın egzersizi için durumu günceller.
        
        Args:
            landmarks: MediaPipe tarafından tespit edilen eklem noktaları
        """
        # Omuz, kalça ve diz noktalarını al
        shoulder = landmarks[11]  # Sol omuz
        hip = landmarks[23]  # Sol kalça
        knee = landmarks[25]  # Sol diz
        
        # Karın açısını hesapla
        angle = self.calculate_angle(shoulder, hip, knee)
        
        # Açı kararlı mı kontrol et
        if not self.is_stable(angle):
            return
        
        # Egzersiz başlamadıysa ve kullanıcı düz yatıyorsa, egzersizi başlat
        if not self.in_progress and angle > self.max_angle - 10:
            self.in_progress = True
            self.state = "down"
            return
        
        # Egzersiz devam ediyorsa
        if self.in_progress:
            # Durumu güncelle
            if angle < self.threshold_angle and self.state == "down":
                self.state = "up"
            elif angle > self.max_angle - 20 and self.state == "up":
                self.state = "down"
                self.repetition_count += 1 