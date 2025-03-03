class UpdateState:
    def __init__(self):
        self.lowered_position = False  # Aşağı pozisyonda mı?
        self.repetition_count = 0  # Tekrar sayısı

    def count_repetitions(self, validate_function):
        if validate_function():
            if not self.lowered_position:
                self.lowered_position = True  # Aşağı pozisyona geçildi
        else:
            if self.lowered_position:
                self.repetition_count += 1  # Tekrar sayısını artır
                self.lowered_position = False  # Yukarı pozisyona geçildi

    def get_repetition_count(self):
        return self.repetition_count
