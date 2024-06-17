import numpy as np
import openmdao.api as om

def get_variable_value(output_file,variable_name,units=None):
    with open(output_file) as file:
        lines = file.readlines()
    for line in lines:
        if variable_name in line:
            # Remove brackets and convert to float
            columns = line.split()
            if units is not None:
                value = columns[1].replace('[', '').replace(']', '')
                value = float(value)
                if columns[2] != units:
                    value = om.convert_units(value, columns[2], units)
                return value
            value = line.split()[1].replace('[', '').replace(']', '')
            return (float(value))

    raise ValueError(f'Variable {variable_name} not found in file')

variable_name = 'ac|geom|wing|S_ref'
value = get_variable_value('comparison/OpenConcept/output_list_op.txt',variable_name,'ft**2')
print(f'The value of {variable_name} is {value}')

print(om.convert_units(1,'pt','cL'))