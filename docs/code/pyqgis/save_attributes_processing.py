from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFileDestination,
                       QgsVectorFileWriter,
                       QgsWkbTypes,
                       QgsProject)


class SaveAttributesAlgorithm(QgsProcessingAlgorithm):
    """Saves the attributes of a vector layer to a CSV file."""

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT',
                'Input layer',
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # We add a file output of type CSV.
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'OUTPUT',
                'Output File',
                'CSV files (*.csv)',
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(
            parameters,
            'INPUT',
            context)

        output = self.parameterAsFileOutput(
            parameters,
            'OUTPUT',
            context)

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / layer.featureCount() if layer.featureCount() else 0
        features = layer.getFeatures()
        
        # Define the options for saving the layer
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = 'CSV'
        save_options.fileEncoding = 'UTF-8'

        # Create the writer
        writer = QgsVectorFileWriter.create(
            fileName=output,
            fields=layer.fields(),
            geometryType=QgsWkbTypes.NoGeometry,
            srs=layer.crs(),
            transformContext=QgsProject.instance().transformContext(),
            options=save_options)

    
        for current, f in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Add the feature
            writer.addFeature(f)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        return {'OUTPUT': output}

    def name(self):
        return 'save_attributes'

    def displayName(self):
        return self.tr('Save Attributes As CSV')
 
    def group(self):
        return self.tr(self.groupId())

    def groupId(self):
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SaveAttributesAlgorithm()
