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
        (1, 2, 4),    # Thumb base to tip
        (5, 6, 8),    # Index base to tip
        (9, 10, 12),  # Middle base to tip
        (13, 14, 16), # Ring base to tip
        (17, 18, 20), # Pinky base to tip
        (0, 5, 17),   # Palm width (wrist to index to pinky)
        (5, 9, 13),   # Knuckle line (index to middle to ring)
        (9, 13, 17)   # Knuckle line (middle to ring to pinky)
    ]
    
    for base_idx, mid_idx, tip_idx in finger_joints:
        # Get the three points to form an angle
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
    
    # Add relative finger positions (extended or not)
    # Thumb
    angles.append(1.0 if landmarks[4].x < landmarks[3].x else 0.0)
    # Index
    angles.append(1.0 if landmarks[8].y < landmarks[6].y else 0.0)
    # Middle
    angles.append(1.0 if landmarks[12].y < landmarks[10].y else 0.0)
    # Ring
    angles.append(1.0 if landmarks[16].y < landmarks[14].y else 0.0)
    # Pinky
    angles.append(1.0 if landmarks[20].y < landmarks[18].y else 0.0)
    
    return angles

def quantize_features(features, num_bins=5):
    """
    Quantize features into discrete bins to reduce sensitivity.
    
    Args:
        features: List of feature values
        num_bins: Number of bins to use for quantization
        
    Returns:
        List of quantized feature values
    """
    # Pre-defined bin edges for more consistent quantization
    angle_bins = np.linspace(0, np.pi, num_bins + 1)
    finger_state_bins = [0, 0.5, 1]  # For binary finger state features
    
    quantized = []
    for i, feature in enumerate(features):
        # Use different quantization for different feature types
        if i >= len(features) - 5:  # Last 5 features are finger states (binary)
            bins = finger_state_bins
        else:  # Angular features
            bins = angle_bins
            
        # Find the bin index
        bin_index = np.digitize(feature, bins) - 1
        bin_index = max(0, min(bin_index, len(bins) - 2))  # Clamp to valid range
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
    
    # Create a simple hash
    # Use a simpler hashing approach for better stability
    hash_val = 0
    for feature in features:
        hash_val = (hash_val * 31 + feature) & 0xFFFFFFFF
    
    return format(hash_val, 'x')[:8]  # Return 8-character hex string

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
    # Skip normalization as quantization and angle-based features provide enough stability
    
    # Calculate angles between joints and add finger extension state
    angles = calculate_finger_angles(landmarks)
    
    # Quantize the angles and states to reduce sensitivity (using fewer bins)
    quantized_features = quantize_features(angles, num_bins=0)
    
    # Create hash from quantized features
    feature_hash = create_hash_from_features(quantized_features)
    
    # Apply salt if provided (simplified for better stability)
    if salt:
        salted_features = quantized_features + [ord(c) % 5 for c in salt[:3]]
        return create_hash_from_features(salted_features)
    else:
        return feature_hash