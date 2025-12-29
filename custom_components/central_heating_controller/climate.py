# Conceptual logic for your Python component
def calculate_hvac_target(trv_list, hvac_room_temp, max_limit):
    total_delta = 0

    for trv in trv_list:
        setpoint = trv.target_temperature
        current = trv.current_temperature

        # Calculate Delta, ignoring rooms that are satisfied
        if trv.mode == "heat" and setpoint > current:
            total_delta += (setpoint - current)

    # Apply your logic:
    if total_delta > 0.9:
        new_target = hvac_room_temp + 1.0
    elif total_delta > 0.5:
        new_target = hvac_room_temp + 0.5
    else:
        new_target = hvac_room_temp - 2.0  # Eco/Off mode

    return min(new_target, max_limit)