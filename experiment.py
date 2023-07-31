# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P

from klibs.KLAudio import Tone
from klibs.KLGraphics import KLDraw as kld
from klibs.KLGraphics import fill, blit, flip
from klibs.KLUserInterface import any_key
from klibs.KLCommunication import message
from klibs.KLUtilities import deg_to_px, hide_mouse_cursor

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
		self.stim_locs = {
			"center": P.screen_c,
			"left_flank":  [P.screen_c[0] - offset,     P.screen_c[1]], # [X, Y]
			"right_flank": [P.screen_c[0] + offset,     P.screen_c[1]],
			"left_guide":  [P.screen_c[0] - offset / 2, P.screen_c[1]], # mid of target & flanker
			"right_guide": [P.screen_c[0] + offset / 2, P.screen_c[1]],
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

		self.error_tone = Tone(duration=100, wave_type="sine", frequency=2000)

		if P.run_practice_blocks:
			pass


	def block(self):
		pass

	def setup_response_collector(self):
		pass

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
