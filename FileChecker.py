def what_is_sensor_type(filename):
    if filename.__contains__('Accelerometer'):
        return 'accelerometer'
    elif filename.__contains__('Gyroscope'):
        return 'gyroscope'
    elif filename.__contains__('Magnetic'):
        return 'magnetic'
    elif filename.__contains__('Light'):
        return 'light'
    elif filename.__contains__('Proximity'):
        return 'proximity'
    elif filename.__contains__('GPS'):
        return 'gps'
    elif filename.__contains__('AmbientTemperature'):
        return 'temp'
    else:
        return 'NA'
