from flask import Flask, render_template, Response, jsonify, request
import cv2
import base64
from color_detector import ColorDetector
import threading
import time

app = Flask(__name__)

# Global detector instance
detector = ColorDetector()
detection_active = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/detection')
def detection():
    return render_template('detection.html')

@app.route('/start_detection', methods=['POST'])
def start_detection():
    global detection_active
    
    try:
        detector.initialize_camera()
        detector.is_running = True
        detection_active = True
        
        return jsonify({
            'status': 'success',
            'message': 'Color detection started successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start detection: {str(e)}'
        })

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global detection_active
    
    try:
        detector.is_running = False
        detection_active = False
        detector.release_camera()
        
        return jsonify({
            'status': 'success',
            'message': 'Color detection stopped successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to stop detection: {str(e)}'
        })

@app.route('/get_frame')
def get_frame():
    if not detection_active:
        return jsonify({'status': 'inactive'})
    
    try:
        frame_base64, color_info = detector.get_frame_with_detection()
        
        if frame_base64 and color_info:
            return jsonify({
                'status': 'success',
                'frame': f'data:image/jpeg;base64,{frame_base64}',
                'color_info': color_info
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to capture frame'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)