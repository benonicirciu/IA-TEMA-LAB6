import time
import random
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

# --- Configurare Parametri ---
V_FORWARD     = 2.0    # rad/s
V_BACKWARD    = -1.5   # rad/s
V_ROTATE      = 2.0    # rad/s
STOP_DISTANCE = 0.6    # m (pragul de detecție)
T_BACKWARD    = 1.0    # secunde (cât timp dă înapoi)
T_ROTATE      = 1.5    # secunde (aprox. 90 grade)

FRONT_SENSORS = [2, 3, 4, 5]
SENSOR_MAX    = 1.0

class RobotState:
    FORWARD  = "FORWARD"
    BACKWARD = "BACKWARD"
    TURNING  = "TURNING"

def get_min_front_distance(sim, sensors):
    min_dist = SENSOR_MAX
    for idx in FRONT_SENSORS:
        result, distance, *_ = sim.readProximitySensor(sensors[idx])
        if result and distance < min_dist:
            min_dist = distance
    return min_dist

def main():
    client = RemoteAPIClient()
    sim = client.require('sim')

    left_motor  = sim.getObject('/PioneerP3DX/leftMotor')
    right_motor = sim.getObject('/PioneerP3DX/rightMotor')
    sensors     = [sim.getObject(f'/PioneerP3DX/ultrasonicSensor[{i}]') for i in range(16)]

    sim.startSimulation()
    
    # Inițializare stare
    current_state = RobotState.FORWARD
    state_start_time = time.time()
    direction_modifier = 1 # 1 pentru dreapta, -1 pentru stânga

    print(f"Robot Explorer pornit. Stare inițială: {current_state}")

    try:
        while True:
            dist_front = get_min_front_distance(sim, sensors)
            now = time.time()
            elapsed = now - state_start_time

            # --- Logica Mașinii de Stări ---
            
            if current_state == RobotState.FORWARD:
                # Acțiune
                sim.setJointTargetVelocity(left_motor, V_FORWARD)
                sim.setJointTargetVelocity(right_motor, V_FORWARD)
                
                # Tranziție: dacă detectăm obstacol
                if dist_front < STOP_DISTANCE:
                    print(f"![{current_state}] Obstacol la {dist_front:.2f}m. Trec la BACKWARD.")
                    current_state = RobotState.BACKWARD
                    state_start_time = now

            elif current_state == RobotState.BACKWARD:
                # Acțiune
                sim.setJointTargetVelocity(left_motor, V_BACKWARD)
                sim.setJointTargetVelocity(right_motor, V_BACKWARD)
                
                # Tranziție: după ce a trecut timpul de dat înapoi
                if elapsed > T_BACKWARD:
                    direction_modifier = random.choice([1, -1]) # Alege stânga sau dreapta aleator
                    print(f"![{current_state}] Timp expirat. Trec la TURNING.")
                    current_state = RobotState.TURNING
                    state_start_time = now

            elif current_state == RobotState.TURNING:
                # Acțiune: rotire pe loc
                sim.setJointTargetVelocity(left_motor, V_ROTATE * direction_modifier)
                sim.setJointTargetVelocity(right_motor, -V_ROTATE * direction_modifier)
                
                # Tranziție: după ce a terminat rotația
                if elapsed > T_ROTATE:
                    print(f"![{current_state}] Rotație completă. Trec la FORWARD.")
                    current_state = RobotState.FORWARD
                    state_start_time = now

            # Afișare stare (opțional, pentru debug)
            # print(f"Stare: {current_state} | Timp în stare: {elapsed:.1f}s", end='\r')
            
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nOprire manuală.")
    finally:
        sim.setJointTargetVelocity(left_motor, 0)
        sim.setJointTargetVelocity(right_motor, 0)
        sim.stopSimulation()

if __name__ == '__main__':
    main()