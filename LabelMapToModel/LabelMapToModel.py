import os
import unittest
import itk
import vtk
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
import logging


class LabelMapToModel(ScriptedLoadableModule):

    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        # TODO make this more human readable by adding spaces
        self.parent.title = "Label Map To Model"
        self.parent.categories = ["Surface Models"]
        self.parent.dependencies = []
        # replace with "Firstname Lastname (Organization)"
        self.parent.contributors = ["Matt McCormick (Kitware, Inc.)"]
        self.parent.helpText = """
    Convert a Slicer Label Map image into a Slicer Model (mesh).
    """
        self.parent.acknowledgementText = """
    This file was originally developed by Matthew McCormick, Kitware, Inc.
    and was partially funded by NIH grant R41CA196565.
"""


class LabelMapToModelWidget(ScriptedLoadableModuleWidget):

    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Instantiate and connect widgets ...

        #
        # Parameters Area
        #
        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters"
        self.layout.addWidget(parametersCollapsibleButton)

        # Layout within the dummy collapsible button
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

        #
        # Input label map selector
        #
        self.inputSelector = slicer.qMRMLNodeComboBox()
        self.inputSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
        self.inputSelector.selectNodeUponCreation = True
        self.inputSelector.addEnabled = False
        self.inputSelector.removeEnabled = False
        self.inputSelector.noneEnabled = False
        self.inputSelector.showHidden = False
        self.inputSelector.showChildNodeTypes = False
        self.inputSelector.setMRMLScene(slicer.mrmlScene)
        self.inputSelector.setToolTip("Pick the input label map.")
        parametersFormLayout.addRow("Input Label Map: ", self.inputSelector)

        #
        # Output model selector
        #
        self.outputSelector = slicer.qMRMLNodeComboBox()
        self.outputSelector.nodeTypes = ["vtkMRMLModelNode"]
        self.outputSelector.selectNodeUponCreation = True
        self.outputSelector.addEnabled = True
        self.outputSelector.removeEnabled = True
        self.outputSelector.noneEnabled = True
        self.outputSelector.showHidden = False
        self.outputSelector.showChildNodeTypes = False
        self.outputSelector.setMRMLScene(slicer.mrmlScene)
        self.outputSelector.setToolTip("Pick the output model.")
        parametersFormLayout.addRow("Output Model: ", self.outputSelector)

        #
        # Apply button
        #
        self.applyButton = qt.QPushButton("Apply")
        self.applyButton.toolTip = "Run the algorithm."
        self.applyButton.enabled = False
        parametersFormLayout.addRow(self.applyButton)

        # Connections
        self.applyButton.connect('clicked(bool)', self.onApplyButton)
        self.inputSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onSelect)
        self.outputSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.onSelect)

        # Add vertical spacer
        self.layout.addStretch(1)

        # Refresh Apply button state
        self.onSelect()

    def cleanup(self):
        pass

    def onSelect(self):
        self.applyButton.enabled = self.inputSelector.currentNode(
        ) and self.outputSelector.currentNode()

    def onApplyButton(self):
        logic = LabelMapToModelLogic()
        logic.run(self.inputSelector.currentNode(),
                  self.outputSelector.currentNode())


class LabelMapToModelLogic(ScriptedLoadableModuleLogic):

    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def hasImageData(self, labelMapNode):
        """Returns true if the passed in volume node has valid image data."""
        if not labelMapNode:
            logging.debug('hasImageData failed: no volume node')
            return False
        if labelMapNode.GetImageData() == None:
            logging.debug('hasImageData failed: no image data in volume node')
            return False
        return True

    def isValidInputOutputData(self, inputLabelMap, outputModel):
        """Validates that the inputs and outputs are present."""
        if not inputLabelMap:
            logging.debug('isValidInputOutputData failed: no input label map node defined')
            return False
        if not outputModel:
            logging.debug('isValidInputOutputData failed: no output model node defined')
            return False
        return True

    def run(self, inputLabelMap, outputModel):
        """
        Run the actual algorithm
        """

        if not self.isValidInputOutputData(inputLabelMap, outputModel):
            slicer.util.errorDisplay(
                'Input volume is the same as output volume. Choose a different output volume.')
            return False

        logging.info('Processing started')

        labelVtkData = inputLabelMap.GetImageData()

        if labelVtkData.GetScalarTypeAsString == 'unsigned char':
            PixelType = itk.UC
        else:
            slicer.util.errorDisplay('Pixel type of the label map is not yet supported.')
            return False

        Dimension = 3

        logging.info('Processing completed')

        return True


class LabelMapToModelTest(ScriptedLoadableModuleTest):

    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_LabelMapToModel1()

    def test_LabelMapToModel1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
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
            ('http://slicer.kitware.com/midas3/download?items=153172',
             'BrainTumor_GBM_HG0003.mrb', slicer.util.loadScene),
        )

        for url, name, loader in downloads:
            filePath = slicer.app.temporaryPath + '/' + name
            if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
                logging.info(
                    'Requesting download %s from %s...\n' % (name, url))
                urllib.urlretrieve(url, filePath)
            if loader:
                logging.info('Loading %s...' % (name,))
                loader(filePath)
        self.delayDisplay('Finished with download and loading')

        labelMapNode = slicer.util.getNode(pattern="Tissue Segmentation Volume")
        logic = LabelMapToModelLogic()
        self.assertTrue(logic.hasImageData(labelMapNode))
        modelNode = slicer.vtkMRMLModelNode()
        logic.run(labelMapNode, modelNode)
        self.delayDisplay('Test passed!')
