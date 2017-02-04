#!/usr/bin/env/python
import wx
from collections import deque

class SnakeGame(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(300,350), style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX))
		
		# Initialize status bar
		self.statusBar = self.CreateStatusBar()
		self.statusBar.SetStatusText('Score: ' + '0')
		self.board = Board(self)
		box = wx.BoxSizer(wx.HORIZONTAL)
		box.Add(self.board, 1, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER, 0)
		self.SetSizer(box)
		self.board.SetFocus()
		self.board.Start()
		self.Center()
		self.Show(True)
	
	def OnAbout(self,e):
		dlg = wx.MessageDialog( self, 'Created by Simon So, 2010', 'About Snake', wx.OK)
		dlg.ShowModal()
		dlg.Destroy()
		
	def OnExit(self,e):
		self.Close(True)

class SnakeBody(object):
	def __init__(self):
		self.Width = 5
		self.Length = 50
		self.HeadDir = SnakeDir.RIGHT
		self.TailDir = SnakeDir.RIGHT
		self.Body = [[wx.Point(50,100),wx.Point(0, 100)]]
		self.NumSegments = 1
				
	def SaveTurnPos(self):
		self.Body[0].insert(1,wx.Point(self.Body[0][0].x,self.Body[0][0].y))
	
	def Move(self):
		self.CalcTailDir()
		headDir = self.HeadDir
		tailDir = self.TailDir
		
		if headDir == SnakeDir.RIGHT:
			self.MoveHeadRight()
		elif headDir == SnakeDir.LEFT:
			self.MoveHeadLeft()
		elif headDir == SnakeDir.UP:
			self.MoveHeadUp()
		else: # headDir == SnakeDir.DOWN:
			self.MoveHeadDown()
		
		if tailDir == SnakeDir.RIGHT:
			self.MoveTailRight()
		elif tailDir == SnakeDir.LEFT:
			self.MoveTailLeft()
		elif tailDir == SnakeDir.UP:
			self.MoveTailUp()
		else: # headDir == SnakeDir.DOWN:
			self.MoveTailDown()

	def MoveHeadUp(self):
		if self.Body[0][0].y == 0:
			self.Body.insert(0,[wx.Point(self.Body[0][0].x,Board.Height),wx.Point(self.Body[0][0].x,Board.Height)])
			self.NumSegments += 1
		else:
			self.Body[0][0].y -= 1	
	
	def MoveHeadDown(self):
		if self.Body[0][0].y == Board.Height:
			self.Body.insert(0,[wx.Point(self.Body[0][0].x,0),wx.Point(self.Body[0][0].x,0)])
			self.NumSegments += 1
		else:
			self.Body[0][0].y += 1
	
	def MoveHeadLeft(self):
		if self.Body[0][0].x == 0:
			self.Body.insert(0,[wx.Point(Board.Width,self.Body[0][0].y),wx.Point(Board.Width,self.Body[0][0].y)])
			self.NumSegments += 1
		else:
			self.Body[0][0].x -= 1
	
	def MoveHeadRight(self):
		if self.Body[0][0].x == Board.Width:
			self.Body.insert(0,[wx.Point(0,self.Body[0][0].y),wx.Point(0,self.Body[0][0].y)])
			self.NumSegments += 1
		else:
			self.Body[0][0].x += 1
	
	def MoveTailUp(self):
		if self.Body[-1][0] == self.Body[-1][-1]:
			del self.Body[-1]
			self.NumSegments -= 1
		else:
			self.Body[-1][-1].y -= 1
	
	def MoveTailDown(self):
		if self.Body[-1][0] == self.Body[-1][-1]:
			del self.Body[-1]
			self.NumSegments -= 1
		else:
			self.Body[-1][-1].y += 1
	
	def MoveTailLeft(self):
		if self.Body[-1][0] == self.Body[-1][-1]:
			del self.Body[-1]
			self.NumSegments -= 1
		else:
			self.Body[-1][-1].x -= 1
	
	def MoveTailRight(self):
		if self.Body[-1][0] == self.Body[-1][-1]:
			del self.Body[-1]
			self.NumSegments -= 1
		else:
			self.Body[-1][-1].x += 1
	
	def CalcTailDir(self):
		diff = self.Body[-1][-2] - self.Body[-1][-1]
		if diff.x > 0:
			self.TailDir = SnakeDir.RIGHT
		elif diff.x < 0:
			self.TailDir = SnakeDir.LEFT
		elif diff.y > 0:
			self.TailDir = SnakeDir.DOWN
		elif diff.y < 0:
			self.TailDir = SnakeDir.UP
		elif diff.x == 0 and diff.y == 0:
			if len(self.Body[-1]) > 2:
				nextDiff = self.Body[-1][-3] - self.Body[-1][-1]
				if nextDiff.x > 0:
					self.TailDir = SnakeDir.RIGHT
				elif nextDiff.x < 0:
					self.TailDir = SnakeDir.LEFT
				elif nextDiff.y > 0:
					self.TailDir = SnakeDir.DOWN
				elif nextDiff.y < 0:
					self.TailDir = SnakeDir.UP
				del self.Body[-1][-2]
			else:
				del self.Body[-1]
	
	def SetPos(self, point):
		self.Body[0][0] = point
	
	def SetWidth(self, width):
		self.Width = width
	
	def SetLength(self, length):
		self.Length = length
	
	def SetHeadDir(self, dir):
		self.HeadDir = dir
	
	def GetBody(self):
		return self.Body
	
	def GetPos(self):
		return self.Body[0][0]
	
	def GetWidth(self):
		return self.Width
	
	def GetLength(self):
		return self.Length
		
	def GetHeadDir(self):
		return self.HeadDir
		
		
class SnakeDir(object):
	UP = 0
	DOWN = 1
	LEFT = 2
	RIGHT = 3

class Board(wx.Panel):
	Width = 300
	Height = 300
	Speed = 10
	ID_TIMER = 1
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.isPaused = False
		self.Score = 0
		self.Snake = SnakeBody()
		self.timer = wx.Timer(self, Board.ID_TIMER)
		self.Bind(wx.EVT_TIMER, self.OnTimer, id=Board.ID_TIMER)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBkgd)
	
	def Start(self):
		self.timer.Start(Board.Speed, wx.TIMER_CONTINUOUS)
	
	def Pause(self):
		self.isPaused = not self.isPaused
		
		if self.isPaused:
			self.timer.Stop()
			self.GetParent().statusBar.SetStatusText('Score: ' + str(self.Score) + ' - PAUSED')
		else:
			self.timer.Start(Board.Speed)
			self.GetParent().statusBar.SetStatusText('Score: ' + str(self.Score))
		self.Refresh()
	
	def SetSnakeDir(self, newDir):
		if newDir == self.Snake.HeadDir:
			return
		elif newDir == SnakeDir.UP and self.Snake.HeadDir == SnakeDir.DOWN:
			return
		elif newDir == SnakeDir.DOWN and self.Snake.HeadDir == SnakeDir.UP:
			return
		elif newDir == SnakeDir.LEFT and self.Snake.HeadDir == SnakeDir.RIGHT:
			return
		elif newDir == SnakeDir.RIGHT and self.Snake.HeadDir == SnakeDir.LEFT:
			return
		else:
			self.Snake.SetHeadDir(newDir)
			self.Snake.SaveTurnPos()
	
	# Does nothing, catches erase background event to prevent flickering
	def OnEraseBkgd(self, e):
		return
	
	def OnKeyDown(self, e):
		keycode = e.GetKeyCode()
		if keycode == ord('P') or keycode == ord('p'):
			self.Pause()
			return
		if keycode == ord('X') or keycode == ord('x'):
			self.GetParent().Close(True)
			return
		if self.isPaused:
			return
		# elif keycode == wx.WXK_LEFT:
			# self.SetSnakeDir(SnakeDir.LEFT)
			# print LEFT
		# elif keycode == wx.WXK_RIGHT:
			# self.SetSnakeDir(SnakeDir.RIGHT)
			# print RIGHT
		# elif keycode == wx.WXK_DOWN:
			# self.SetSnakeDir(SnakeDir.DOWN)
			# print DOWN
		# elif keycode == wx.WXK_UP:
			# self.SetSnakeDir(SnakeDir.UP)
			# print UP
		if keycode == ord('A') or keycode == ord('a'):
			self.SetSnakeDir(SnakeDir.LEFT)
		elif keycode == ord('D') or keycode == ord('d'):
			self.SetSnakeDir(SnakeDir.RIGHT)
		elif keycode == ord('S') or keycode == ord('s'):
			self.SetSnakeDir(SnakeDir.DOWN)
		elif keycode == ord('W') or keycode == ord('w'):
			self.SetSnakeDir(SnakeDir.UP)
		else:
			e.Skip()
	
	def OnPaint(self, e):
		dc = wx.BufferedPaintDC(self)
		dc.Clear()
		self.DrawSnake(dc)
	
	def DrawSnake(self, dc):
		snakeLen = self.Snake.GetLength()
		snakeWidth = self.Snake.GetWidth()
		headPos = self.Snake.GetPos()
		dc.SetPen(wx.Pen(wx.BLACK,snakeWidth))
		for segments in self.Snake.Body:
			dc.DrawLines(segments)
	
	def OnTimer(self, e):
		if e.GetId() == Board.ID_TIMER:
			self.Snake.Move()
			self.Refresh()
		else:
			e.Skip()
			
app = wx.App(False) 
frame = SnakeGame(None, 'Snake')
app.MainLoop()

