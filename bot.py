import json
from game.models import GameState
from game.enums import Action, SegmentType, TyreType

class Bot:
    def __init__(self):

        
        self.FUEL_ALLOWANCE = 219.0
        self.FUEL_TARGET_END = 3.0 # Finish with 3L = 98.6% usage
        self.FUEL_SAVE_TRIGGER = 0.88 
        self.CORNER_BUFFER = 1.6 
        self.decel = None
        self.fuel_per_lap = 3.65 
        self.last_total_fuel = 0
    
        self.corner_speeds = {} 
        
    def run(self, game_state: GameState):
        if self.decel is None:
            self.decel = game_state.config.constant_deceleration
            self._load_corner_speeds(game_state.track.segments)
        
        car = game_state.player
        segs = game_state.track.segments
        curr_seg = segs[car.position.segment_index]
        
        # Update fuel per lap average
        if game_state.total_fuel_used > self.last_total_fuel and game_state.lap > 1:
            lap_fuel = game_state.total_fuel_used - self.last_total_fuel
            self.fuel_per_lap = 0.8 * self.fuel_per_lap + 0.2 * lap_fuel # EMA
        self.last_total_fuel = game_state.total_fuel_used
        
        next_corner = self._find_next_corner(segs, car.position.segment_index, car.position.segment_progress)
        if next_corner:
            brake_dist = self._calc_brake_dist(car.speed, next_corner['speed'])
            if next_corner['dist'] <= brake_dist and car.speed > next_corner['speed'] + self.CORNER_BUFFER:
                return Action.DECELERATE
        
        # 2. PIT - Level 2 fuel logic
        if curr_seg.is_pit_entry and self._should_pit_fuel(car, game_state):
            return Action.PIT(tyre_type=TyreType.SOFT, refuel=True) # No wear in L2, softs = fastest
        
        # 3. ACCELERATE - With fuel saving
        if curr_seg.type == SegmentType.STRAIGHT:
            target_speed = curr_seg.target_speed
            
            # If burning too much fuel  lift 3.5%
            if self._is_over_fuel_pace(game_state):
                target_speed *= 0.965
                
            if car.speed < target_speed:
                return Action.ACCELERATE
        
        return Action.NOTHING

    def _load_corner_speeds(self, segments):
        for seg in segments:
            if seg.type == SegmentType.CORNER:
                self.corner_speeds[seg.id] = seg.corner_speed

    def _find_next_corner(self, segs, start_idx, progress):
        dist = segs[start_idx].length - progress
        for i in range(1, 6): 
            idx = (start_idx + i) % len(segs)
            if segs[idx].type == SegmentType.CORNER:
                return {'speed': segs[idx].corner_speed, 'dist': dist}
            dist += segs[idx].length
        return None

    def _calc_brake_dist(self, v_now, v_target):
        if v_now <= v_target: return 0
        return (v_now**2 - v_target**2) / (2 * self.decel)

    def _should_pit_fuel(self, car, gs):
        
        fuel_to_end = self.fuel_per_lap * gs.laps_remaining
        if gs.laps_remaining == 0:
            return car.fuel < fuel_to_end + 1.0
        
        if car.fuel < 25.0: return True
        return car.fuel < fuel_to_end + self.FUEL_TARGET_END

    def _is_over_fuel_pace(self, gs):
        if gs.lap == 0: return False
        fuel_pct_used = gs.total_fuel_used / self.FUEL_ALLOWANCE
        race_pct_done = gs.lap / (gs.lap + gs.laps_remaining)
        return fuel_pct_used > race_pct_done + 0.05 and fuel_pct_used > self.FUEL_SAVE_TRIGGER