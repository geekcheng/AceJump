import sublime, sublime_plugin

begin_char = 'a'
letters = [chr(x+ord(begin_char)) for x in range(26)]
regexp = r"{}[\d\w]*"

is_mark = False
words = []

## hash the number to string
def number_to_string(num):
	length = len(letters)
	str = ""
	if num == 0:
		return begin_char
	while num:
		str += letters[int(num%length)]
		num //= length
	return str[::-1]
	

def string_to_num(str):
	num = 0
	lenght = len(letters)
	for s in str:
		num = num * lenght + (ord(s) - ord(begin_char))
	return num

class MyJumpCommand(sublime_plugin.WindowCommand):

	def run(self):
		self.view = self.window.active_view()
		self.back()
		## wheter has modify the view
		self.str = ""

		## the labels shows that where the characters we are looking for may be in
		self.labels = False
		self.window.show_input_panel(
			"AceJump", "",self.init,self.change,self.cancel
			)

	def change(self, command):
		if not command:
			self.back()
		elif len(command) == 1:
			self.str = command
			self.view.run_command("ace_mark" , {"char" : command})
		else:
			self.jump(command)
		return

	def init(self, command):
		self.cancel()
		if len(command) > 1 :
			self.jump(command)

	def cancel(self):
		if is_mark:
			#self.unlabel_words()
			self.view.run_command("ace_mark", {"char": ""})
		self.view.erase_status("AceJump")
		# if caller != input:
		sublime.status_message("AceJump: Cancelled")

	def jump(self, command):
		index = string_to_num(command[1:])
		if index :
			global words
			region = words[index]
			self.view.run_command("ace_jump_to_place" , {"index" : region.begin()})
			self.back()
		return

	def back(self):
		self.str = ""
		self.view.run_command("ace_mark" , {"char" : ""})



class AceMarkCommand(sublime_plugin.TextCommand):
	def run(self,edit,char):
		if len(char) > 0 :
			self.mark(edit,char)
		else:
			self.unmark(edit)

	def mark(self,edit,char):
		char = char.lower()
		global is_mark
		if is_mark:
			self.unmark(edit)
		global words # :\
		# Find words in this region
		mark_regions = []
		visible_region = self.view.visible_region()
		num = 0
		words = []
		visible_region = self.view.visible_region()
		pos = visible_region.begin()
		last_pos = visible_region.end()
		while pos < last_pos :
			word = self.view.find(regexp.format(char), pos )
			if word:
				words.append(word)
				tmp_mark_wds = number_to_string(num)
				tmp_mark_wds_len = len(tmp_mark_wds)
				##conside charaction \n
				replace_region = sublime.Region(word.begin(), word.begin() + tmp_mark_wds_len)
				self.view.replace(edit, replace_region, tmp_mark_wds)
				mark_regions.append(replace_region)
				num = num + 1
			else:
				break
			pos = word.end()

		matches = len(words)
		if not matches:
			self.view.set_status("AceJump", "No matches found")
			return
		is_mark = True
		# Which scope to use here, string?
		# comment, string
		self.view.add_regions("AceJumpMarks", mark_regions, "comment")
		self.view.set_status(
			"AceJump", "Found {} match{} for character {}".format(matches, "es" if matches > 1 else "", char)
		)

	def unmark(self,edit):
		global is_mark
		if is_mark:
			self.view.erase_regions("AceJumpMarks")
			self.view.erase_regions("mark_line")
			self.view.end_edit(edit)
			self.view.run_command("undo")
			is_mark = False


class AceJumpToPlaceCommand(sublime_plugin.TextCommand):

	def run(self, edit, index):
		## add marks 
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(index))
		self.view.show(index)
		self.view.add_regions("mark_line", [sublime.Region(index,index)], "mark", "dot", sublime.DRAW_STIPPLED_UNDERLINE)
