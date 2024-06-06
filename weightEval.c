#include <stdio.h>

int check_weight(float weight, float threshold) {
    /*
    Assigns measured weight to corresponding bucket

    Parameters:
    weight (float): weight measured by scale
    threshold (float): predefined weight threshold

    Returns:
    bucket flag (int)

    Raises:
    None
    */
    if (weight < 0 || threshold < 0){
        return -1;      // Return -1 on wrong input
    } else if (weight < threshold) {
        return 3;       // Return BUCKET_ONE if weight is below the threshold
    } else if (weight < threshold){
        return 4;       // Return BUCKET_TWO if weight is equal to or above the threshold
    }
}
