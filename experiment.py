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
			'up':   Arrow(*arrow_dims, rotation=270, fill=WHITE), # 0º = right-facing
			'down': Arrow(*arrow_dims, rotation=90,  fill=WHITE)
		}

		# Error signal
		self.error_tone = Tone(duration=100, wave_type="sine", frequency=2000)

		# Block sequence
		hand_guide = ['none', 'left_guide', 'right_guide']
		self.block_sequence = hand_guide * P.reps_per_condition # extend to desired number of blocks

		if P.run_practice_blocks:
			self.block_sequence.append(hand_guide) # add additional round of blocks
			self.insert_practice_block(block_nums=[1,2,3], trial_counts=P.trials_per_practice_block)


	def block(self):
		# After practice phase completes, begin randomizing block conditions
		# Or, in other words, ensure practice phase contains one block for each cond.
		if not P.practicing:
			shuffle(self.block_sequence)

		self.guide_for_block = self.block_sequence.pop() # Get guide location for current block
		self.hand_used = self.guide_for_block.split('_')[0] # Pop out laterality for tidy messaging

		# Rough draft of instructions
		msg = "Better instructions to come." + \
			"\nIn each trial of this task, three arrows will be presented in a line." + \
			"\nUsing the provided keypad, indicate whether the central arrows points upward (red button), or downward (black button)." + \
			"\nPlease try to be both fast, and accurate, when responding."
		
		# Tack on hand instructions when necessary.
		if self.hand_used != "None":
			msg += "\n\nDuring this block, please place and keep your {} hand on the gray line, with your palm facing inwards."
			msg = msg.format(self.hand_used)

		msg += "\n\nWhen you are ready to to begin, press any key to start the block."
		if P.practicing:
			if P.block_number < 3:
				msg += "\n(this is a practice block)"
			else:
				msg += "\n(this is the final practice block)"
		
		# Present fixation and wait for block initiation
		self.draw_display(msg=msg)
		any_key()


	def setup_response_collector(self):
		self.rc.uses(KeyPressResponse) # This feel self-explanatory
		
		# This experiment used a Millikey SV-2 r1, wherein the up & down buttons
		# are mapped to '1' and '2', respectively. 
		self.rc.keypress_listener.key_map = {'1': 'up', '2': 'down'}
		# Self-terminate if no response made by 2s
		self.rc.terminate_after = [2000, TK_MS]
		# Abort trial upon response
		self.rc.keypress_listener.interrupts = True


	def trial_prep(self):
		# Establish & register time until target array onset
		self.fix_targ_soa = self.get_fix_target_asyncrony()
		self.evm.register_ticket(["target_onset", self.fix_targ_soa])

		# Present base display
		self.draw_display(phase = 'fixation')

	def trial(self):
		# Do nothing until array onset
		while self.evm.before("target_onset"):
			ui_request()

		# Present array and listen for response
		self.draw_display(phase = 'target')
		self.rc.collect()

		# Grab response (or lack thereof)
		response = self.rc.keypress_listener.response()

		# Admonish participant for incorrect or absent responses
		if response.value != self.target_type:
			self.error_tone.play()

		# clear display and pause until next trial
		self.draw_display()

		return {
			"block_num": P.block_number,
			"trial_num": P.trial_number,
			"hand_placed": self.hand_used,
			"fix_target_asynchrony": self.fix_targ_soa,
			"target_type": self.target_type,
			"left_flanker_type": self.left_flanker,
			"right_flanker_type": self.right_flanker,
			"response_time": response.rt,
			"response_made": response.value
		}

	def trial_clean_up(self):
		# Very likely superfluous 
		self.rc.keypress_listener.reset()
		
		# Enforce 1s delay between trials
		ITI = now() + (P.inter_trial_interval / 1000.0)
		while now() < ITI:
			ui_request()


	def clean_up(self):
		pass

	# Draws the necessary stimuli for the current trial/task phase
	def draw_display(self, phase, msg = None):

		hide_mouse_cursor()
		fill() # Paint background

		# Draw hand guide when appropriate
		if self.guide_for_block != 'none':
			blit(self.guide, 5, self.locs[self.guide_for_block])

		if phase == 'fixation':
			blit(self.fixation, 5, self.locs["center"])

		# Present the appropriate arrow types (up/down) for each location
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
	
	def give_instructions(self, hand_used):
		msg = ""
		if P.block_number == 1:
			msg += ""

