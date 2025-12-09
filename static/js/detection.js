class ColorDetectionApp {
    constructor() {
        this.isDetecting = false;
        this.animationFrame = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.getElementById('startBtn').addEventListener('click', () => this.startDetection());
        document.getElementById('stopBtn').addEventListener('click', () => this.stopDetection());
    }

    async startDetection() {
        try {
            const response = await fetch('/start_detection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.isDetecting = true;
                this.updateUI(true);
                this.startVideoFeed();
            } else {
                this.showAlert('Failed to start detection: ' + data.message, 'danger');
            }
        } catch (error) {
            this.showAlert('Error starting detection: ' + error.message, 'danger');
        }
    }

    async stopDetection() {
        try {
            const response = await fetch('/stop_detection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.isDetecting = false;
                this.updateUI(false);
                if (this.animationFrame) {
                    cancelAnimationFrame(this.animationFrame);
                }
            } else {
                this.showAlert('Failed to stop detection: ' + data.message, 'danger');
            }
        } catch (error) {
            this.showAlert('Error stopping detection: ' + error.message, 'danger');
        }
    }

    async startVideoFeed() {
        if (!this.isDetecting) return;

        try {
            const response = await fetch('/get_frame');
            const data = await response.json();

            if (data.status === 'success') {
                this.updateVideoFeed(data.frame);
                this.updateColorInfo(data.color_info);
            } else if (data.status === 'inactive') {
                // Detection was stopped
                return;
            }

            // Continue the loop
            this.animationFrame = requestAnimationFrame(() => this.startVideoFeed());
        } catch (error) {
            console.error('Error fetching frame:', error);
            // Retry after a short delay
            setTimeout(() => this.startVideoFeed(), 100);
        }
    }

    updateVideoFeed(frameData) {
        const videoFeed = document.getElementById('videoFeed');
        const placeholder = document.getElementById('placeholder');

        videoFeed.src = frameData;
        videoFeed.classList.remove('d-none');
        placeholder.classList.add('d-none');
    }

    updateColorInfo(colorInfo) {
        if (!colorInfo) return;

        const colorSwatch = document.getElementById('colorSwatch');
        const colorName = document.getElementById('colorName');
        const hexValue = document.getElementById('hexValue');
        const rgbValue = document.getElementById('rgbValue');
        const colorDetails = document.getElementById('colorDetails');

        // Update color swatch
        colorSwatch.style.backgroundColor = colorInfo.hex;

        // Update color name
        colorName.textContent = colorInfo.name;
        colorName.style.color = colorInfo.hex;

        // Update color values
        hexValue.textContent = colorInfo.hex;
        rgbValue.textContent = `rgb(${colorInfo.rgb.join(', ')})`;

        // Show color details
        colorDetails.classList.remove('d-none');

        // Add visual feedback
        this.animateColorChange();
    }

    animateColorChange() {
        const colorSwatch = document.getElementById('colorSwatch');
        colorSwatch.style.transform = 'scale(1.1)';
        setTimeout(() => {
            colorSwatch.style.transform = 'scale(1)';
        }, 200);
    }

    updateUI(isDetecting) {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const videoFeed = document.getElementById('videoFeed');
        const placeholder = document.getElementById('placeholder');

        if (isDetecting) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            startBtn.classList.remove('btn-success');
            startBtn.classList.add('btn-secondary');
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            startBtn.classList.remove('btn-secondary');
            startBtn.classList.add('btn-success');
            
            videoFeed.classList.add('d-none');
            placeholder.classList.remove('d-none');
            
            // Reset color display
            document.getElementById('colorName').textContent = 'No Color Detected';
            document.getElementById('colorName').style.color = '';
            document.getElementById('colorDetails').classList.add('d-none');
            document.getElementById('colorSwatch').style.backgroundColor = '#f8f9fa';
        }
    }

    showAlert(message, type) {
        // Remove existing alerts
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.querySelector('.container.py-5').insertBefore(alertDiv, document.querySelector('.container.py-5').firstChild);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ColorDetectionApp();
});