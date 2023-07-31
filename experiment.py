# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P

from klibs.KLConstants import TK_MS
from klibs.KLAudio import Tone
from klibs.KLGraphics import KLDraw as kld
from klibs.KLGraphics import fill, blit, flip
from klibs.KLUserInterface import any_key, ui_request
from klibs.KLCommunication import message
from klibs.KLUtilities import deg_to_px, hide_mouse_cursor
from klibs.KLResponseCollectors import KeyPressResponse

from random import shuffle, expovariate

# RGB constants for easy reference
GRAY = [90, 90, 96, 255]
WHITE = [255, 255, 255, 255]



class handShieldingFlankerTask(klibs.Experiment):

	def setup(self):
		#
		# Stimulus Properties
		#

		# Stimulus location registration points
		# Defined in "units" relative to screen centre
		offset = deg_to_px(4) 
		self.locs = {
			"center":        P.screen_c,
			"message": 		[P.screen_c[0],     P.screen_c[1] - offset], # [X, Y]
			"left_flank":   [P.screen_c[0] - offset,     P.screen_c[1]], 
			"right_flank":  [P.screen_c[0] + offset,     P.screen_c[1]],
			"left_guide":   [P.screen_c[0] - offset / 2, P.screen_c[1]], # mid of target & flanker
			"right_guide":  [P.screen_c[0] + offset / 2, P.screen_c[1]],
		}

		# Stimulus sizings
		# Defined in common units
		stim_length = deg_to_px(1.0) 
		stim_girth = deg_to_px(0.2)

		fixation_length   = stim_length
		hand_guide_length = stim_length * 3.0
		# Arrows' composite parts
		arrow_tail_length = stim_length * 0.75
		arrow_head_length = stim_length * 0.25
		arrow_head_width  = stim_girth  * 3.0
		arrow_dimensions = [
			arrow_tail_length, stim_girth,		# length, width of tail
			arrow_head_length, arrow_head_width # length, width of head
		]

		# Stimulus objects
		self.fixation = kld.FixationCross(size=fixation_length, thickness=stim_girth, fill=WHITE)
		self.guide = kld.Line(length=hand_guide_length, thickness=stim_girth, color=GRAY)
		self.arrows = {
			'up':   kld.Arrow(*arrow_dimensions, rotation=270, fill=WHITE), # 0º = right-ward
			'down': kld.Arrow(*arrow_dimensions, rotation=90,  fill=WHITE)
		}

		# Error signal
		self.error_tone = Tone(duration=100, wave_type="sine", frequency=2000)

		# Block sequence
		base = ['left_guide', 'right_guide']
		shuffle(base)

		self.block_sequence = base * P.reps_per_condition

		if P.run_practice_blocks:
			pass


	def block(self):
		self.hand_guide_loc = self.block_sequence.pop()
		
		self.hand_placed = "left" if self.hand_guide_loc == "left_guide" else "right"

		msg = "Better instructions to come." + \
			"\nIn each trial of this task, three arrows will be presented in a line." + \
			"\nPlease indicated whether the MIDDLE arrow points up (up key), or down (down key)."+ \
			"\nDuring the block, you will place and hold your {} hand on the gray line, palm-in."+ \
			"\n\nPress any key to start."
		msg = msg.format(self.hand_placed.upper())
		
		fill()
		message(text=msg, location=self.locs["message"], registration=8)
		blit(self.fixation, 5, self.locs["center"])
		blit(self.guide, 5, self.locs[self.hand_guide_loc])
		flip()

		any_key()

		quit()

	def setup_response_collector(self):
		# Will potentially be replaced depending on whether button pad
		# is amicable or not
		self.rc.uses(KeyPressResponse)
		# Response mappings
		self.rc.keypress_listener.key_map = {'Up': 'up', 'Down': 'down'}
		# Response window
		self.rc.terminate_after = [1000, TK_MS]
		# Abort trial upon response
		self.rc.keypress_listener.interrupts = True



	def trial_prep(self):
		self.fix_targ_soa = self.get_fix_target_asyncrony()
		self.evm.register_ticket(["array_on", self.fix_targ_soa])
		self.present_stimuli()
		hide_mouse_cursor()

	def trial(self):

		while self.evm.before("array_on"):
			ui_request()

		self.present_stimuli(target_phase=True)
		
		self.rc.collect()

		response = self.rc.keypress_listener.response()
		error_made = "NA"

		if response[0] != "NO_RESPONSE":
			error_made = int(response[0] != self.target_type)

		return {
			"block_num": P.block_number,
			"trial_num": P.trial_number,
			"hand_placed": self.hand_placed,
			"fix_target_asynchrony": self.fix_targ_soa,
			"target_type": self.target_type,
			"left_flanker_type": self.left_flanker,
			"right_flanker_type": self.right_flanker,
			"response_time": response[1],
			"response_made": response[0],
			"response_error": error_made
		}

	def trial_clean_up(self):
		pass

	def clean_up(self):
		pass


	def present_stimuli(self, target_phase = False):
		fill() # Paint background

		blit(self.guide, 5, self.locs[self.hand_guide_loc]) # Add hand guide
		
		if target_phase: # add target & flankers, when appropriate
			blit(self.arrows[self.left_flanker],  5, self.locs["left_flanker"])
			blit(self.arrows[self.target_type],   5, self.locs["center"])
			blit(self.arrows[self.right_flanker], 5, self.locs["right_flanker"])
		else: # otherwise, only add fixation cross
			blit(self.fixation, 5, self.locs["center"])

		flip() # make visible

	# Get fix-target asynchrony, sampled from non-decaying time function
	def get_fix_target_asyncrony(self):

		# dummy val to start loop
		interval = P.fixation_max + 1

		# until val below max is generated
		while interval > P.fixation_max:
			# sample value from exponential distribution, ensuring never below min val
			# don't ask why this works, but run it a few times and you'll see it does
			interval = expovariate(1.0 / float(P.fixation_mean - P.fixation_min) + P.fixation_min)

		return interval

