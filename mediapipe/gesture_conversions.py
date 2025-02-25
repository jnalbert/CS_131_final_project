import numpy as np
import hashlib

def normalize_landmarks(landmarks):
    """
    Normalize landmarks relative to wrist position and hand size.
    
    Args:
        landmarks: List of landmark objects with x, y, z attributes
        
    Returns:
        List of normalized landmark dictionaries
    """
    # Use wrist as origin
    wrist = landmarks[0]
    
    # Find the furthest point from wrist to determine scale
    max_dist = 0
    for lm in landmarks:
        dist = ((lm.x - wrist.x)**2 + (lm.y - wrist.y)**2 + (lm.z - wrist.z)**2)**0.5
        max_dist = max(max_dist, dist)
    
    if max_dist == 0:  # Avoid division by zero
        max_dist = 1
    
    # Normalize all points relative to wrist and scale
    normalized = []
    for lm in landmarks:
        normalized.append({
            'x': (lm.x - wrist.x) / max_dist,
            'y': (lm.y - wrist.y) / max_dist,
            'z': (lm.z - wrist.z) / max_dist
        })
    
    return normalized

def calculate_finger_angles(landmarks):
    """
    Calculate angles between finger joints for more stable features.
    
    Args:
        landmarks: List of landmark objects with x, y, z attributes
        
    Returns:
        List of angles (in radians)
    """
    angles = []
    
    # Define finger joint indices - (base, middle, tip) for each finger
    finger_joints = [
        (1, 2, 3),   # Thumb
        (5, 6, 7),   # Index 
        (9, 10, 11), # Middle  
        (13, 14, 15),# Ring
        (17, 18, 19) # Pinky
    ]
    
    for base_idx, mid_idx, tip_idx in finger_joints:
        # Get the three joints of the finger
        base = landmarks[base_idx]
        mid = landmarks[mid_idx]
        tip = landmarks[tip_idx]
        
        # Calculate vectors
        v1 = np.array([mid.x - base.x, mid.y - base.y, mid.z - base.z])
        v2 = np.array([tip.x - mid.x, tip.y - mid.y, tip.z - mid.z])
        
        # Handle zero vectors
        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)
        
        if v1_norm == 0 or v2_norm == 0:
            angles.append(0)
            continue
            
        v1 = v1 / v1_norm
        v2 = v2 / v2_norm
        
        # Calculate angle
        dot_product = np.clip(np.dot(v1, v2), -1.0, 1.0)
        angle = np.arccos(dot_product)
        angles.append(angle)
    
    return angles

def quantize_features(features, num_bins=10):
    """
    Quantize features into discrete bins to reduce sensitivity.
    
    Args:
        features: List of feature values
        num_bins: Number of bins to use for quantization
        
    Returns:
        List of quantized feature values
    """
    # Find min and max values
    min_val = min(features)
    max_val = max(features)
    range_val = max_val - min_val
    
    if range_val == 0:
        return [0] * len(features)
    
    # Assign each feature to a bin
    quantized = []
    for feature in features:
        normalized = (feature - min_val) / range_val
        bin_index = min(int(normalized * num_bins), num_bins - 1)
        quantized.append(bin_index)
    
    return quantized

def create_hash_from_features(features):
    """
    Create a simple hash from quantized features.
    
    Args:
        features: List of quantized feature values
        
    Returns:
        Hash string
    """
    # Convert features to string with unique separator
    feature_str = "|".join([str(f) for f in features])
    
    # Create a simple hash using first 12 characters of SHA-256
    hash_obj = hashlib.sha256(feature_str.encode())
    return hash_obj.hexdigest()[:12]

def get_gesture_hash(landmarks, salt=""):
    """
    Generate a stable hash for a hand gesture that's consistent
    for similar hand positions.
    
    Args:
        landmarks: List of landmark objects with x, y, z attributes
        salt: Optional salt string to add security
        
    Returns:
        Hash string
    """
    # Step 1: Normalize the landmarks
    normalized = normalize_landmarks(landmarks)
    
    # Step 2: Calculate angles between joints
    angles = calculate_finger_angles(landmarks)
    
    # Step 3: Quantize the angles to reduce sensitivity
    quantized_angles = quantize_features(angles, num_bins=15)
    
    # Step 4: Create hash from quantized features
    feature_hash = create_hash_from_features(quantized_angles)
    
    # Step 5: Apply cryptographic hash with salt for final password
    if salt:
        password_input = feature_hash + salt
        return hashlib.sha256(password_input.encode()).hexdigest()
    else:
        return feature_hash