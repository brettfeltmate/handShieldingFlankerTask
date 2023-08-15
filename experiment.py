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
from klibs.KLUtilities import deg_to_px, hide_mouse_cursor
from klibs.KLResponseCollectors import KeyPressResponse
from klibs.KLKeyMap import KeyMap

from random import shuffle, expovariate
import sdl2

# RGB constants for easy reference
GRAY = [90, 90, 96, 85]
WHITE = [255, 255, 255, 255]



class handShieldingFlankerTask(klibs.Experiment):

	def setup(self):

		"""
		Stimulus sizings estimated from Davoli & Brockmole's 2012 APP paper.
		In E1's methods, display was 43cm along the diagonal.
		Assuming a 5:4 aspect ratio and 1280x1024 resolution, display was 33.6 x 21.9cm
		Target was described as being 1.3 x 2.2cm in size, and flankers 3 x 6cm, 
		and offset 7.7cm centre-to-centre. Stimuli were viewed from a distance of 40cm.

		Using these values, targets are estimated to have been 1.86 x 3.3º visual angle,
		flankers 4.3 * 8.6º, and the offset as 11º.
		Here we don't have the option of specifying text width (only height), well, at least
		not without significant effort. So only height will be specified as width will be in the ballpark
		"""
		# Stimulus sizings
		target_height = deg_to_px(2.2)
		flanker_height = deg_to_px(8.6)
		offset = deg_to_px(11)

		# Add text styles for rendering stimuli
		self.txtm.add_style("target", font_size = target_height)
		self.txtm.add_style("flanker", font_size = flanker_height)

		# Reference coordinates for positioning
		self.locs = {
			"left_flank":  [P.screen_c[0] - offset,   P.screen_c[1]], #[x, y]
			"left_guide":  [P.screen_c[0] - offset/2, P.screen_c[1]], # mid of flank & centre
			"center":       P.screen_c,
			"right_flank": [P.screen_c[0] + offset,   P.screen_c[1]],
			"right_guide": [P.screen_c[0] + offset/2, P.screen_c[1]],
			"instrux":     [P.screen_c[0],            P.screen_c[1] - offset/2] # up from center
		}

		# Guide line
		self.guide = Line(length=target_height, thickness=deg_to_px(0.5), color=GRAY)

		# Relevant property of blocks are if & which hand should be placed on-screen
		self.practice_block_sequence = ['left_guide', 'right_guide']
		shuffle(self.practice_block_sequence)

		self.test_block_sequence = ['left_guide', 'right_guide', 'none']
		shuffle(self.test_block_sequence)
		self.test_block_sequence = self.test_block_sequence * P.reps_per_condition


		# This feels hacky, but for blocks sans hand guide, I need to ensure the responding hand
		# is varied
		self.key_hand_no_guide = ['left', 'right']
		shuffle(self.key_hand_no_guide)

		# Establish key mappings
		self.targs = ["S", "H"]
		shuffle(self.targs)
		# colour tabels are for user instructions, sdl2 codes correspond to actual keys; mapping of 
		# each to a particular target is randomized

		self.key_map = KeyMap("response", ['red', 'black'], self.targs, [sdl2.SDLK_1, sdl2.SDLK_2])

		if P.run_practice_blocks:
			self.insert_practice_block(block_nums=[1,2], trial_counts=P.trials_per_practice_block)


	def block(self):

		# Get guide location for block
		if P.practicing:
			self.guide_for_block = self.practice_block_sequence.pop()
		else:
			self.guide_for_block = self.test_block_sequence.pop()


		# Generate & present block instructions
		instrux = self.get_instructions()
		self.draw_display(msg = instrux)

		any_key()


	def setup_response_collector(self):
		self.rc.uses(KeyPressResponse) # This feel self-explanatory
		
		# This experiment used a Millikey SV-2 r1, wherein the up & down buttons
		# are mapped to '1' and '2', respectively. 
		self.rc.keypress_listener.key_map = self.key_map
		# Abort trial upon response
		self.rc.keypress_listener.interrupts = True


	def trial_prep(self):
		# determine flanker identities fro trial
		self.left_flank_letter, self.right_flank_letter = self.get_flankers()

		# Register time until target array onset
		self.evm.register_ticket(["target_onset", 1000])

		# Present base display
		self.draw_display()

	def trial(self):
		# Do nothing until array onset
		while self.evm.before("target_onset"):
			ui_request()

		# Present array and listen for response
		self.draw_display(show_array=True)
		self.rc.collect()

		# Grab response (or lack thereof)
		response = self.rc.keypress_listener.response()

		# clear display and pause until next trial
		self.draw_display()

		return {
			"block_num": P.block_number,
			"trial_num": P.trial_number,
			"hand_placed": self.guide_for_block.split('_')[0],
			"target_letter": self.target_letter,
			"left_flanker_type": self.left_flanker,
			"right_flanker_type": self.right_flanker,
			"response_time": response.rt,
			"response_made": response.value
		}

	def trial_clean_up(self):
		# Very likely superfluous 
		self.rc.keypress_listener.reset()


	def clean_up(self):
		pass

	# Draws the necessary stimuli for the current trial/task phase
	def draw_display(self, show_array=False, msg = None):

		hide_mouse_cursor()
		fill() # Paint background

		# Used to present instructions at block start
		if msg is not None:
			message(msg, location=self.locs['instrux'], registration=8)

		# Draw hand guide when appropriate
		if self.guide_for_block != 'none':
			blit(self.guide, 5, self.locs[self.guide_for_block])

		# Present the appropriate arrow types (up/down) for each location
		if show_array:
			message(
				self.left_flank_letter, style="flanker", 
				location=self.locs["left_flank"], registration=5
			)
			message(
				self.target_letter, style="target",
				location=self.locs['center'], registration=5
			)
			message(
				self.right_flank_letter, style="flanker", 
				location=self.locs["right_flank"], registration=5
			)

		flip() # make visible

	
	def get_instructions(self):
		msg = ""
		if P.block_number == 1:
			add  = "On each trial in this task, you will be shown three letters in a row."
			add += "\nWhen this happens, please indicate whether the center letter is a "
			add += "{0}, using the red button, or a {1}, using the black button."
			add += "\nPlease try to be as fast, and as accurate, as possible when responding."
			add = add.format(*self.targs)
			msg += add

		if self.guide_for_block != 'none':
			guide_hand = self.guide_for_block.split('_')[0]
			key_hand = 'left' if guide_hand == 'right' else 'right'

			add = "\n\nThroughout this block, please place and hold your {0} hand on the gray line"
			add += "\nand use the index and middle fingers of your {1} hand to respond."
			add = add.format(guide_hand, key_hand)

		else:
			key_hand = self.key_hand_no_guide.pop()

			add = "\nThroughout this block, use the index and middle fingers of your {} hand"
			add += " to respond.\nNeither hand needs to be placed on the screen for this block."
			add = add.format(key_hand)


		msg += add + "\n\nPress any key to begin the block."

		if P.practicing:
			if P.block_number == 1:
				msg += "\n(this is a practice block)"
			else:
				msg += "\n(this is the final practice block)"

		return msg



	def get_flankers(self):
		left, right = "", ""

		if self.left_flanker == "neutral":
			left = 'X'
		elif self.left_flanker == 'congruent':
			left = self.target_letter
		elif self.left_flanker == 'incongruent': 
			left = 'H' if self.target_letter == 'S' else 'S'

		if self.right_flanker == "neutral":
			right = 'X'
		elif self.right_flanker == 'congruent':
			right = self.target_letter
		elif self.right_flanker == 'incongruent': 
			right = 'H' if self.target_letter == 'S' else 'S'

		return [left, right]
