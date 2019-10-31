from qgis.processing import alg

@alg(name='save_attributes', label='Save Attributes As CSV',
    group='', group_label='')
@alg.input(type=alg.SOURCE, name='INPUT', label='Input Layer')
@alg.input(type=alg.FILE_DEST, name='OUTPUT', label='Output File')
def processAlgorithm(instance, parameters, context, feedback, inputs):
    """Saves the attributes of a vector layer to a CSV file."""
    source = instance.parameterAsSource(parameters, 'INPUT', context)
    csv = instance.parameterAsFileOutput(parameters, 'OUTPUT', context)


    fieldnames = [field.name() for field in source.fields()]

    # Compute the number of steps to display within the progress bar and
    # get features from source
    total = 100.0 / source.featureCount() if source.featureCount() else 0
    features = source.getFeatures()

    with open(csv, 'w') as output_file:
      # write header
      line = ','.join(name for name in fieldnames) + '\n'
      output_file.write(line)
      for current, f in enumerate(features):
          # Stop the algorithm if cancel button has been clicked
          if feedback.isCanceled():
              break

          # Add a feature in the sink
          line = ','.join(str(f[name]) for name in fieldnames) + '\n'
          output_file.write(line)

          # Update the progress bar
          feedback.setProgress(int(current * total))

    return {'OUTPUT': csv}