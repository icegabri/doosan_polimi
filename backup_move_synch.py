def move_sync(self,cobot_target, height, vel_cobot):
        # Set the target pos height and velocity limit
        with self.lock:
            self.height = height * self.N_ROPE # Double rope manipulatore need to double the paramenter                          
            self.speed_limit = self.mm_to_rpm(vel_cobot)
            cobot_speed = self.rpm_to_mm(self.speed_limit)
            
        ######### Wait for the balancer to receive the same target pos and wait for it to start moving ######## REMOVED TO REDUCE INPUT LAG BEFORE START MOVING THE ROBOT
        #while True:
            #with self.lock:
                #if self.actual_vel != 0: and (self.target_pos == self.height)
                        #break        
                #time.sleep(self.T_WAIT)
        time.sleep(self.T_WAIT) # Wait little time to make the modbus registers update
        amovel(posx(0,0,cobot_target,0,0,0), v = cobot_speed, a = cobot_speed, mod = DR_MV_MOD_REL)
        time.sleep(self.T_WAIT_MOVE)
        with self.lock:
            vel_status = self.actual_vel
        if vel_status: #and (self.target_pos == self.height): # Check that the manipulator start moving and the target pos correspond to the one setted
            tp_log("Vel = {0} and t_pos = {1}".format(self.actual_vel, self.height))
        else:
            tp_log("Wrong Vel = {0} and t_pos = {1}".format(self.actual_vel, self.height))
            tp_log("Reset and close the program")
            self.reset_and_stop()
        # If the vel of the manipulator is 0 or is the vel is 0 or the there is an error stop the cobot
        while True:
            with self.lock:
                vel_status = self.actual_vel            
                resting = self.status_recv["bit_5_resting"]
                wrong_command = self.status_recv["bit_2_wrong_command"]
                error_from_manipulator = self.status_recv["bit_3_error_from_man"]
            if vel_status == 0: #  ((target - 2 ) <= self.actual_pos <= (target + 2)) or 
                stop(DR_SSTOP)
                tp_log("Stopped due to speed == 0")
                break
            elif resting:
                stop(DR_SSTOP)
                tp_log("Stopped due to resting")
                break
            elif wrong_command:
                stop(DR_SSTOP)
                tp_log("Stopped due to command error")
                self.reset_and_stop()
            elif error_from_manipulator:
                stop(DR_SSTOP)
                tp_log("Stopped due to manipulator error")
                self.reset_and_stop()
                
            time.sleep(self.T_WAIT)
        # Wait for the cobot to stop
        mwait(0)