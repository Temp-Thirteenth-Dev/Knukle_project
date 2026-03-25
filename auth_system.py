import cv2
import os
import numpy as np

class KnuckleAuthSystem:
    def __init__(self, db_path="database"):
        self.db_path = db_path
        self.threshold = 85  # Adjust this: Higher = Stricter, Lower = Easier
        os.makedirs(self.db_path, exist_ok=True)

    def _preprocess_image(self, image_path):
        """
        Loads an image, converts to grayscale, resizes, and enhances.
        """
        if not os.path.exists(image_path):
            return None

        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return None

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Resize to standard size for consistency
        # (Width, Height)
        gray = cv2.resize(gray, (300, 300))

        # --- Enhancement ---
        # 1. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # 2. Sharpening (High Pass Filter)
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
        high_pass = cv2.subtract(enhanced, blurred)
        sharpened = cv2.addWeighted(enhanced, 1.0, high_pass, 1.5, 0)

        return sharpened

    def register_user(self, user_id, image_path):
        """
        Saves a user's knuckle image into the database.
        """
        user_folder = os.path.join(self.db_path, user_id)
        os.makedirs(user_folder, exist_ok=True)
        
        dest_path = os.path.join(user_folder, "registered.bmp")
        
        # Read original image
        img = cv2.imread(image_path)
        if img is None:
            return False, "Invalid image file."

        # Resize and save for consistency
        img = cv2.resize(img, (300, 300))
        cv2.imwrite(dest_path, img)
        
        return True, f"User '{user_id}' registered successfully!"

    def verify_user(self, user_id, login_image_path):
        """
        Compares login image with the stored image for the given user_id.
        Returns: (Success: Bool, Score: Int, Message: Str)
        """
        user_folder = os.path.join(self.db_path, user_id)
        registered_img_path = os.path.join(user_folder, "registered.bmp")

        # 1. Check if user exists
        if not os.path.exists(registered_img_path):
            return False, 0, f"User '{user_id}' not found in database."

        # 2. Preprocess both images
        img1 = self._preprocess_image(registered_img_path)
        img2 = self._preprocess_image(login_image_path)

        if img1 is None or img2 is None:
            return False, 0, "Error processing images."

        # 3. SIFT Feature Extraction
        try:
            # SIFT is in opencv-contrib-python
            sift = cv2.SIFT_create()
            kp1, desc1 = sift.detectAndCompute(img1, None)
            kp2, desc2 = sift.detectAndCompute(img2, None)
        except Exception as e:
            return False, 0, f"SIFT Error: {e}"

        if desc1 is None or desc2 is None:
            return False, 0, "Could not detect features (image might be too blurry)."

        # 4. Feature Matching
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(desc1, desc2, k=2)

        # 5. Ratio Test (Lowe's ratio test)
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        score = len(good_matches)

        # 6. Decision
        if score >= self.threshold:
            return True, score, f"Access Granted. Match Score: {score}"
        else:
            return False, score, f"Access Denied. Match Score: {score} (Required: {self.threshold})"

    def visualize_match(self, user_id, login_image_path):
        """
        Visualizes the SIFT feature matching between the registered image and the login image.
        Uses matplotlib to show the results.
        """
        import matplotlib.pyplot as plt

        user_folder = os.path.join(self.db_path, user_id)
        registered_img_path = os.path.join(user_folder, "registered.bmp")

        # 1. Check if user exists
        if not os.path.exists(registered_img_path):
            return False, f"User '{user_id}' not found in database."

        # 2. Preprocess both images
        img1 = self._preprocess_image(registered_img_path)
        img2 = self._preprocess_image(login_image_path)

        if img1 is None or img2 is None:
            return False, "Error processing images."

        # 3. SIFT Feature Extraction
        try:
            sift = cv2.SIFT_create()
            kp1, desc1 = sift.detectAndCompute(img1, None)
            kp2, desc2 = sift.detectAndCompute(img2, None)
        except Exception as e:
            return False, f"SIFT Error: {e}"

        if desc1 is None or desc2 is None:
            return False, "Could not detect features."

        # 4. Feature Matching
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(desc1, desc2, k=2)

        # 5. Ratio Test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        # 6. Draw Matches
        result = cv2.drawMatches(
            img1, kp1,
            img2, kp2,
            good_matches[:50], None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )

        plt.figure(figsize=(12,6))
        plt.imshow(result, cmap='gray')
        plt.title(f"Admin Visualization - Matches found: {len(good_matches)}")
        plt.axis('off')
        plt.show()

        return True, "Visualization launched successfully."

    def visualize_match_web(self, user_id, login_image_path):
        """
        Web-friendly visualization that returns a Base64-encoded PNG string
        instead of opening a pyplot window.
        """
        import base64

        user_folder = os.path.join(self.db_path, user_id)
        registered_img_path = os.path.join(user_folder, "registered.bmp")

        if not os.path.exists(registered_img_path):
            return False, f"User '{user_id}' not found in database.", 0

        img1 = self._preprocess_image(registered_img_path)
        img2 = self._preprocess_image(login_image_path)

        if img1 is None or img2 is None:
            return False, "Error processing images.", 0

        try:
            sift = cv2.SIFT_create()
            kp1, desc1 = sift.detectAndCompute(img1, None)
            kp2, desc2 = sift.detectAndCompute(img2, None)
        except Exception as e:
            return False, f"SIFT Error: {e}", 0

        if desc1 is None or desc2 is None:
            return False, "Could not detect features.", 0

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(desc1, desc2, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        result = cv2.drawMatches(
            img1, kp1,
            img2, kp2,
            good_matches[:50], None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )

        _, buffer = cv2.imencode('.png', result)
        img_str = base64.b64encode(buffer).decode('utf-8')

        return True, img_str, len(good_matches)
