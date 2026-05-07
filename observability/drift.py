import numpy as np

def compute_score_shift(validation_probs, scored_probs):
    """Compute basic score distribution shift metrics."""
    if not validation_probs or not scored_probs:
        return {"status": "unavailable"}
        
    val_arr = np.array(validation_probs)
    score_arr = np.array(scored_probs)
    
    val_mean = float(np.mean(val_arr))
    score_mean = float(np.mean(score_arr))
    val_std = float(np.std(val_arr))
    score_std = float(np.std(score_arr))
    
    shift = abs(val_mean - score_mean)
    warning = shift > 0.05
    
    return {
        "status": "available",
        "validation_mean": val_mean,
        "scored_mean": score_mean,
        "validation_std": val_std,
        "scored_std": score_std,
        "shift_magnitude": shift,
        "shift_warning": warning,
        "note": "This represents distribution shift, not formal concept drift."
    }
