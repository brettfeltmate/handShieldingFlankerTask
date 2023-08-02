# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P

from klibs.KLConstants import TK_MS
from klibs.KLAudio import Tone
from klibs.KLGraphics.KLDraw import FixationCross, Arrow, Line
from klibs.KLGraphics import fill, blit, flip
from klibs.KLUserInterface import any_key, ui_request
from klibs.KLCommunication import message
from klibs.KLUtilities import deg_to_px, hide_mouse_cursor, now
from klibs.KLResponseCollectors import KeyPressResponse

from random import shuffle, expovariate

# RGB constants for easy reference
GRAY = [90, 90, 96, 85]
WHITE = [255, 255, 255, 255]



class handShieldingFlankerTask(klibs.Experiment):

	def setup(self):
		#
		# Stimulus Properties
		#

		# Stimulus location registration points
		# Defined in "units" relative to screen centre
		offset = deg_to_px(8) 
		self.locs = {
			"center":         P.screen_c,
			"message": 	     [P.screen_c[0],     P.screen_c[1] - offset], # [X, Y]
			"left_flanker":  [P.screen_c[0] - offset,     P.screen_c[1]], 
			"right_flanker": [P.screen_c[0] + offset,     P.screen_c[1]],
			"left_guide":    [P.screen_c[0] - offset / 2, P.screen_c[1]], # mid of target & flanker
			"right_guide":   [P.screen_c[0] + offset / 2, P.screen_c[1]],
		}

		# Stimulus sizings
		# Defined in common units
		base_len = deg_to_px(1.0) 
		base_thick = deg_to_px(0.2)

		fix_len = base_len
		hand_guide_len = base_len * 3.0
		hand_guide_thick = base_thick / 2.0
		# Arrows' composite parts
		arrow_tail_len = base_len * 0.75
		arrow_head_len = base_len * 0.50
		arrow_head_wid = base_thick  * 5.0
		arrow_dims = [
			arrow_tail_len, base_thick,		# length, width of tail
			arrow_head_len, arrow_head_wid # length, width of head
		]

		# Stimulus objects
		self.fixation = FixationCross(size=fix_len, thickness=base_thick, fill=WHITE)
		self.guide = Line(length=hand_guide_len, thickness=hand_guide_thick, color=GRAY)
		self.arrows = {
			'up':   Arrow(*arrow_dims, rotation=270, fill=WHITE), # 0º = right-ward
			'down': Arrow(*arrow_dims, rotation=90,  fill=WHITE)
		}

		# Error signal
		self.error_tone = Tone(duration=100, wave_type="sine", frequency=2000)

		# Block sequence
		base = ['left_guide', 'right_guide']
		shuffle(base) # randomize which hand starts

		self.block_sequence = base * P.reps_per_condition 

		if P.run_practice_blocks:
			pass


	def block(self):
		self.hand_guide_loc = self.block_sequence.pop()

		msg = "Better instructions to come." + \
			"\nIn each trial of this task, three arrows will be presented in a line." + \
			"\nPlease indicated whether the middle arrow points up (up key), or down (down key)."+ \
			"\nDuring the block, you will place and hold your {} hand on the gray line, palm-in."+ \
			"\n\nPress any key to start."
		msg = msg.format("left" if self.hand_guide_loc == "left_guide" else "right")
		
		fill()
		message(text=msg, location=self.locs["message"], registration=8)
		blit(self.fixation, 5, self.locs["center"])
		blit(self.guide, 5, self.locs[self.hand_guide_loc])
		flip()

		any_key()


	def setup_response_collector(self):
		# Will potentially be replaced depending on whether button pad
		# is amicable or not
		self.rc.uses(KeyPressResponse)
		# Response mappings
		# This experiment used a Millikey SV-2 r1, wherein the up & down buttons
		# are mapped to '1' and '2', respectively.
		self.rc.keypress_listener.key_map = {'1': 'up', '2': 'down'}
		# Response window
		self.rc.terminate_after = [2000, TK_MS]
		# Abort trial upon response
		self.rc.keypress_listener.interrupts = True


	def trial_prep(self):
		# Establish & register time until target array onset
		self.fix_targ_soa = self.get_fix_target_asyncrony()
		self.evm.register_ticket(["target_onset", self.fix_targ_soa])

		# Present base display
		self.present_stimuli(phase = 'fixation')

	def trial(self):
		# Do nothing until array onset
		while self.evm.before("target_onset"):
			ui_request()

		# Present array and listen for response
		self.present_stimuli(phase = 'target')
		self.rc.collect()

		# Grab response (if made)
		response = self.rc.keypress_listener.response()
		error_made = "NO_RESPONSE"
		
		# Determine if error was made
		if response.value != "NO_RESPONSE":
			error_made = int(response.value != self.target_type)

		# Admonish participant if so
		if error_made != 0:
			self.error_tone.play()

		# clear display and pause until next trial
		self.present_stimuli()

		ITI = now() + (P.inter_trial_interval / 1000.0)

		while now() < ITI:
			ui_request()

		return {
			"block_num": P.block_number,
			"trial_num": P.trial_number,
			"hand_placed": "left" if self.hand_guide_loc == "left_guide" else "right",
			"fix_target_asynchrony": self.fix_targ_soa,
			"target_type": self.target_type,
			"left_flanker_type": self.left_flanker,
			"right_flanker_type": self.right_flanker,
			"response_time": response.rt,
			"response_made": response.value,
			"response_error": error_made
		}

	def trial_clean_up(self):
		self.rc.keypress_listener.reset()


	def clean_up(self):
		pass


	def present_stimuli(self, phase):

		hide_mouse_cursor()
		fill() # Paint background

		blit(self.guide, 5, self.locs[self.hand_guide_loc]) # Add hand guide

		if phase == 'fixation':
			blit(self.fixation, 5, self.locs["center"])

		if phase == 'target':
			blit(self.arrows[self.left_flanker],  5, self.locs["left_flanker"])
			blit(self.arrows[self.target_type],   5, self.locs["center"])
			blit(self.arrows[self.right_flanker], 5, self.locs["right_flanker"])

		flip() # make visible

	# Get fix-target asynchrony, sampled from non-decaying time function
	def get_fix_target_asyncrony(self):

		# dummy val to start loop
		interval = P.fixation_max + 1

		# until val below max is generated
		while interval > P.fixation_max:
			# sample value from exponential distribution, ensuring never below min val
			# don't ask why this works, but run it a few times and you'll see it does
			interval = expovariate(1.0 / float(P.fixation_mean - P.fixation_min)) + P.fixation_min

		return interval

