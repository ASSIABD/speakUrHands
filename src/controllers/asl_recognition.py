import numpy as np
import cv2
import os
import time
import sys
import base64
import threading

IMAGE_SIZE = (128, 128)
CLASS_NAMES = [chr(i) for i in range(ord('A'), ord('Z') + 1)] + ['nothing', 'del', 'space']

def find_model_path():
    candidates = [
        'training/best_model.keras',
        'best_model.keras',
        '../training/best_model.keras',
        'Mini_Projet_Java/Mini_Projet_Java/Code_Source/training/best_model.keras'
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    return os.path.abspath(candidates[0])

PREDICTION_INTERVAL = 2.5  # Snappier prediction interval (reduced from 5s)

# Global model state for background loading
model = None
model_loading = True
model_error = None

def load_model_worker():
    """Load TensorFlow model in background thread to avoid blocking camera startup."""
    global model, model_loading, model_error
    try:
        # Suppress verbose TF logging
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        import tensorflow as tf

        abs_model_path = find_model_path()
        if not os.path.exists(abs_model_path):
            model_error = f"Model file not found at {abs_model_path}"
            model_loading = False
            print(f"STATUS:Error - {model_error}", file=sys.stderr)
            sys.stderr.flush()
            return

        # Reconstruct MobileNetV2 architecture with 26 classes
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=(128, 128, 3),
            include_top=False,
            weights=None
        )
        inputs = tf.keras.Input(shape=(128, 128, 3))
        x = base_model(inputs, training=False)
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        outputs = tf.keras.layers.Dense(26, activation='softmax')(x)
        built_model = tf.keras.Model(inputs, outputs)

        built_model.load_weights(abs_model_path)
        
        # Warmup inference
        dummy = np.zeros((1, 128, 128, 3), dtype=np.float32)
        _ = built_model(dummy, training=False)

        model = built_model
        model_loading = False
        print(f"STATUS:Model loaded successfully from {abs_model_path}", file=sys.stderr)
        sys.stderr.flush()
    except Exception as e:
        model_error = str(e)
        model_loading = False
        print(f"STATUS:Error - Failed to load model: {e}", file=sys.stderr)
        sys.stderr.flush()

def preprocess_frame(frame):
    """Preprocess a single camera frame for model prediction."""
    try:
        img = cv2.resize(frame, IMAGE_SIZE)
        img = img.astype(np.float32) / 255.0  
        return np.expand_dims(img, axis=0) 
    except Exception as e:
        print(f"STATUS:Error - Frame preprocessing failed: {e}", file=sys.stderr)
        sys.stderr.flush()
        return None

def predict_from_frame(loaded_model, frame):
    """Predict hand gesture from a cropped frame using the loaded model."""
    try:
        processed_img = preprocess_frame(frame)
        if processed_img is None:
            return "Error", 0.0

        predictions = loaded_model(processed_img, training=False)
        preds_numpy = predictions.numpy()
        predicted_index = np.argmax(preds_numpy[0])
        confidence = float(preds_numpy[0][predicted_index])
        predicted_class = CLASS_NAMES[predicted_index]
        return predicted_class, confidence
    except Exception as e:
        print(f"STATUS:Error - Prediction failed: {e}", file=sys.stderr)
        sys.stderr.flush()
        return "Error", 0.0

def handle_prediction_result(prediction, translation_history):
    """Update the translation history based on the prediction result."""
    if prediction == 'del' and translation_history:
        translation_history.pop()
    elif prediction == 'space':
        if not translation_history or translation_history[-1] != ' ':
            translation_history.append(' ')
    elif prediction not in ['nothing', 'del', 'space']:
        last_meaningful_char = next((char for char in reversed(translation_history) if char not in (' ', 'nothing', 'del')), None)
        if prediction != last_meaningful_char:
            translation_history.append(prediction)

    return translation_history 

def realtime_detection_for_java():
    """Main loop: starts camera immediately and streams frames while model loads in background."""
    global model, model_loading, model_error

    # Start model loading asynchronously in background thread
    loader_thread = threading.Thread(target=load_model_worker, daemon=True)
    loader_thread.start()

    # Open camera immediately with DirectShow for instant access on Windows
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("STATUS:Error - Cannot access camera.", file=sys.stderr)
        sys.stderr.flush()
        time.sleep(3)
        sys.exit(1)

    print("STATUS:Camera opened. Starting detection loop.", file=sys.stderr)
    sys.stderr.flush()

    last_prediction_time = time.time()
    last_status_sent_time = 0
    translation_history = []
    ready_announced = False

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("STATUS:Warning - Failed to grab frame. Retrying...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(0.1)
                if not cap.isOpened():
                    print("STATUS:Error - Camera became inaccessible.", file=sys.stderr)
                    sys.stderr.flush()
                    break 
                continue

            frame = cv2.flip(frame, 1) 
            current_time = time.time()

            # Center guide box calculation
            h, w, _ = frame.shape
            box_size = min(w, h, 250)
            x1 = (w - box_size) // 2
            y1 = (h - box_size) // 2
            x2 = x1 + box_size
            y2 = y1 + box_size

            # Create copy for display
            display_frame = frame.copy()

            if model_loading:
                # Orange box while AI model is warming up in background
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
                cv2.putText(display_frame, "Loading AI Model...", (x1 - 10, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                if current_time - last_status_sent_time >= 2.0:
                    print("PREDICTION:Loading AI Model... please wait")
                    sys.stdout.flush()
                    last_status_sent_time = current_time
            elif model_error:
                # Red box if error
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(display_frame, "Model Error", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                # Green guide box when ready
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (113, 204, 46), 2)
                cv2.putText(display_frame, "Place Hand Here", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (113, 204, 46), 2)
                
                if not ready_announced:
                    print("PREDICTION:Ready! Show your sign")
                    sys.stdout.flush()
                    ready_announced = True

            # Encode and stream frame to JavaFX
            try:
                ret_encode, buffer = cv2.imencode('.jpg', display_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                if ret_encode:
                    frame_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
                    print(f"FRAME_B64:{frame_base64}")
                    sys.stdout.flush()
            except Exception as e:
                print(f"STATUS:Error - Frame sending failed: {e}", file=sys.stderr)
                sys.stderr.flush()

            # Prediction interval
            if not model_loading and model is not None:
                if current_time - last_prediction_time >= PREDICTION_INTERVAL:
                    cropped_hand = frame[y1:y2, x1:x2]
                    prediction, confidence = predict_from_frame(model, cropped_hand)

                    if prediction != "Error":
                        translation_history = handle_prediction_result(prediction, translation_history)

                    print(f"PREDICTION:{prediction}")
                    display_translation = ''.join([c for c in translation_history if c not in ('nothing', 'del')])
                    print(f"TRANSLATION:{display_translation}")
                    sys.stdout.flush()

                    last_prediction_time = current_time

            time.sleep(0.033)  # Smooth ~30 FPS

    except KeyboardInterrupt:
        print("STATUS:Received KeyboardInterrupt. Shutting down.", file=sys.stderr)
        sys.stderr.flush()
    except Exception as e:
        print(f"STATUS:Error - Unexpected loop error: {e}", file=sys.stderr)
        sys.stderr.flush()
    finally:
        print("STATUS:Initiating shutdown sequence.", file=sys.stderr)
        if cap.isOpened():
            cap.release()
            print("STATUS:Camera released.", file=sys.stderr)
        print("STATUS:Shutdown complete.", file=sys.stderr)
        sys.stderr.flush()
        sys.stdout.flush()

if __name__ == "__main__":
    realtime_detection_for_java()