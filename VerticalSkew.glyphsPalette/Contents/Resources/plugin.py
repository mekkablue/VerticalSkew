# encoding: utf-8

###########################################################################################################
#
#
#	Palette Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Palette
#
#
###########################################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from GlyphsApp import GSBottomLeft, GSCenterLeft, GSTopLeft, GSBottomRight, GSCenterRight, GSTopRight
import math

class VerticalSkew (PalettePlugin):
	
	dialog = objc.IBOutlet()
	textField = objc.IBOutlet()
	upButton = objc.IBOutlet()
	downButton = objc.IBOutlet()
	
	def settings(self):
		self.name = Glyphs.localize({
			'en': u'Vertical Skew',
			'de': u'Vertikal neigen'
		})
		
		self.dialogName = self.name
		
		# if user never triggered a transform origin in the Transformations palette:
		if Glyphs.defaults["GSTransformationsMetricsOriginType"] is None:
			Glyphs.defaults["GSTransformationsMetricsOriginType"] = 0
		
		# Load .nib dialog (without .extension)
		self.loadNib('IBdialog', __file__)
	
	def start(self):
		# Adding a callback for the 'GSUpdateInterface' event
		# Glyphs.addCallback(self.update, UPDATEINTERFACE)
		Glyphs.registerDefault('com.mekkablue.VerticalSkew.angle', 5.0)
		self.textField.setFloatValue_(float(Glyphs.defaults['com.mekkablue.VerticalSkew.angle']))
	
	def __del__(self):
		pass
		#Glyphs.removeCallback(self.update)
	
	def transform( self, skew=0.0, origin=NSZeroPoint ):
		myTransform = NSAffineTransform.transform()
		myTransform.shearYBy_atCenter_(math.tan(math.radians(skew)), -origin.x)
		return myTransform

	# Action triggered by UI
	@objc.IBAction
	def setAngle_( self, sender ):
		# Store angle coming in from dialog
		Glyphs.defaults['com.mekkablue.VerticalSkew.angle'] = sender.floatValue()
		
	# Action triggered by UI
	@objc.IBAction
	def upScale_( self, sender ):
		skewAngle = Glyphs.defaults['com.mekkablue.VerticalSkew.angle']
		if skewAngle:
			self.verticalSkew( Glyphs.font, skewAngle )
	
	# Action triggered by UI
	@objc.IBAction
	def downScale_( self, sender ):
		skewAngle = Glyphs.defaults['com.mekkablue.VerticalSkew.angle']
		if skewAngle:
			self.verticalSkew( Glyphs.font, -skewAngle )
	
	def transformOrigin(self,bounds):
		originType = int(Glyphs.defaults["GSTransformationsMetricsOriginType"])
		gridChoice = int(Glyphs.defaults["selectedTransformGridCorner"])
		pivotX = 0.0
		
		# origin grid or metrics choice:
		if originType%2 == 0:
			if gridChoice == GSBottomLeft or gridChoice == GSCenterLeft or gridChoice == GSTopLeft:
				pivotX = bounds.origin.x
			elif gridChoice == GSBottomRight or gridChoice == GSCenterRight or gridChoice == GSTopRight:
				pivotX = bounds.origin.x + bounds.size.width
			else: 
				# if gridChoice == GSBottomCenter or gridChoice == GSCenterCenter or gridChoice == GSTopCenter:
				pivotX = bounds.origin.x + bounds.size.width * 0.5
		
		# free point:
		elif originType == 1:
			pivotX = float(Glyphs.defaults["GSTransformOriginX"])
		
		return NSPoint(pivotX,0.0)
	
	def verticalSkew( self, font, angle ):
		if font:
			layers = font.selectedLayers
			
			# mutiple layers (or no selection):
			if len(layers) > 1 or (len(layers)==1 and len(layers[0].selection)==0):
				for thisLayer in layers:
					transformOrigin = self.transformOrigin(thisLayer.bounds)
					layerTransform = self.transform(skew=angle, origin=transformOrigin)
					matrix = layerTransform.transformStruct()
					thisLayer.applyTransform(matrix)
					
			# selection in a single layer:
			elif len(layers) == 1 and layers[0].selection:
				thisLayer = layers[0]
				transformOrigin = self.transformOrigin(thisLayer.selectionBounds)
				selectionTransform = self.transform(skew=angle, origin=transformOrigin)
				
				for thisItem in thisLayer.selection:
					if type(thisItem) == GSComponent:
						matrix = selectionTransform.transformStruct()
						thisItem.applyTransform(matrix)
					else:
						try:
							thisItem.position = selectionTransform.transformPoint_(thisItem.position)
						except:
							pass
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
	
	_sortID = 41
	def setSortID_(self, id):
		try:
			self._sortID = id
		except Exception as e:
			self.logToConsole( "setSortID_: %s" % str(e) )
	def sortID(self):
		return self._sortID
	