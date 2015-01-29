import os
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# GenRanOff
#

class GenRanOff:
  def __init__(self, parent):
    parent.title = "GenRanOff" # TODO make this more human readable by adding spaces
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['GenRanOff'] = self.runTest

  def runTest(self):
    tester = GenRanOffTest()
    tester.runTest()

#
# GenRanOffWidget
#

class GenRanOffWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.collapsed = True
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "GenRanOff Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Target List selector
    #
    self.targetListSelector = slicer.qMRMLNodeComboBox()
    self.targetListSelector.nodeTypes = ( ("vtkMRMLMarkupsFiducialNode"), "" )
    self.targetListSelector.selectNodeUponCreation = False
    self.targetListSelector.addEnabled = False
    self.targetListSelector.removeEnabled = False
    self.targetListSelector.noneEnabled = False
    self.targetListSelector.showHidden = False
    self.targetListSelector.showChildNodeTypes = False
    self.targetListSelector.setMRMLScene( slicer.mrmlScene )
    self.targetListSelector.setToolTip( "Pick the target list." )
    parametersFormLayout.addRow("Target List: ", self.targetListSelector)

    #
    # Target selector
    #
    self.targetSelector = qt.QComboBox()
    parametersFormLayout.addRow("Target: ",self.targetSelector)

    #
    # Offset selection
    #
    offsetLayout = qt.QHBoxLayout()

    xOffsetLabel = qt.QLabel("X: ")
    self.xOffset = qt.QDoubleSpinBox()
    self.xOffset.setFixedWidth(80)
    self.xOffset.setMinimum(-20)
    self.xOffset.setMaximum(20)
    offsetLayout.addWidget(xOffsetLabel)
    offsetLayout.addWidget(self.xOffset)

    yOffsetLabel = qt.QLabel("Y: ")
    self.yOffset = qt.QDoubleSpinBox()
    self.yOffset.setFixedWidth(80)
    self.yOffset.setMinimum(-20)
    self.yOffset.setMaximum(20)
    offsetLayout.addWidget(yOffsetLabel)
    offsetLayout.addWidget(self.yOffset)

    zOffsetLabel = qt.QLabel("Z: ")
    self.zOffset = qt.QDoubleSpinBox()
    self.zOffset.setFixedWidth(80)
    self.zOffset.setMinimum(-20)
    self.zOffset.setMaximum(20)
    offsetLayout.addWidget(zOffsetLabel)
    offsetLayout.addWidget(self.zOffset)

    offsetLayout.addStretch()

    offsetBox = ctk.ctkCollapsibleGroupBox()
    offsetBox.setTitle("Offset")
    offsetBox.setLayout(offsetLayout)
    parametersFormLayout.addRow(offsetBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply offset")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.targetListSelector.connect("nodeActivated(vtkMRMLNode*)", self.onTargetListSelect)
    self.targetSelector.connect("activated(int)", self.onTargetActivated)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onTargetListSelect(self):
    self.originalTargetList = {}
    self.targetSelector.clear()
    self.targetList = self.targetListSelector.currentNode()
    if self.targetList != None:
      for i in range(self.targetList.GetNumberOfFiducials()):
        fidPos = [0.0, 0.0, 0.0]
        self.targetList.GetNthFiducialPosition(i,fidPos)
        self.originalTargetList[i] = fidPos
        self.targetSelector.addItem(self.targetList.GetNthFiducialLabel(i))

  def onTargetActivated(self,index):
    self.targetIndex = index
    self.applyButton.enabled = True

  def onApplyButton(self):
    logic = GenRanOffLogic()
    print("Run the algorithm")
    logic.run(self.originalTargetList, self.targetList, self.targetIndex, self.xOffset.value, self.yOffset.value, self.zOffset.value)

  def onReload(self,moduleName="GenRanOff"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onReloadAndTest(self,moduleName="GenRanOff"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(),
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")


#
# GenRanOffLogic
#

class GenRanOffLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def run(self,originalTargetList,targetList,targetIndex,xOffset,yOffset,zOffset):
    """
    Run the actual algorithm
    """
    
    if (targetList == None) or (targetIndex < 0):
      return False

    print "Here: " + str(xOffset)
    targetList.SetNthFiducialPosition(targetIndex, 
                                      originalTargetList[targetIndex][0]+xOffset,
                                      originalTargetList[targetIndex][1]+yOffset,
                                      originalTargetList[targetIndex][2]+zOffset)

    return True


class GenRanOffTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_GenRanOff1()

  def test_GenRanOff1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = GenRanOffLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
