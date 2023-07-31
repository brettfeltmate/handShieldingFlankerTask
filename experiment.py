# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P

from klibs.KLConstants import TK_MS
from klibs.KLAudio import Tone
from klibs.KLGraphics import KLDraw as kld
from klibs.KLGraphics import fill, blit, flip
from klibs.KLUserInterface import any_key
from klibs.KLCommunication import message
from klibs.KLUtilities import deg_to_px, hide_mouse_cursor
from klibs.KLResponseCollectors import KeyPressResponse

from random import shuffle

# RGB constants for easy reference
GRAY = [90, 90, 96, 255]



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
		self.fixation = kld.FixationCross(size=fixation_length, thickness=stim_girth)
		self.hand_guide = kld.Line(length=hand_guide_length, thickness=stim_girth, color=GRAY)
		self.arrow_up = kld.Arrow(*arrow_dimensions, rotation=270)
		self.arrow_down = kld.Arrow(*arrow_dimensions, rotation=90)
		self.arrow_up.render()
		self.arrow_down.render()

		# Error signal
		self.error_tone = Tone(duration=100, wave_type="sine", frequency=2000)

		# Block sequence
		base = ['left_guide', 'right_guide']
		shuffle(base)

		self.block_sequence = base * P.reps_per_condition

		if P.run_practice_blocks:
			pass


	def block(self):
		self.block
		hand_placed = "left"

		hand = "left"

		msg = "Better instructions to come. + \
			\nIn each trial of this task, three arrows will be presented in a line. \
			\nPlease indicated whether the MIDDLE arrow points up (up key), or down (down key). \
			\nDuring the block, you will place and hold your hand on the gray line, palm-in. \
			\n\nPress any key to start."
		
		fill()
		message(text=msg, location=self.locs["message"], registration=8)
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
		pass

	def trial(self):

		return {
			"block_num": P.block_number,
			"trial_num": P.trial_number
		}

	def trial_clean_up(self):
		pass

	def clean_up(self):
		pass


