# assessments/cv_integration.py
import cv2
import numpy as np
from pathlib import Path
from django.conf import settings
import os


class PavementImageAnalyzer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(str(image_path))
        if self.image is None:
            raise ValueError(f"Could not load image from {image_path}")

    def detect_cracks(self, threshold=127):
        """Simple crack detection using thresholding"""
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by size to remove noise
        min_area = 100
        cracks = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

        # Calculate crack percentage
        if len(cracks) > 0:
            crack_mask = np.zeros_like(gray)
            cv2.drawContours(crack_mask, cracks, -1, 255, -1)
            crack_area = np.count_nonzero(crack_mask)
            total_area = gray.shape[0] * gray.shape[1]
            crack_percentage = (crack_area / total_area) * 100
        else:
            crack_percentage = 0

        return {
            'crack_percentage': crack_percentage,
            'crack_contours': cracks,
            'binary_image': binary,
        }

    def save_analysis_result(self, output_dir=None):
        """Save analysis results as images"""
        if output_dir is None:
            output_dir = Path(settings.MEDIA_ROOT) / 'analysis_results'

        os.makedirs(output_dir, exist_ok=True)

        # Get filename without extension
        base_name = Path(self.image_path).stem

        # Run crack detection
        crack_results = self.detect_cracks()

        # Save binary image
        binary_path = Path(output_dir) / f"{base_name}_binary.jpg"
        cv2.imwrite(str(binary_path), crack_results['binary_image'])

        # Save contour visualization
        contour_image = self.image.copy()
        cv2.drawContours(contour_image, crack_results['crack_contours'], -1, (0, 0, 255), 2)
        contour_path = Path(output_dir) / f"{base_name}_contours.jpg"
        cv2.imwrite(str(contour_path), contour_image)

        return {
            'binary_image_path': str(binary_path),
            'contour_image_path': str(contour_path),
            'crack_percentage': crack_results['crack_percentage'],
        }