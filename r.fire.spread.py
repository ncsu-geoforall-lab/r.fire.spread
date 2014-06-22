#!/usr/bin/env python
############################################################################
#
# MODULE:       r.fire.spread
# AUTHOR(S):    Vaclav Petras
# PURPOSE:      Wrapper for r.ros and r.spread
# COPYRIGHT:    (C) 2014 by Vaclav Petras, and the GRASS Development Team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
############################################################################

#%module
#% label: Simulates elliptically anisotropic spread.
#% description: Generates a raster map of the cumulative time of spread, given raster maps containing the rates of spread (ROS), the ROS directions and the spread origins. It optionally produces raster maps to contain backlink UTM coordinates for tracing spread paths. Usable for fire spread simulations.
#% keywords: raster, fire, spread, hazard
#%end
#%flag
#% key: s
#% description: Consider spotting effect
#% guisection: Spotting
#%end
#%option
#% key: start
#% type: string
#% required: yes
#% multiple: no
#% description: Name of an existing raster map layer in the user's current mapset search path containing starting locations of the spread phenomenon. Any positive integers in this map are recognized as starting sources (seeds).
#% gisprompt: old,cell,raster
#% guisection: Input maps
#%end
#%option
#% key: w_speed
#% type: string
#% required: no
#% multiple: no
#% label: Raster map containing midflame wind speed (ft/min, required with -s)
#% description: Name of an existing raster map layer in the user's current mapset search path containing wind velocities at half of the average flame height (feet/minute).
#% gisprompt: old,cell,raster
#% guisection: Spotting
#%end
#%option
#% key: f_mois
#% type: string
#% required: no
#% multiple: no
#% label: Raster map containing fine fuel moisture of the cell receiving a spotting firebrand (%, required with -s)
#% description: Name of an existing raster map layer in the user's current mapset search path containing the 1-hour (<.25") fuel moisture (percentage content multiplied by 100).
#% gisprompt: old,cell,raster
#% guisection: Spotting
#%end
#%option
#% key: least_size
#% type: string
#% required: no
#% multiple: no
#% options: 3,5,7,9,11,13,15
#% key_desc: odd int
#% description: An odd integer ranging 3 - 15 indicating the basic sampling window size within which all cells will be considered to see whether they will be reached by the current spread cell. The default number is 3 which means a 3x3 window.
#% guisection: Advanced
#%end
#%option
#% key: comp_dens
#% type: string
#% required: no
#% multiple: no
#% key_desc: decimal
#% label: Sampling density for additional computing (range: 0.0 - 1.0 (0.5))
#% description: A decimal number ranging 0.0 - 1.0 indicating additional sampling cells will be considered to see whether they will be reached by the current spread cell. The closer to 1.0 the decimal number is, the longer the program will run and the higher the simulation accuracy will be. The default number is 0.5.
#% guisection: Advanced
#%end
#%option
#% key: times
#% type: string
#% required: yes
#% multiple: yes
#% key_desc: int (>= 0)
#% description: Times of changes.
#%end
#%option
#% key: lag
#% type: string
#% required: yes
#% multiple: no
#% key_desc: int (>= 0)
#% description: A non-negative integer specifying the simulating duration time lag (minutes). The default is infinite, but the program will terminate when the current geographic region/mask has been filled. It also controls the computational time, the shorter the time lag, the faster the program will run. Is required although is not for the r.spread.
#%end
#%option
#% key: time_step
#% type: string
#% required: yes
#% multiple: no
#% key_desc: int (>= 0)
#% description: Time interval of saving simulation results.
#%end
#%option
#% key: output
#% type: string
#% required: yes
#% multiple: no
#% label: Raster map to contain output spread time (min)
#% description: Name of the new raster map layer to contain the results of the cumulative spread time needed for a phenomenon to reach each cell from the starting sources (minutes).
#% gisprompt: new,cell,raster
#% guisection: Output maps
#%end

#%option
#% key: model
#% type: string
#% required: yes
#% multiple: no
#% key_desc: name
#% label: Raster map containing fuel models
#% description: Name of an existing raster map layer in the user's current mapset search path containing the standard fuel models defined by the USDA Forest Service. Valid values are 1-13; other numbers are recognized as barriers by r.ros.
#% gisprompt: old,cell,raster
#%end
#%option
#% key: moisture_1h
#% type: string
#% required: no
#% multiple: yes
#% key_desc: name
#% label: Raster map containing the 1-hour fuel moisture (%)
#% description: Name of an existing raster map layer in the user's current mapset search path containing the 1-hour (<.25") fuel moisture (percentage content multiplied by 100).
#% gisprompt: old,cell,raster
#%end
#%option
#% key: moisture_10h
#% type: string
#% required: no
#% multiple: yes
#% key_desc: name
#% label: Raster map containing the 10-hour fuel moisture (%)
#% description: Name of an existing raster map layer in the user's current mapset search path containing the 10-hour (.25-1") fuel moisture (percentage content multiplied by 100).
#% gisprompt: old,cell,raster
#%end
#%option
#% key: moisture_100h
#% type: string
#% required: no
#% multiple: yes
#% key_desc: name
#% label: Raster map containing the 100-hour fuel moisture (%)
#% description: Name of an existing raster map layer in the user's current mapset search path containing the 100-hour (1-3") fuel moisture (percentage content multiplied by 100).
#% gisprompt: old,cell,raster
#%end
#%option
#% key: moisture_live
#% type: string
#% required: yes
#% multiple: yes
#% key_desc: name
#% label: Raster map containing live fuel moisture (%)
#% description: Name of an existing raster map layer in the user's current mapset search path containing live (herbaceous) fuel moisture (percentage content multiplied by 100).
#% gisprompt: old,cell,raster
#%end
#%option
#% key: velocity
#% type: string
#% required: no
#% multiple: yes
#% key_desc: name
#% description: Name of an existing raster map layer in the user's current mapset search path containing wind velocities at half of the average flame height (feet/minute).
#% gisprompt: old,cell,raster
#%end
#%option
#% key: direction
#% type: string
#% required: no
#% multiple: yes
#% key_desc: name
#% label: Name of raster map containing wind directions (degree)
#% description: Name of an existing raster map layer in the user's current mapset search path containing wind direction, clockwise from north (degree).
#% gisprompt: old,cell,raster
#%end
#%option
#% key: slope
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% label: Name of raster map containing slope (degree)
#% description: Name of an existing raster map layer in the user's current mapset search path containing topographic slope (degree).
#% gisprompt: old,cell,raster
#%end
#%option
#% key: aspect
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% label: Raster map containing aspect (degree, CCW from E)
#% description: Name of an existing raster map layer in the user's current mapset search path containing topographic aspect, counterclockwise from east (GRASS convention) in degrees.
#% gisprompt: old,cell,raster
#%end
#%option
#% key: elevation
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% label: Raster map containing elevation (m, required with -s)
#% description: Name of an existing raster map layer in the user's current mapset search path containing elevation (meters). Option is required from spotting distance computation (when -s flag is enabled)
#% gisprompt: old,cell,raster
#% guisection: Spotting
#%end
#%option
#% key: speed
#% type: string
#% required: no
#% multiple: no
#% key_desc: name
#% description: Name of an existing raster map layer in the user's current mapset search path containing wind velocities at half of the average flame height (feet/minute).
#% gisprompt: old,cell,raster
#%end

# description: Prefix for output raster maps (.base, .max, .maxdir, .spotdist)

# -*- coding: utf-8 -*-

"""
Created on Wed Mar 19 20:59:06 2014

@author: Vaclav Petras
"""

import sys

import grass.script.core as gcore
from grass.script.core import run_command, write_command

# print-only version of run_command for debugging
#def run_command(*args, **kwargs):
#    command = ''
#    for arg in args:
#        command += arg + ' '
#    for key, value in kwargs.iteritems():
#        command += key + '=' + str(value) + ' '
#    print command


# this has much simpler solution using concat, set and sorted
def determine_simulation_times(time_step, max_time, change_times):
    """
    >>> determine_simulation_times(2, 9, [0, 3, 5])
    [0, 2, 3, 4, 5, 6, 8]
    >>> determine_simulation_times(1, 10, [0, 2, 5])
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> determine_simulation_times(3, 11, [0, 5])
    [0, 3, 5, 6, 9]
    >>> determine_simulation_times(4, 16, [0, 4, 12])
    [0, 4, 8, 12, 16]
    >>> determine_simulation_times(4, 16, [0, 4, 12, 20])
    [0, 4, 8, 12, 16]
    >>> step = 3
    >>> max_time = 14
    >>> changes = [0, 2, 6, 7]
    >>> export_times = range(0, max_time, step)
    >>> sorted(set(export_times + changes))
    [0, 2, 3, 6, 7, 9, 12]
    >>> determine_simulation_times(step, max_time, changes)
    [0, 2, 3, 6, 7, 9, 12]
    """
    current_time = 0
    simulation_times = [current_time]
    current_change_time_index = 0
    next_change_time = change_times[current_change_time_index + 1]
    while current_time < max_time:
        if next_change_time > current_time and \
           next_change_time < current_time + time_step:
            simulation_times.append(next_change_time)
            if current_change_time_index + 1 < len(change_times):
                current_change_time_index += 1
            if not current_change_time_index + 1 >= len(change_times):
                next_change_time = change_times[current_change_time_index + 1]
        current_time += time_step
        if current_time > max_time:
            break
        simulation_times.append(current_time)
    return simulation_times


def times_to_intervals(simulation_times):
    """
    >>> times_to_intervals([0, 4, 5, 8, 9, 12])
    [(0, 4), (4, 5), (5, 8), (8, 9), (9, 12)]
    """
    intervals = []
    for i in range(len(simulation_times)):
        if i < len(simulation_times) - 1:
            interval = (simulation_times[i], simulation_times[i+1])
            intervals.append(interval)
    return intervals


def data_for_intervals(intervals, data_times):
    """
    >>> data_for_intervals([(0, 4), (4, 5), (5, 8)], [0, 5])
    [0, 0, 5]
    >>> data_for_intervals([(0, 3), (3, 4), (4, 5), (5, 6)], [0, 3, 4, 5, 6])
    [0, 3, 4, 5]
    >>> data_for_intervals([(0, 1), (1, 3), (3, 8), (8, 9)], [0, 3])
    [0, 0, 3, 3]
    """
    interval_data = []
    i = 0
    #for j in range(j, len(intervals)):
    for interval in intervals:
        #if data_times[i] == intervals[j][0]:
        if data_times[i] == interval[0]:
            #print "eq", data_times[i], intervals[j][0]
            interval_data.append(data_times[i])
            current_data = data_times[i]
            if i + 1 < len(data_times):
                i += 1
            #print i
        else:
            #print "nq", data_times[i], intervals[j][0]
            interval_data.append(current_data)
    return interval_data


def data_indexes_for_intervals(intervals, data_times):
    """
    >>> data_indexes_for_intervals([(0, 4), (4, 5), (5, 8)], [0, 5])
    [0, 0, 1]
    >>> data_indexes_for_intervals([(0, 3), (3, 4), (4, 5), (5, 6)], [0, 3, 4, 5, 6])
    [0, 1, 2, 3]
    >>> data_indexes_for_intervals([(0, 1), (1, 3), (3, 8), (8, 9)], [0, 3])
    [0, 0, 1, 1]
    """
    indexes = []
    i = 0
    #for j in range(j, len(intervals)):
    for interval in intervals:
        #if data_times[i] == intervals[j][0]:
        if data_times[i] == interval[0]:
            #print "eq", data_times[i], intervals[j][0]
            indexes.append(i)
            current_data = i
            if i + 1 < len(data_times):
                i += 1
            #print i
        else:
            #print "nq", data_times[i], intervals[j][0]
            indexes.append(current_data)
    return indexes


from math import log


def number_lenght(number):
    """
    >>> number_lenght(239)
    3
    >>> number_lenght(46)
    2
    >>> number_lenght(7)
    1
    """
    return int(log(number, 10)) + 1


def format_order(number, zeros):
    """
    >>> format_order(2, 3)
    '002'
    >>> format_order(3, 1)
    '3'
    >>> format_order(5269, 4)
    '5269'
    >>> numbers = [5, 56, 8547, 189, 0]
    >>> lenght = number_lenght(max(numbers))
    >>> [format_order(number, lenght) for number in numbers]
    ['0005', '0056', '8547', '0189', '0000']
    """
    return str(number).zfill(zeros)


def output_names_for_intervals(basename, intervals):
    """
    >>> output_names_for_intervals('fire', [(0, 4), (4, 5), (5, 8)])
    ['fire_4', 'fire_5', 'fire_8']
    >>> output_names_for_intervals('firespread', [(0, 3), (3, 12)])
    ['firespread_03', 'firespread_12']
    >>> output_names_for_intervals('fire_spread', [(0, 1), (1, 26), (26, 150)])
    ['fire_spread_001', 'fire_spread_026', 'fire_spread_150']
    """
    names = []
    maximum = intervals[-1][1]
#    print maximum
    lenght = number_lenght(maximum)
 #   print lenght
    for interval in intervals:
        names.append(basename + '_' + format_order(interval[1], lenght))
    return names


# named tuple version of the class bellow
#FireSimulationParams = namedtuple('FireSimulationParams',
#                                  'model moistures_live '
#                                  'moistures_1h moistures_10h moistures_100h '
#                                  'wind_directions wind_velocities '
#                                  'slope aspect elevation '
#                                  'start_raster')
class FireSimulationParams:
    def __init__(self, model=None, moistures_live=None,
                 moistures_1h=None, moistures_10h=None, moistures_100h=None,
                 wind_directions=None, wind_velocities=None,
                 slope=None, aspect=None, elevation=None,
                 start_raster=None):
        self.model = model
        self.moistures_live = moistures_live
        self.moistures_1h = moistures_1h
        self.moistures_10h = moistures_10h
        self.moistures_100h = moistures_100h
        self.wind_directions = wind_directions
        self.wind_velocities = wind_velocities
        self.slope = slope
        self.aspect = aspect
        self.elevation = elevation
        self.start_raster = start_raster

    def assert_not_none_attributes(self):
        """Check if all attributes are set (testing against None)"""
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                assert value is not None, "%s is None" % key


def simulate_fire(params, simulation_intervals, data_indexes, outputs):
    """
    n = ['a' , 'b', 'c']
    o = ['i' , 'j', 'k', 'l']
    params = FireSimulationParams(model='m', moistures_live=n, moistures_1h=n, moistures_10h=n, moistures_100h=n, wind_directions=n, wind_velocities=n, start_raster='x', slope='o', aspect='p', elevation='q')
    simulate_fire(params, [(0, 1), (1, 3), (3, 8), (8, 9)], [0, 1, 1, 2], o)
    """
    start_raster = params.start_raster
    # TODO: clean the tmp maps: g.mremove rast="rfirespread_rros_out*" -f
    ros_basename = 'rfirespread_rros_out'
    ros_base = ros_basename + '.base'
    ros_max = ros_basename + '.max'
    ros_maxdir = ros_basename + '.maxdir'
    rros_params = dict(model=params.model,
                       slope=params.slope, aspect=params.aspect,
                       elevation=params.elevation,
                       output=ros_basename)

    for index, interval in enumerate(simulation_intervals):
        # print ">>>>>>>>>", index, interval, params.model, params.moistures_100h[data_indexes[index]], params.wind_directions[data_indexes[index]], params.wind_velocities[data_indexes[index]]
        # TODO: change the print to message
        rros_params['moisture_live'] = params.moistures_live[data_indexes[index]]
        if params.moistures_1h:
            rros_params['moisture_1h'] = params.moistures_1h[data_indexes[index]]
        if params.moistures_10h:
            rros_params['moisture_10h'] = params.moistures_10h[data_indexes[index]]
        if params.moistures_100h:
            rros_params['moisture_100h'] = params.moistures_100h[data_indexes[index]]
        if params.wind_directions:
            rros_params['direction'] = params.wind_directions[data_indexes[index]]
        if params.wind_velocities:
            rros_params['velocity'] = params.wind_velocities[data_indexes[index]]

        ret = run_command('r.ros', **rros_params)
        if ret != 0:
            gcore.fatal(_("r.ros failed. Please check above error messages."))
        ret = run_command('r.spread',
                          max=ros_max, dir=ros_maxdir, base=ros_base,
                          start=start_raster, output=outputs[index],
                          init_time=interval[0], lag=interval[1] - interval[0])
        print "interval =", interval
        print "difference =", interval[1] - interval[0]
        print gcore.read_command('r.info', map=outputs[index])
        if ret != 0:
            gcore.fatal(_("r.spread failed. Please check above error messages."))
        ret = run_command('g.remove', rast=[ros_base, ros_max, ros_maxdir])
        if ret != 0:
            gcore.fatal(_("g.remove failed when cleaning after r.ros and r.spread."
                          " This might mean the error of programmer or unexpected behavior of one of the modules."
                          " Please check above error messages."))
        ret = run_command('r.null', map=outputs[index], setnull=0)
        if ret != 0:
            gcore.fatal(_("r.null failed. Please check above error messages."))
        ret = write_command('r.colors', map=outputs[index], rules='-',
                            stdin="""
                            0% 50:50:50
                            60% yellow
                            100% red
                            """)
        if ret != 0:
            gcore.fatal(_("r.colors failed. Please check above error messages."))
        start_raster = outputs[index]


def main():

    sim_params = FireSimulationParams()

    options, flags = gcore.parser()

    sim_params.model = options['model']
    sim_params.moistures_live = options['moisture_live'].split(',')
    if options['moisture_1h']:
        sim_params.moistures_1h = options['moisture_1h'].split(',')
    else:
        sim_params.moistures_1h = None
    if options['moisture_10h']:
        sim_params.moistures_10h = options['moisture_10h'].split(',')
    else:
        sim_params.moistures_10h = None
    if options['moisture_100h']:
        sim_params.moistures_100h = options['moisture_100h'].split(',')
    else:
        sim_params.moistures_100h = None
    if options['direction']:
        sim_params.wind_directions = options['direction'].split(',')
    else:
        sim_params.wind_directions = None
    if options['speed']:
        sim_params.wind_velocities = options['speed'].split(',')
    else:
        sim_params.wind_velocities = None

    sim_params.slope = options['slope']
    sim_params.aspect = options['aspect']
    sim_params.elevation = options['elevation']

    sim_params.start_raster = options['start']
    basename = options['output']

    # TODO: handle no dead moistures
    # TODO: add handling of 0 (or 1?) at the beginning of times
    # TODO: change name of lag?
    # TODO: check if times and maps has the same sizes
    # TODO: check if multiple things are multiple
    # TODO: resolve inconsitency in speed vs velocity
    # TODO: create convention for plural for options with multiple

    change_times = [int(i) for i in options['times'].split(',')]
    max_time = int(options['lag'])
    time_step = int(options['time_step'])

    number_of_changes = len(change_times)
    for i in [sim_params.moistures_live, sim_params.moistures_1h, sim_params.moistures_10h, sim_params.moistures_100h, sim_params.wind_directions, sim_params.wind_velocities]:
        # here allowing None as valid state
        if i is not None and len(i) != number_of_changes:
            gcore.fatal(_("Lenghts does not match:"
                          " times={t}, maps are {i}").format(t=number_of_changes,
                                                             i=i))
            # TODO: make this one by one to make it informative

    export_times = range(0, max_time + 1, time_step)
    simulation_times = sorted(set(export_times + change_times))

    simulation_intervals = times_to_intervals(simulation_times)
    data_indexes = data_indexes_for_intervals(simulation_intervals, change_times)
    outputs = output_names_for_intervals(basename, simulation_intervals)

    # TODO: fix for r.ros/r.spread acceptable None/empty attributes
    # sim_params.assert_not_none_attributes()

    simulate_fire(sim_params, simulation_intervals, data_indexes, outputs=outputs)

    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'doctest':
        import doctest
        doctest.testmod()
    else:
        sys.exit(main())
