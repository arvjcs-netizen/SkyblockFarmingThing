# hypixel skyblock macro, allows for left and right movement that changes each time, makes a noise if it moves, you can tune these numbers for your farm.






import minescript
import time
import random
import winsound

# ==================== CONFIGURATION ====================
LONG_MIN, LONG_MAX = 19.7, 20.1  
SHORT_MIN, SHORT_MAX = 1.3, 1.4   

# Buffers for long side-to-side runs
LONG_STARTUP = 2.0  
LONG_END = 2.5      

# Buffers for short forward steps (since total time is only ~1.2s)
SHORT_STARTUP = 0.2  
SHORT_END = 0.35     
# =======================================================

def play_alert_sound():
    try:
        for _ in range(3):
            winsound.Beep(1000, 300)
            time.sleep(0.1)
    except Exception:
        pass

def walk_with_velocity_monitor(press_func, min_time, max_time, direction_name):
    """Monitors velocity while safely ignoring acceleration startup and wall impacts for all directions."""
    duration = random.uniform(min_time, max_time)
    minescript.echo(f"Moving {direction_name} for {duration:.2f} seconds...")
    
    press_func(True)
    start_time = time.time()
    
    # Assign specific startup and end buffers depending on the movement type
    if direction_name in ["Left", "Right"]:
        startup_buffer = LONG_STARTUP
        end_buffer = LONG_END
    else:  # Forward
        startup_buffer = SHORT_STARTUP
        end_buffer = SHORT_END
        
    buffer_start_time = start_time + startup_buffer
    buffer_end_time = (start_time + duration) - end_buffer
    
    last_pos = minescript.player_position()
    
    try:
        while time.time() - start_time < duration:
            time.sleep(0.05)
            
            current_time = time.time()
            current_pos = minescript.player_position()
            
            delta_x = current_pos[0] - last_pos[0]
            delta_z = current_pos[2] - last_pos[2]
            
            vel_x = abs(delta_x) * 20.0
            vel_z = abs(delta_z) * 20.0
            
            # Only check velocity when we are safely in the middle window (ignoring startup and wall hits)
            if buffer_start_time <= current_time <= buffer_end_time:
                # --- LEFT / RIGHT MONITORING ---
                if direction_name in ["Left", "Right"]:
                    if vel_z < 3.0:
                        play_alert_sound()
                        raise Exception(f"Z velocity dropped during {direction_name} mid-run! Got {vel_z:.1f} (Stuck or blocked)")
                    
                    if vel_x > 0.5:
                        play_alert_sound()
                        raise Exception(f"Unexpected X movement during {direction_name}! Vel X: {vel_x:.1f}")
                        
                # --- FORWARD MONITORING ---
                elif direction_name == "Forward":
                    if vel_x < 2.0:
                        play_alert_sound()
                        raise Exception(f"Forward velocity stalled mid-step! Vel X: {vel_x:.1f}")
                    
                    if vel_z > 0.5:
                        play_alert_sound()
                        raise Exception(f"Unexpected Z drift during Forward! Vel Z: {vel_z:.1f}")

            last_pos = current_pos

    finally:
        press_func(False)
        time.sleep(0.1)

# Main farming loop
try:
    minescript.echo("Starting fully buffered velocity-monitored loop. Run \\kill to stop!")
    minescript.player_press_attack(True)
    
    while True:
        walk_with_velocity_monitor(minescript.player_press_left, LONG_MIN, LONG_MAX, "Left")
        walk_with_velocity_monitor(minescript.player_press_forward, SHORT_MIN, SHORT_MAX, "Forward")
        walk_with_velocity_monitor(minescript.player_press_right, LONG_MIN, LONG_MAX, "Right")
        walk_with_velocity_monitor(minescript.player_press_forward, SHORT_MIN, SHORT_MAX, "Forward")

except Exception as e:
    play_alert_sound()
    minescript.echo(f"Script alert: {e}")
finally:
    # Safety cleanup: release all keys and attack
    minescript.player_press_attack(False)
    minescript.player_press_left(False)
    minescript.player_press_right(False)
    minescript.player_press_forward(False)
    minescript.echo("Safety cleanup complete. All keys released.")
