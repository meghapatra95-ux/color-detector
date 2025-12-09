import cv2
import numpy as np
from collections import Counter
from sklearn.cluster import KMeans
import base64

class ColorDetector:
    def __init__(self, camera_index=0, k_clusters=3):
        self.camera_index = camera_index
        self.k_clusters = k_clusters
        self.cap = None
        self.dominant_color = None
        self.is_running = False
        
    def initialize_camera(self):
        """Initialize the webcam"""
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                raise Exception("Could not open webcam")
        return True
    
    def release_camera(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()
            self.cap = None
        self.is_running = False
    
    def get_dominant_color(self, image, k=None):
        """Extract dominant colors from image using K-means clustering"""
        if k is None:
            k = self.k_clusters
            
        # Resize image to speed up processing
        image = cv2.resize(image, (100, 100))
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Reshape image to be a list of pixels
        pixels = image_rgb.reshape(-1, 3)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
        kmeans.fit(pixels)
        
        # Get the dominant colors
        colors = kmeans.cluster_centers_
        
        # Count labels to find the most dominant color
        labels = kmeans.labels_
        label_counts = Counter(labels)
        dominant_index = label_counts.most_common(1)[0][0]
        
        return colors[dominant_index].astype(int)
    
    def rgb_to_hex(self, rgb):
        """Convert RGB to HEX color code"""
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    
    def get_color_name(self, rgb):
        """Approximate color name based on RGB values"""
        r, g, b = rgb
        
        # Extended color definitions with thresholds
        color_ranges = {
            'Red': ((200, 0, 0), (255, 100, 100)),
            'Green': ((0, 200, 0), (100, 255, 100)),
            'Blue': ((0, 0, 200), (100, 100, 255)),
            'Yellow': ((200, 200, 0), (255, 255, 100)),
            'Orange': ((200, 100, 0), (255, 165, 50)),
            'Purple': ((100, 0, 100), (180, 80, 180)),
            'Pink': ((200, 100, 150), (255, 182, 193)),
            'Brown': ((100, 40, 0), (165, 42, 42)),
            'Black': ((0, 0, 0), (50, 50, 50)),
            'White': ((200, 200, 200), (255, 255, 255)),
            'Gray': ((100, 100, 100), (180, 180, 180)),
            'Cyan': ((0, 200, 200), (100, 255, 255)),
            'Magenta': ((200, 0, 200), (255, 100, 255))
        }
        
        # Check if color falls within any defined range
        for color_name, (lower, upper) in color_ranges.items():
            if (lower[0] <= r <= upper[0] and 
                lower[1] <= g <= upper[1] and 
                lower[2] <= b <= upper[2]):
                return color_name
        
        # If no exact match, find closest color
        colors_exact = {
            'Red': (255, 0, 0),
            'Green': (0, 255, 0),
            'Blue': (0, 0, 255),
            'Yellow': (255, 255, 0),
            'Orange': (255, 165, 0),
            'Purple': (128, 0, 128),
            'Pink': (255, 192, 203),
            'Brown': (165, 42, 42),
            'Black': (0, 0, 0),
            'White': (255, 255, 255),
            'Gray': (128, 128, 128),
            'Cyan': (0, 255, 255),
            'Magenta': (255, 0, 255)
        }
        
        min_distance = float('inf')
        closest_color = "Unknown"
        
        for name, color_rgb in colors_exact.items():
            distance = np.sqrt((r - color_rgb[0])**2 + 
                             (g - color_rgb[1])**2 + 
                             (b - color_rgb[2])**2)
            if distance < min_distance:
                min_distance = distance
                closest_color = name
        
        return closest_color
    
    def process_frame(self, frame):
        """Process a single frame and return color information"""
        height, width = frame.shape[:2]
        
        # Calculate center region coordinates
        region_ratio = 0.5
        region_height = int(height * region_ratio)
        region_width = int(width * region_ratio)
        
        start_y = (height - region_height) // 2
        start_x = (width - region_width) // 2
        end_y = start_y + region_height
        end_x = start_x + region_width
        
        # Extract center region
        center_region = frame[start_y:end_y, start_x:end_x]
        
        # Get dominant color
        dominant_rgb = self.get_dominant_color(center_region)
        color_name = self.get_color_name(dominant_rgb)
        hex_color = self.rgb_to_hex(dominant_rgb)
        
        # Draw detection area on frame
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 2)
        
        color_info = {
            'rgb': dominant_rgb.tolist(),
            'hex': hex_color,
            'name': color_name,
            'region_coords': (start_x, start_y, end_x, end_y)
        }
        
        self.dominant_color = color_info
        return frame, color_info
    
    def get_frame_with_detection(self):
        """Get a single frame with color detection"""
        if not self.cap or not self.is_running:
            return None, None
        
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        
        processed_frame, color_info = self.process_frame(frame)
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return frame_base64, color_info