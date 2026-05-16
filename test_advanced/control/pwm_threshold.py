class pwm_threshold():
    def __init__(self, max_pwm=1900, min_pwm=1100):
        self.max_pwm = max_pwm
        self.min_pwm = min_pwm
    
    def check_pwm(self, pwm):
        return max(self.min_pwm, min(self.max_pwm, pwm))