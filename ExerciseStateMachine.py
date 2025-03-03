class ExerciseStateMachine:
    def __init__(self, exercise_name, joint_name, lowering_threshold, rising_threshold):
        """
        Genel egzersiz state machine yapısı.
        
        :param exercise_name: Egzersizin adı (örneğin: "Squat", "Shoulder Raise")
        :param joint_name: Kontrol edilecek eklem (örneğin: "knee", "shoulder")
        :param lowering_threshold: Çömelme/bükülme için eşik değeri
        :param rising_threshold: Kalkma/açılma için eşik değeri
        """
        self.exercise_name = exercise_name
        self.joint_name = joint_name
        self.lowering_threshold = lowering_threshold  # Bükülme eşiği
        self.rising_threshold = rising_threshold  # Açılma eşiği
        self.state = "START"  # Başlangıç durumu
        self.repetition_count = 0  # Tekrar sayacı

    def update_state(self, joint_angle):
        """Eklem açısına göre state machine güncellenir."""
        if self.state == "START":
            if joint_angle < self.lowering_threshold:  # Hareket başladı (bükülme/çömelme)
                self.state = "LOWERING"

        elif self.state == "LOWERING":
            if joint_angle > self.rising_threshold:  # Hareket tamamlandı (kalkma)
                self.state = "RISING"

        elif self.state == "RISING":
            if joint_angle >= self.rising_threshold + 10:  # Tam açılma sağlanırsa tekrar tamamlanır
                self.repetition_count += 1
                self.state = "START"

    def get_state(self):
        return self.state

    def get_repetition_count(self):
        return self.repetition_count 