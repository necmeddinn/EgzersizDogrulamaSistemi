import cv2
import mediapipe as mp
import traceback
from exercise_detection import ExerciseDetection

def main():
    try:
        # MediaPipe Pose modelini başlat
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

        cap = cv2.VideoCapture(0)  # Kamerayı aç
        
        # ExerciseDetection sınıfını başlat
        try:
            exercise_detection = ExerciseDetection()
            print("ExerciseDetection başarıyla başlatıldı.")
        except Exception as e:
            print(f"ExerciseDetection başlatılırken hata oluştu: {e}")
            traceback.print_exc()
            return

        print("Kamera açıldı. Egzersiz Seçimi:")
        
        selected_exercise = None

        # Kullanıcıdan egzersiz seçimi
        while selected_exercise is None:
            ret, frame = cap.read()
            if not ret:
                print("Kamera açılmadı.")
                break

            # Seçim yapılmadıysa ekranda talimatları göster
            cv2.putText(frame, "Select Exercise:", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

            # Egzersiz seçeneklerini dikey olarak göster
            exercises = ["Squat", "Neck Flexion", "Shoulder", "Arm Raise", 
                        "Thoracic Extension", "Lumbar Side Bending", 
                        "Hip Abduction", "Knee Flexion", "Leg Raise", 
                        "Abdominal Crunches"]
            
            for i, exercise in enumerate(exercises):
                cv2.putText(frame, f"{i}: {exercise}", (10, 100 + i * 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)

            # Kullanıcıdan egzersiz seçimi
            key = cv2.waitKey(1) & 0xFF
            if key in [ord(str(i)) for i in range(10)]:  # 0-9 arası tuşlar
                exercise_names = ["squat", "neck_flexion_extension", "shoulder_region", 
                                "arm_raise_lateral_front", "thoracic_extension", 
                                "lumbar_side_bending_flexion", "hip_abduction", 
                                "knee_flexion_extension", "leg_raise_straight_leg_raise", 
                                "abdominal_crunches"]
                
                selected_index = key - ord('0')
                if selected_index < len(exercise_names):
                    selected_exercise = exercise_names[selected_index]
                    print(f"Selected exercise: {selected_exercise}")  # Seçilen egzersizi yazdır
                    
                    # Seçilen egzersizin ExerciseDetection içinde var olduğunu kontrol et
                    if selected_exercise not in exercise_detection.exercises:
                        print(f"Hata: {selected_exercise} egzersizi ExerciseDetection içinde bulunamadı.")
                        print(f"Mevcut egzersizler: {list(exercise_detection.exercises.keys())}")
                        selected_exercise = None  # Seçimi sıfırla
                        continue

            # Görüntüyü göster
            cv2.imshow('Exercise Selection', frame)

            if key == ord('q'):
                break

        # Egzersiz seçimi yapıldıktan sonra "Exercise Selection" penceresini kapat
        cv2.destroyWindow('Exercise Selection')

        # Egzersiz seçimi yapıldıktan sonra
        while cap.isOpened() and selected_exercise is not None:
            try:
                ret, frame = cap.read()
                if not ret:
                    print("Kamera akışında hata.")
                    break

                # BGR'yi RGB'ye çeviriyoruz
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image)

                # Eğer poz tespit edildiyse
                if results.pose_landmarks:
                    # Landmark nesnelerini doğrudan kullan, tuple'a dönüştürme
                    landmarks = results.pose_landmarks.landmark
                    
                    # Eklemleri çiz
                    for i, landmark in enumerate(landmarks):
                        x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)  # Eklemleri yeşil daire ile çiz

                    # Eklemler arası bağlantıları çiz
                    connections = mp_pose.POSE_CONNECTIONS
                    for connection in connections:
                        start_idx, end_idx = connection
                        start_point = landmarks[start_idx]
                        end_point = landmarks[end_idx]
                        cv2.line(frame, (int(start_point.x * frame.shape[1]), int(start_point.y * frame.shape[0])),
                                (int(end_point.x * frame.shape[1]), int(end_point.y * frame.shape[0])), (255, 0, 0), 2)

                    # Egzersiz durumunu güncelle
                    try:
                        # Landmark nesnelerini doğrudan kullan
                        exercise_detection.exercises[selected_exercise].update_state(landmarks)
                        repetition_count = exercise_detection.exercises[selected_exercise].get_repetition_count()
                        exercise_results = exercise_detection.detect_exercises(landmarks)
                        
                        # Sonuçları ekrana yazdır - DAHA BÜYÜK YAZI
                        cv2.putText(frame, f"Repetitions: {repetition_count}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                        cv2.putText(frame, f"{selected_exercise.capitalize()}: {exercise_results[selected_exercise]}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                        
                        # Egzersiz adını ekrana yazdır - DAHA BÜYÜK YAZI
                        cv2.putText(frame, f"Selected Exercise: {selected_exercise.capitalize()}", (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
                    except Exception as e:
                        print(f"Egzersiz durumu güncellenirken hata oluştu: {e}")
                        traceback.print_exc()
                        cv2.putText(frame, f"Error: {str(e)}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

                else:
                    cv2.putText(frame, "No keypoints detected", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

                # Görüntüyü göster
                cv2.imshow('Exercise Detection', frame)

                # Kullanıcıdan çıkış tuşu kontrolü
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            except Exception as e:
                print(f"Egzersiz tespiti sırasında hata oluştu: {e}")
                traceback.print_exc()
                break

        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Program çalışırken beklenmeyen bir hata oluştu: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()