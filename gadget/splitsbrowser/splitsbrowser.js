/*!
 *  SplitsBrowser - Orienteering results analysis.
 *  
 *  Copyright (C) 2000-2013 Dave Ryder, Reinhard Balling, Andris Strazdins,
 *                          Ed Nash, Luke Woodward
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License along
 *  with this program; if not, write to the Free Software Foundation, Inc.,
 *  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */
// Tell JSHint not to complain that this isn't used anywhere.
/* exported SplitsBrowser */
var SplitsBrowser = { Version: "3.1.1", Model: {}, Input: {}, Controls: {} };


(function () {
    "use strict";
    
    // Whether a warning about missing messages has been given.  We don't
    // really want to irritate the user with many alert boxes if there's a
    // problem with the messages.
    var warnedAboutMessages = false;
    
    // Default alerter function, just calls window.alert.
    var alertFunc = function (message) { window.alert(message); };
    
    /**
    * Issue a warning about the messages, if a warning hasn't already been
    * issued.
    * @param {String} warning - The warning message to issue.
    */ 
    function warn(warning) {
        if (!warnedAboutMessages) {
            alertFunc(warning);
            warnedAboutMessages = true;
        }
    }
    
    /**
    * Sets the alerter to use when a warning message should be shown.
    *
    * This function is intended only for testing purposes.
    
    * @param {Function} alerter - The function to be called when a warning is
    *     to be shown.
    */
    SplitsBrowser.setMessageAlerter = function (alerter) {
        alertFunc = alerter;
    };
    
    /**
    * Returns the message with the given key.
    * @param {String} key - The key of the message.
    * @return {String} The message with the given key, or a placeholder string
    *     if the message could not be looked up.
    */
    SplitsBrowser.getMessage = function (key) {
        if (SplitsBrowser.hasOwnProperty("Messages")) {
            if (SplitsBrowser.Messages.hasOwnProperty(key)) {
                return SplitsBrowser.Messages[key];
            } else {
                warn("Message not found for key '" + key + "'");
                return "?????";
            }
        } else {
            warn("No messages found.  Has a language file been loaded?");
            return "?????";
        }
    };
    
    /**
    * Returns the message with the given key, with some string formatting
    * applied to the result.
    *
    * The object 'params' should map search strings to their replacements.
    *
    * @param {String} key - The key of the message.
    * @param {Object} params - Object mapping parameter names to values.
    */ 
    SplitsBrowser.getMessageWithFormatting = function (key, params) {
        var message = SplitsBrowser.getMessage(key);
        for (var paramName in params) {
            if (params.hasOwnProperty(paramName)) {
                // Irritatingly there isn't a way of doing global replace
                // without using regexps.  So we must escape any magic regex
                // metacharacters first, so that we have a regexp that will
                // match a single static string.
                var paramNameRegexEscaped = paramName.replace(/([.+*?|{}()^$\[\]\\])/g, "\\$1");
                message = message.replace(new RegExp(paramNameRegexEscaped, "g"), params[paramName]);
            }
        }
        
        return message;
    };
})();

(function () {
    "use strict";
    
    // Minimum length of a course that is considered to be given in metres as
    // opposed to kilometres.
    var MIN_COURSE_LENGTH_METRES = 500;

    /**
     * Utility function used with filters that simply returns the object given.
     * @param x - Any input value
     * @returns The input value.
     */
    SplitsBrowser.isTrue = function (x) { return x; };

    /**
    * Utility function that returns whether a value is not null.
    * @param x - Any input value.
    * @returns True if the value is not null, false otherwise.
    */
    SplitsBrowser.isNotNull = function (x) { return x !== null; };

    /**
    * Exception object raised if invalid data is passed.
    * @constructor.
    * @param {string} message - The exception detail message.
    */
    var InvalidData = function (message) {
        this.name = "InvalidData";
        this.message = message;
    };

    /**
    * Returns a string representation of this exception.
    * @returns {String} String representation.
    */
    InvalidData.prototype.toString = function () {
        return this.name + ": " + this.message;
    };

    /**
    * Utility function to throw an 'InvalidData' exception object.
    * @param {string} message - The exception message.
    * @throws {InvalidData} if invoked.
    */
    SplitsBrowser.throwInvalidData = function (message) {
        throw new InvalidData(message);
    };
    
    /**
    * Exception object raised if a data parser for a format deems that the data
    * given is not of that format.
    * @constructor
    * @param {String} message - The exception message.
    */
    var WrongFileFormat = function (message) {
        this.name = "WrongFileFormat";
        this.message = message;
    };
    
    /**
    * Returns a string representation of this exception.
    * @returns {String} String representation.
    */
    WrongFileFormat.prototype.toString = function () {
        return this.name + ": " + this.message;
    };
    
    /**
    * Utility funciton to throw a 'WrongFileFormat' exception object.
    * @param {string} message - The exception message.
    * @throws {WrongFileFormat} if invoked.
    */
    SplitsBrowser.throwWrongFileFormat = function (message) {
        throw new WrongFileFormat(message);
    };
    
    /**
    * Parses a course length.
    *
    * This can be specified as a decimal number of kilometres or metres, with
    * either a full stop or a comma as the decimal separator.
    *
    * @param {String} stringValue - The course length to parse, as a string.
    * @return {Number} The parsed course length.
    */
    SplitsBrowser.parseCourseLength = function (stringValue) {
        var courseLength = parseFloat(stringValue.replace(",", "."));
        if (courseLength >= MIN_COURSE_LENGTH_METRES) {
            courseLength /= 1000;
        }
        
        return courseLength;
    };
    
})();


(function () {
    "use strict";

    SplitsBrowser.NULL_TIME_PLACEHOLDER = "-----";
    
    /**
    * Formats a time period given as a number of seconds as a string in the form
    *  [-][h:]mm:ss.
    * @param {Number} seconds - The number of seconds.
    * @returns {string} The string formatting of the time.
    */
    SplitsBrowser.formatTime = function (seconds) {
        
        if (seconds === null) {
            return SplitsBrowser.NULL_TIME_PLACEHOLDER;
        }
    
        var result = "";
        if (seconds < 0) {
            result = "-";
            seconds = -seconds;
        }
        
        var hours = Math.floor(seconds / (60 * 60));
        var mins = Math.floor(seconds / 60) % 60;
        var secs = seconds % 60;
        if (hours > 0) {
            result += hours.toString() + ":";
        }
        
        if (mins < 10) {
            result += "0";
        }
        
        result += mins + ":";
        
        if (secs < 10) {
            result += "0";
        }
        
        result += Math.round(secs);
        
        return result;
    };
    
    /**  
    * Parse a time of the form MM:SS or H:MM:SS into a number of seconds.
    * @param {string} time - The time of the form MM:SS.
    * @return {Number} The number of seconds.
    */
    SplitsBrowser.parseTime = function (time) {
        if (time.match(/^\d+:\d\d$/)) {
            return parseInt(time.substring(0, time.length - 3), 10) * 60 + parseInt(time.substring(time.length - 2), 10);
        } else if (time.match(/^\d+:\d\d:\d\d$/)) {
            return parseInt(time.substring(0, time.length - 6), 10) * 3600 + parseInt(time.substring(time.length - 5, time.length - 3), 10) * 60 + parseInt(time.substring(time.length - 2), 10);
        } else {
            // Assume anything unrecognised is a missed split.
            return null;
        }
    };
})();

(function () {
    "use strict";

    var NUMBER_TYPE = typeof 0;
    
    var isNotNull = SplitsBrowser.isNotNull;
    var throwInvalidData = SplitsBrowser.throwInvalidData;
    var getMessage = SplitsBrowser.getMessage;

    /**
    * Function used with the JavaScript sort method to sort competitors in order
    * by finishing time.
    * 
    * Competitors that mispunch are sorted to the end of the list.
    * 
    * The return value of this method will be:
    * (1) a negative number if competitor a comes before competitor b,
    * (2) a positive number if competitor a comes after competitor a,
    * (3) zero if the order of a and b makes no difference (i.e. they have the
    *     same total time, or both mispunched.)
    * 
    * @param {SplitsBrowser.Model.Competitor} a - One competitor to compare.
    * @param {SplitsBrowser.Model.Competitor} b - The other competitor to compare.
    * @returns {Number} Result of comparing two competitors.  TH
    */
    SplitsBrowser.Model.compareCompetitors = function (a, b) {
        if (a.totalTime === b.totalTime) {
            return a.order - b.order;
        } else if (a.totalTime === null) {
            return (b.totalTime === null) ? 0 : 1;
        } else {
            return (b.totalTime === null) ? -1 : a.totalTime - b.totalTime;
        }
    };
    
    /**
    * Returns the sum of two numbers, or null if either is null.
    * @param {Number|null} a - One number, or null, to add.
    * @param {Number|null} b - The other number, or null, to add.
    * @return {Number|null} null if at least one of a or b is null,
    *      otherwise a + b.
    */
    function addIfNotNull(a, b) {
        return (a === null || b === null) ? null : (a + b);
    }
    
    /**
    * Returns the difference of two numbers, or null if either is null.
    * @param {Number|null} a - One number, or null, to add.
    * @param {Number|null} b - The other number, or null, to add.
    * @return {Number|null} null if at least one of a or b is null,
    *      otherwise a - b.
    */    
    function subtractIfNotNull(a, b) {
        return (a === null || b === null) ? null : (a - b);
    }
    
    /**
    * Convert an array of split times into an array of cumulative times.
    * If any null splits are given, all cumulative splits from that time
    * onwards are null also.
    *
    * The returned array of cumulative split times includes a zero value for
    * cumulative time at the start.
    * @param {Array} splitTimes - Array of split times.
    * @return {Array} Corresponding array of cumulative split times.
    */
    function cumTimesFromSplitTimes(splitTimes) {
        if (!$.isArray(splitTimes)) {
            throw new TypeError("Split times must be an array - got " + typeof splitTimes + " instead");
        } else if (splitTimes.length === 0) {
            throwInvalidData("Array of split times must not be empty");
        }
        
        var cumTimes = [0];
        for (var i = 0; i < splitTimes.length; i += 1) {
            cumTimes.push(addIfNotNull(cumTimes[i], splitTimes[i]));
        }

        return cumTimes;
    }
    
    /**
    * Convert an array of cumulative times into an array of split times.
    * If any null cumulative splits are given, the split times to and from that
    * control are null also.
    *
    * The input array should begin with a zero, for the cumulative time to the
    * start.
    * @param {Array} cumTimes - Array of cumulative split times.
    * @return {Array} Corresponding array of split times.
    */
    function splitTimesFromCumTimes(cumTimes) {
        if (!$.isArray(cumTimes)) {
            throw new TypeError("Cumulative times must be an array - got " + typeof cumTimes + " instead");
        } else if (cumTimes.length === 0) {
            throwInvalidData("Array of cumulative times must not be empty");
        } else if (cumTimes[0] !== 0) {
            throwInvalidData("Array of cumulative times must have zero as its first item");
        } else if (cumTimes.length === 1) {
            throwInvalidData("Array of cumulative times must contain more than just a single zero");
        }
        
        var splitTimes = [];
        for (var i = 0; i + 1 < cumTimes.length; i += 1) {
            splitTimes.push(subtractIfNotNull(cumTimes[i + 1], cumTimes[i]));
        }
        
        return splitTimes;
    }

    /**
    * Object that represents the data for a single competitor.
    *
    * The first parameter (order) merely stores the order in which the competitor
    * appears in the given list of results.  Its sole use is to stabilise sorts of
    * competitors, as JavaScript's sort() method is not guaranteed to be a stable
    * sort.  However, it is not strictly the finishing order of the competitors,
    * as it has been known for them to be given not in the correct order.
    *
    * It is not recommended to use this constructor directly.  Instead, use one of
    * the factory methods fromSplitTimes or fromCumTimes to pass in either the
    * split or cumulative times and have the other calculated.
    *
    * @constructor
    * @param {Number} order - The position of the competitor within the list of results.
    * @param {String} name - The name of the competitor.
    * @param {String} club - The name of the competitor's club.
    * @param {String} startTime - The competitor's start time.
    * @param {Array} splitTimes - Array of split times, as numbers, with nulls for missed controls.
    * @param {Array} cumTimes - Array of cumulative split times, as numbers, with nulls for missed controls.
    */
    var Competitor = function (order, name, club, startTime, splitTimes, cumTimes) {

        if (typeof order !== NUMBER_TYPE) {
            throwInvalidData("Competitor order must be a number, got " + typeof order + " '" + order + "' instead");
        }

        this.order = order;
        this.name = name;
        this.club = club;
        this.startTime = startTime;
        this.isNonCompetitive = false;
        this.className = null;
        
        this.splitTimes = splitTimes;
        this.cumTimes = cumTimes;
        this.splitRanks = null;
        this.cumRanks = null;
        this.timeLosses = null;

        this.totalTime = (this.cumTimes.indexOf(null) > -1) ? null : this.cumTimes[this.cumTimes.length - 1];
    };
    
    /**
    * Marks this competitor as being non-competitive.
    */
    Competitor.prototype.setNonCompetitive = function () {
        this.isNonCompetitive = true;
    };
    
    /**
    * Sets the name of the class that the competitor belongs to.
    * @param {String} className - The name of the class.
    */
    Competitor.prototype.setClassName = function (className) {
        this.className = className;
    };
    
    /**
    * Create and return a Competitor object where the competitor's times are given
    * as a list of split times.
    *
    * The first parameter (order) merely stores the order in which the competitor
    * appears in the given list of results.  Its sole use is to stabilise sorts of
    * competitors, as JavaScript's sort() method is not guaranteed to be a stable
    * sort.  However, it is not strictly the finishing order of the competitors,
    * as it has been known for them to be given not in the correct order.
    *
    * @param {Number} order - The position of the competitor within the list of results.
    * @param {String} name - The name of the competitor.
    * @param {String} club - The name of the competitor's club.
    * @param {Number} startTime - The competitor's start time, as seconds past midnight.
    * @param {Array} splitTimes - Array of split times, as numbers, with nulls for missed controls.
    */
    Competitor.fromSplitTimes = function (order, name, club, startTime, splitTimes) {
        var cumTimes = cumTimesFromSplitTimes(splitTimes);
        return new Competitor(order, name, club, startTime, splitTimes, cumTimes);
    };
    
    /**
    * Create and return a Competitor object where the competitor's times are given
    * as a list of cumulative split times.
    *
    * The first parameter (order) merely stores the order in which the competitor
    * appears in the given list of results.  Its sole use is to stabilise sorts of
    * competitors, as JavaScript's sort() method is not guaranteed to be a stable
    * sort.  However, it is not strictly the finishing order of the competitors,
    * as it has been known for them to be given not in the correct order.
    *
    * @param {Number} order - The position of the competitor within the list of results.
    * @param {String} name - The name of the competitor.
    * @param {String} club - The name of the competitor's club.
    * @param {Number} startTime - The competitor's start time, as seconds past midnight.
    * @param {Array} cumTimes - Array of cumulative split times, as numbers, with nulls for missed controls.
    */
    Competitor.fromCumTimes = function (order, name, club, startTime, cumTimes) {
        var splitTimes = splitTimesFromCumTimes(cumTimes);
        return new Competitor(order, name, club, startTime, splitTimes, cumTimes);
    };
    
    /**
    * Returns whether this competitor completed the course.
    * @return {boolean} Whether the competitor completed the course.
    */
    Competitor.prototype.completed = function () {
        return this.totalTime !== null;
    };
    
    /**
    * Returns the 'suffix' to use with a competitor.
    * The suffix indicates whether they are non-competitive or a mispuncher.  If
    * they are neither, an empty string is returned.
    * @return Suffix.
    */
    Competitor.prototype.getSuffix = function () {
        if (this.completed()) {
            return (this.isNonCompetitive) ? getMessage("NonCompetitiveShort") : "";
        } else {
            return getMessage("MispunchedShort");
        }
    };
    
    /**
    * Returns the competitor's split to the given control.  If the control
    * index given is zero (i.e. the start), zero is returned.  If the
    * competitor has no time recorded for that control, null is returned.
    * @param {Number} controlIndex - Index of the control (0 = start).
    * @return {Number} The split time in seconds for the competitor to the
    *      given control.
    */
    Competitor.prototype.getSplitTimeTo = function (controlIndex) {
        return (controlIndex === 0) ? 0 : this.splitTimes[controlIndex - 1];
    };
    
    /**
    * Returns the competitor's cumulative split to the given control.  If the
    * control index given is zero (i.e. the start), zero is returned.   If the
    * competitor has no cumulative time recorded for that control, null is
    * returned.
    * @param {Number} controlIndex - Index of the control (0 = start).
    * @return {Number} The cumulative split time in seconds for the competitor
    *      to the given control.
    */
    Competitor.prototype.getCumulativeTimeTo = function (controlIndex) {
        return this.cumTimes[controlIndex];
    };
    
    /**
    * Returns the rank of the competitor's split to the given control.  If the
    * control index given is zero (i.e. the start), or if the competitor has no
    * time recorded for that control, null is returned.
    * @param {Number} controlIndex - Index of the control (0 = start).
    * @return {Number} The split time in seconds for the competitor to the
    *      given control.
    */
    Competitor.prototype.getSplitRankTo = function (controlIndex) {
        return (controlIndex === 0) ? null : this.splitRanks[controlIndex - 1];
    };
    
    /**
    * Returns the rank of the competitor's cumulative split to the given
    * control.  If the control index given is zero (i.e. the start), or if the
    * competitor has no time recorded for that control, null is returned.
    * @param {Number} controlIndex - Index of the control (0 = start).
    * @return {Number} The split time in seconds for the competitor to the
    *      given control.
    */
    Competitor.prototype.getCumulativeRankTo = function (controlIndex) {
        return (controlIndex === 0) ? null : this.cumRanks[controlIndex - 1];
    };
    
    /**
    * Returns the time loss of the competitor at the given control, or null if
    * time losses cannot be calculated for the competitor or have not yet been
    * calculated.
    * @param {Number} controlIndex - Index of the control.
    * @return {Number|null} Time loss in seconds, or null.
    */
    Competitor.prototype.getTimeLossAt = function (controlIndex) {
        return (controlIndex === 0 || this.timeLosses === null) ? null : this.timeLosses[controlIndex - 1];
    };
    
    /**
    * Returns all of the competitor's cumulative time splits.
    * @return {Array} The cumulative split times in seconds for the competitor.
    */
    Competitor.prototype.getAllCumulativeTimes = function () {
        return this.cumTimes;
    };
    
    /**
    * Returns whether this competitor is missing a start time.
    * 
    * The competitor is missing its start time if it doesn't have a start time
    * and it also has at least one split.  (A competitor that has no start time
    * and no splits either didn't start the race.)
    *
    * @return {boolean} True if the competitor doesn't have a start time, false
    *     if they do, or if they have no other splits.
    */
    Competitor.prototype.lacksStartTime = function () {
        return this.startTime === null && this.splitTimes.some(isNotNull);
    };
    
    /**
    * Sets the split and cumulative-split ranks for this competitor.
    * @param {Array} splitRanks - Array of split ranks for this competitor.
    * @param {Array} cumRanks - Array of cumulative-split ranks for this competitor.
    */
    Competitor.prototype.setSplitAndCumulativeRanks = function (splitRanks, cumRanks) {
        this.splitRanks = splitRanks;
        this.cumRanks = cumRanks;
    };

    /**
    * Return this competitor's cumulative times after being adjusted by a 'reference' competitor.
    * @param {Array} referenceCumTimes - The reference cumulative-split-time data to adjust by.
    * @return {Array} The array of adjusted data.
    */
    Competitor.prototype.getCumTimesAdjustedToReference = function (referenceCumTimes) {
        if (referenceCumTimes.length !== this.cumTimes.length) {
            throwInvalidData("Cannot adjust competitor times because the numbers of times are different (" + this.cumTimes.length + " and " + referenceCumTimes.length + ")");
        } else if (referenceCumTimes.indexOf(null) > -1) {
            throwInvalidData("Cannot adjust competitor times because a null value is in the reference data");
        }

        var adjustedTimes = this.cumTimes.map(function (time, idx) { return subtractIfNotNull(time, referenceCumTimes[idx]); });
        return adjustedTimes;
    };
    
    /**
    * Returns the cumulative times of this competitor with the start time added on.
    * @param {Array} referenceCumTimes - The reference cumulative-split-time data to adjust by.
    * @return {Array} The array of adjusted data.
    */
    Competitor.prototype.getCumTimesAdjustedToReferenceWithStartAdded = function (referenceCumTimes) {
        var adjustedTimes = this.getCumTimesAdjustedToReference(referenceCumTimes);
        var startTime = this.startTime;
        return adjustedTimes.map(function (adjTime) { return addIfNotNull(adjTime, startTime); });
    };
    
    /**
    * Returns an array of percentages that this competitor's splits were behind
    * those of a reference competitor.
    * @param {Array} referenceCumTimes - The reference cumulative split times
    * @return {Array} The array of percentages.
    */
    Competitor.prototype.getSplitPercentsBehindReferenceCumTimes = function (referenceCumTimes) {
        if (referenceCumTimes.length !== this.cumTimes.length) {
            throwInvalidData("Cannot determine percentages-behind because the numbers of times are different (" + this.cumTimes.length + " and " + referenceCumTimes.length + ")");
        } else if (referenceCumTimes.indexOf(null) > -1) {
            throwInvalidData("Cannot determine percentages-behind because a null value is in the reference data");
        }
        
        var percentsBehind = [0];
        this.splitTimes.forEach(function (splitTime, index) {
            if (splitTime === null) {
                percentsBehind.push(null);
            } else {
                var referenceSplit = referenceCumTimes[index + 1] - referenceCumTimes[index];
                percentsBehind.push(100 * (splitTime - referenceSplit) / referenceSplit);
            }
        });
        
        return percentsBehind;
    };
    
    /**
    * Determines the time losses for this competitor.
    * @param {Array} fastestSplitTimes - Array of fastest split times.
    */
    Competitor.prototype.determineTimeLosses = function (fastestSplitTimes) {
        if (this.completed()) {
            if (fastestSplitTimes.length !== this.splitTimes.length) {
                throwInvalidData("Cannot determine time loss of competitor with " + this.splitTimes.length + " split times using " + fastestSplitTimes.length + " fastest splits");
            } else if (fastestSplitTimes.indexOf(null) >= 0) {
                throwInvalidData("Cannot determine time loss of competitor when there is a null value in the fastest splits");
            }
            
            // We use the same algorithm for calculating time loss as the
            // original, with a simplification: we calculate split ratios
            // (split[i] / fastest[i]) rather than time loss rates
            // (split[i] - fastest[i])/fastest[i].  A control's split ratio
            // is its time loss rate plus 1.  Not subtracting one at the start
            // means that we then don't have to add it back on at the end.
            
            var splitRatios = this.splitTimes.map(function (splitTime, index) {
                return splitTime / fastestSplitTimes[index];
            });
            
            splitRatios.sort(d3.ascending);
            
            var medianSplitRatio;
            if (splitRatios.length % 2 === 1) {
                medianSplitRatio = splitRatios[(splitRatios.length - 1) / 2];
            } else {
                var midpt = splitRatios.length / 2;
                medianSplitRatio = (splitRatios[midpt - 1] + splitRatios[midpt]) / 2;
            }
            
            this.timeLosses = this.splitTimes.map(function (splitTime, index) {
                return Math.round(splitTime - fastestSplitTimes[index] * medianSplitRatio);
            });
        }
    };
    
    /**
    * Returns whether this competitor 'crosses' another.  Two competitors are
    * considered to have crossed if their chart lines on the Race Graph cross.
    * @param {Competitor} other - The competitor to compare against.
    * @return {Boolean} true if the competitors cross, false if they don't.
    */
    Competitor.prototype.crosses = function (other) {
        if (other.cumTimes.length !== this.cumTimes.length) {
            throwInvalidData("Two competitors with different numbers of controls cannot cross");
        }
        
        // We determine whether two competitors cross by keeping track of
        // whether this competitor is ahead of other at any point, and whether
        // this competitor is behind the other one.  If both, the competitors
        // cross.
        var beforeOther = false;
        var afterOther = false;
        
        for (var controlIdx = 0; controlIdx < this.cumTimes.length; controlIdx += 1) {
            if (this.cumTimes[controlIdx] !== null && other.cumTimes[controlIdx] !== null) {
                var thisTotalTime = this.startTime + this.cumTimes[controlIdx];
                var otherTotalTime = other.startTime + other.cumTimes[controlIdx];
                if (thisTotalTime < otherTotalTime) {
                    beforeOther = true;
                } else if (thisTotalTime > otherTotalTime) {
                    afterOther = true;
                }
            }
        }
         
        return beforeOther && afterOther;
    };
    
    SplitsBrowser.Model.Competitor = Competitor;
})();

(function (){
    "use strict";

    var throwInvalidData = SplitsBrowser.throwInvalidData;
    
    /**
     * Object that represents a collection of competitor data for a class.
     * @constructor.
     * @param {string} name - Name of the age class.
     * @param {Number} numControls - Number of controls.
     * @param {Array} competitors - Array of Competitor objects.
     */
    var AgeClass = function (name, numControls, competitors) {
        this.name = name;
        this.numControls = numControls;
        this.competitors = competitors;
        this.course = null;
        
        var fastestSplitTimes = d3.range(1, numControls + 2).map(function (controlIdx) {
            var splitRec = this.getFastestSplitTo(controlIdx);
            return (splitRec === null) ? null : splitRec.split;
        }, this);
        
        this.competitors.forEach(function (comp) {
            comp.setClassName(this.name);
            comp.determineTimeLosses(fastestSplitTimes);
        }, this);
    };
    
    /**
    * Returns whether this age-class is empty, i.e. has no competitors.
    * @return {boolean} True if this age class has no competitors, false if it
    *     has at least one competitor.
    */
    AgeClass.prototype.isEmpty = function () {
        return (this.competitors.length === 0);
    };
    
    /**
    * Sets the course that this age class belongs to.
    * @param {SplitsBrowser.Model.Course} course - The course this class belongs to.
    */
    AgeClass.prototype.setCourse = function (course) {
        this.course = course;
    };
    
    /**
    * Returns the controls that all competitors in this class failed to punch.
    *
    * @return {Array} Array of numbers of controls that all competitors in this
    *     class failed to punch.
    */
    AgeClass.prototype.getControlsWithNoSplits = function () {
        return d3.range(1, this.numControls + 1).filter(function (controlNum) {
            return this.competitors.every(function (competitor) { return competitor.getSplitTimeTo(controlNum) === null; });
        }, this);
    };
    
    /**
    * Returns the fastest split time recorded by competitors in this class.  If
    * no fastest split time is recorded (e.g. because all competitors
    * mispunched that control, or the class is empty), null is returned.
    * @param {Number} controlIdx - The index of the control to return the
    *      fastest split to.
    * @return {Object|null} Object containing the name and fastest split, or
    *      null if no split times for that control were recorded.
    */
    AgeClass.prototype.getFastestSplitTo = function (controlIdx) {
        if (typeof controlIdx !== "number" || controlIdx < 1 || controlIdx > this.numControls + 1) {
            throwInvalidData("Cannot return splits to leg '" + controlIdx + "' in a course with " + this.numControls + " control(s)");
        }
    
        var fastestSplit = null;
        var fastestCompetitor = null;
        this.competitors.forEach(function (comp) {
            var compSplit = comp.getSplitTimeTo(controlIdx);
            if (compSplit !== null) {
                if (fastestSplit === null || compSplit < fastestSplit) {
                    fastestSplit = compSplit;
                    fastestCompetitor = comp;
                }
            }
        });
        
        return (fastestSplit === null) ? null : {split: fastestSplit, name: fastestCompetitor.name};
    };
    
    /**
    * Returns all competitors that visited the control in the given time
    * interval.
    * @param {Number} controlNum - The number of the control, with 0 being the
    *     start, and this.numControls + 1 being the finish.
    * @param {Number} intervalStart - The start time of the interval, as
    *     seconds past midnight.
    * @param {Number} intervalEnd - The end time of the interval, as seconds
    *     past midnight.
    * @return {Array} Array of objects listing the name and start time of each
    *     competitor visiting the control within the given time interval.
    */
    AgeClass.prototype.getCompetitorsAtControlInTimeRange = function (controlNum, intervalStart, intervalEnd) {
        if (typeof controlNum !== "number" || isNaN(controlNum) || controlNum < 0 || controlNum > this.numControls + 1) {
            throwInvalidData("Control number must be a number between 0 and " + this.numControls + " inclusive");
        }
        
        var matchingCompetitors = [];
        this.competitors.forEach(function (comp) {
            var cumTime = comp.getCumulativeTimeTo(controlNum);
            if (cumTime !== null && comp.startTime !== null) {
                var actualTimeAtControl = cumTime + comp.startTime;
                if (intervalStart <= actualTimeAtControl && actualTimeAtControl <= intervalEnd) {
                    matchingCompetitors.push({name: comp.name, time: actualTimeAtControl});
                }
            }
        });
        
        return matchingCompetitors;
    };
    
    SplitsBrowser.Model.AgeClass = AgeClass;
})();

(function () {
    "use strict";
      
    var throwInvalidData = SplitsBrowser.throwInvalidData; 
    var compareCompetitors = SplitsBrowser.Model.compareCompetitors;
    
    /**
    * Utility function to merge the lists of all competitors in a number of age
    * classes.  All age classes must contain the same number of controls.
    * @param {Array} ageClasses - Array of AgeClass objects.
    */
    function mergeCompetitors(ageClasses) {
        if (ageClasses.length === 0) {
            throwInvalidData("Cannot create an AgeClassSet from an empty set of competitors");
        }
        
        var allCompetitors = [];
        var expectedControlCount = ageClasses[0].numControls;
        ageClasses.forEach(function (ageClass) {
            if (ageClass.numControls !== expectedControlCount) {
                throwInvalidData("Cannot merge age classes with " + expectedControlCount + " and " + ageClass.numControls + " controls");
            }
            
            ageClass.competitors.forEach(function (comp) { allCompetitors.push(comp); });
        });

        allCompetitors.sort(compareCompetitors);
        return allCompetitors;
    }

    /**
    * Given an array of numbers, return a list of the corresponding ranks of those
    * numbers.
    * @param {Array} sourceData - Array of number values.
    * @returns Array of corresponding ranks.
    */
    function getRanks(sourceData) {
        // First, sort the source data, removing nulls.
        var sortedData = sourceData.filter(function (x) { return x !== null; });
        sortedData.sort(d3.ascending);
        
        // Now construct a map that maps from source value to rank.
        var rankMap = new d3.map();
        sortedData.forEach(function(value, index) {
            if (!rankMap.has(value)) {
                rankMap.set(value, index + 1);
            }
        });
        
        // Finally, build and return the list of ranks.
        var ranks = sourceData.map(function(value) {
            return (value === null) ? null : rankMap.get(value);
        });
        
        return ranks;
    }
    
    /**
    * An object that represents the currently-selected age classes.
    * @constructor
    * @param {Array} ageClasses - Array of currently-selected age classes.
    */
    var AgeClassSet = function (ageClasses) {
        this.allCompetitors = mergeCompetitors(ageClasses);
        this.ageClasses = ageClasses;
        this.numControls = ageClasses[0].numControls;
        this.computeRanks();
    };
    
    /**
    * Returns whether this age-class set is empty, i.e. whether it has no
    * competitors at all.
    */    
    AgeClassSet.prototype.isEmpty = function () {
        return this.allCompetitors.length === 0;
    };
    
    /**
    * Returns the course used by all of the age classes that make up this set.
    * @return {SplitsBrowser.Model.Course} The course used by all age-classes.
    */
    AgeClassSet.prototype.getCourse = function () {
        return this.ageClasses[0].course;
    };
    
    /**
    * Returns the name of the 'primary' age class, i.e. that that has been
    * chosen in the drop-down list.
    * @return {String} Name of the primary age class.
    */
    AgeClassSet.prototype.getPrimaryClassName = function () {
        return this.ageClasses[0].name;
    };
    
    /**
    * Returns the number of age classes that this age-class set is made up of.
    * @return {Number} The number of age classes that this age-class set is
    *     made up of.
    */
    AgeClassSet.prototype.getNumClasses = function () {
        return this.ageClasses.length;
    };
    
    /**
    * Returns an array of the cumulative times of the winner of the set of age
    * classes.
    * @return {Array} Array of the winner's cumulative times.
    */
    AgeClassSet.prototype.getWinnerCumTimes = function () {
        if (this.allCompetitors.length === 0) {
            return null;
        }
        
        var firstCompetitor = this.allCompetitors[0];
        return (firstCompetitor.completed()) ? firstCompetitor.cumTimes : null;
    };

    /**
    * Return the imaginary competitor who recorded the fastest time on each leg
    * of the class.
    * If at least one control has no competitors recording a time for it, null
    * is returned.
    * @returns {Array|null} Cumulative splits of the imaginary competitor with
    *           fastest time, if any.
    */
    AgeClassSet.prototype.getFastestCumTimes = function () {
        return this.getFastestCumTimesPlusPercentage(0);
    };

    /**
    * Returns an array of controls that no competitor in any of the age-classes
    * in this set punched.
    * @return {Array} Array of control numbers of controls that no competitor
    *     punched.
    */
    AgeClassSet.prototype.getControlsWithNoSplits = function () {
        var controlsWithNoSplits = this.ageClasses[0].getControlsWithNoSplits();
        for (var classIndex = 1; classIndex < this.ageClasses.length && controlsWithNoSplits.length > 0; classIndex += 1) {
            var thisClassControlsWithNoSplits = this.ageClasses[classIndex].getControlsWithNoSplits();
            
            var controlIdx = 0;
            while (controlIdx < controlsWithNoSplits.length) {
                if (thisClassControlsWithNoSplits.indexOf(controlsWithNoSplits[controlIdx]) >= 0) {
                    controlIdx += 1;
                } else {
                    controlsWithNoSplits.splice(controlIdx, 1);
                }
            }
        }
        
        return controlsWithNoSplits;
    };

    /**
    * Return the imaginary competitor who recorded the fastest time on each leg
    * of the given classes, with a given percentage of their time added.
    * If at least one control has no competitors recording a time for it, null
    * is returned.
    * @param {Number} percent - The percentage of time to add.
    * @returns {Array|null} Cumulative splits of the imaginary competitor with
    *           fastest time, if any, after adding a percentage.
    */
    AgeClassSet.prototype.getFastestCumTimesPlusPercentage = function (percent) {
        var ratio = 1 + percent / 100;
        var fastestCumTimes = new Array(this.numControls + 1);
        fastestCumTimes[0] = 0;
        for (var controlIdx = 1; controlIdx <= this.numControls + 1; controlIdx += 1) {
            var fastestForThisControl = null;
            for (var competitorIdx = 0; competitorIdx < this.allCompetitors.length; competitorIdx += 1) {
                var thisTime = this.allCompetitors[competitorIdx].getSplitTimeTo(controlIdx);
                if (thisTime !== null && (fastestForThisControl === null || thisTime < fastestForThisControl)) {
                    fastestForThisControl = thisTime;
                }
            }
            
            if (fastestForThisControl === null) {
                // No fastest time recorded for this control.
                return null;
            } else {
                fastestCumTimes[controlIdx] = fastestCumTimes[controlIdx - 1] + fastestForThisControl * ratio;
            }
        }

        return fastestCumTimes;
    };
    
    /**
    * Compute the ranks of each competitor within their class.
    */
    AgeClassSet.prototype.computeRanks = function () {
        var splitRanksByCompetitor = [];
        var cumRanksByCompetitor = [];
        
        this.allCompetitors.forEach(function () {
            splitRanksByCompetitor.push([]);
            cumRanksByCompetitor.push([]);
        });
        
        d3.range(1, this.numControls + 2).forEach(function (control) {
            var splitsByCompetitor = this.allCompetitors.map(function(comp) { return comp.getSplitTimeTo(control); });
            var splitRanksForThisControl = getRanks(splitsByCompetitor);
            this.allCompetitors.forEach(function (_comp, idx) { splitRanksByCompetitor[idx].push(splitRanksForThisControl[idx]); });
        }, this);
        
        d3.range(1, this.numControls + 2).forEach(function (control) {
            // We want to null out all subsequent cumulative ranks after a
            // competitor mispunches.
            var cumSplitsByCompetitor = this.allCompetitors.map(function (comp, idx) {
                // -1 for previous control, another -1 because the cumulative
                // time to control N is cumRanksByCompetitor[idx][N - 1].
                if (control > 1 && cumRanksByCompetitor[idx][control - 1 - 1] === null) {
                    // This competitor has no cumulative rank for the previous
                    // control, so either they mispunched it or mispunched a
                    // previous one.  Give them a null time here, so that they
                    // end up with another null cumulative rank.
                    return null;
                } else {
                    return comp.getCumulativeTimeTo(control);
                }
            });
            var cumRanksForThisControl = getRanks(cumSplitsByCompetitor);
            this.allCompetitors.forEach(function (_comp, idx) { cumRanksByCompetitor[idx].push(cumRanksForThisControl[idx]); });
        }, this);
        
        this.allCompetitors.forEach(function (comp, idx) {
            comp.setSplitAndCumulativeRanks(splitRanksByCompetitor[idx], cumRanksByCompetitor[idx]);
        });
    };
    
    /**
    * Returns the best few splits to a given control.
    *
    * The number of splits returned may actually be fewer than that asked for,
    * if there are fewer than that number of people on the class or who punch
    * the control.
    *
    * The results are returned in an array of 2-element arrays, with each child
    * array containing the split time and the name.  The array is returned in
    * ascending order of split time.
    *
    * @param {Number} numSplits - Maximum number of split times to return.
    * @param {Number} controlIdx - Index of the control.
    * @return {Array} Array of the fastest splits to the given control.
    */
    AgeClassSet.prototype.getFastestSplitsTo = function (numSplits, controlIdx) {
        if (typeof numSplits !== "number" || numSplits <= 0) {
            throwInvalidData("The number of splits must be a positive integer");
        } else if (typeof controlIdx !== "number" || controlIdx <= 0 || controlIdx > this.numControls + 1) {
            throwInvalidData("Control " + controlIdx + " out of range");
        } else {
            // Compare competitors by split time at this control, and, if those
            // are equal, total time.
            var comparator = function (compA, compB) {
                var compASplit = compA.getSplitTimeTo(controlIdx);
                var compBSplit = compB.getSplitTimeTo(controlIdx);
                return (compASplit === compBSplit) ? d3.ascending(compA.totalTime, compB.totalTime) : d3.ascending(compASplit, compBSplit);
            };
            
            var competitors = this.allCompetitors.filter(function (comp) { return comp.completed(); });
            competitors.sort(comparator);
            var results = [];
            for (var i = 0; i < competitors.length && i < numSplits; i += 1) {
                results.push({name: competitors[i].name, split: competitors[i].getSplitTimeTo(controlIdx)});
            }
            
            return results;
        }
    };    

    /**
    * Return data from the current classes in a form suitable for plotting in a chart.
    * @param {Array} referenceCumTimes - 'Reference' cumulative time data, such
    *            as that of the winner, or the fastest time.
    * @param {Array} currentIndexes - Array of indexes that indicate which
    *           competitors from the overall list are plotted.
    * @param {Object} chartType - The type of chart to draw.
    * @returns {Array} Array of data.
    */
    AgeClassSet.prototype.getChartData = function (referenceCumTimes, currentIndexes, chartType) {
        if (this.isEmpty()) {
            throwInvalidData("Cannot return chart data when there is no data");
        } else if (typeof referenceCumTimes === "undefined") {
            throw new TypeError("referenceCumTimes undefined or missing");
        } else if (typeof currentIndexes === "undefined") {
            throw new TypeError("currentIndexes undefined or missing");
        } else if (typeof chartType === "undefined") {
            throw new TypeError("chartType undefined or missing");
        }

        var competitorData = this.allCompetitors.map(function (comp) { return chartType.dataSelector(comp, referenceCumTimes); });
        var selectedCompetitorData = currentIndexes.map(function (index) { return competitorData[index]; });

        var xMax = referenceCumTimes[referenceCumTimes.length - 1];
        var yMin;
        var yMax;
        if (currentIndexes.length === 0) {
            // No competitors selected.  Set yMin and yMax to the boundary
            // values of the first competitor.
            var firstCompetitorTimes = competitorData[0];
            yMin = d3.min(firstCompetitorTimes);
            yMax = d3.max(firstCompetitorTimes);
        } else {
            yMin = d3.min(selectedCompetitorData.map(function (values) { return d3.min(values); }));
            yMax = d3.max(selectedCompetitorData.map(function (values) { return d3.max(values); }));
        }

        if (yMax === yMin) {
            // yMin and yMax will be used to scale a y-axis, so we'd better
            // make sure that they're not equal.
            yMax = yMin + 1;
        }

        var cumulativeTimesByControl = d3.transpose(selectedCompetitorData);
        var xData = (chartType.skipStart) ? referenceCumTimes.slice(1) : referenceCumTimes;
        var zippedData = d3.zip(xData, cumulativeTimesByControl);
        var competitorNames = currentIndexes.map(function (index) { return this.allCompetitors[index].name; }, this);
        return {
            dataColumns: zippedData.map(function (data) { return { x: data[0], ys: data[1] }; }),
            competitorNames: competitorNames,
            numControls: this.numControls,
            xExtent: [0, xMax],
            yExtent: [yMin, yMax]
        };
    };
    
    SplitsBrowser.Model.AgeClassSet = AgeClassSet;
})();

(function () {
    "use strict";
    
    var throwInvalidData = SplitsBrowser.throwInvalidData;
    
    /**
    * A collection of 'classes', all runners within which ran the same physical
    * course.
    *
    * Course length and climb are both optional and can both be null.
    * @constructor
    * @param {String} name - The name of the course.
    * @param {Array} classes - Array of AgeClass objects comprising the course.
    * @param {Number|null} length - Length of the course, in kilometres.
    * @param {Number|null} climb - The course climb, in metres.
    * @param {Array|null} controls - Array of codes of the controls that make
    *     up this course.  This may be null if no such information is provided.
    */
    var Course = function (name, classes, length, climb, controls) {
        this.name = name;
        this.classes = classes;
        this.length = length;
        this.climb = climb;
        this.controls = controls;
    };
    
    /** 'Magic' control code that represents the start. */
    Course.START = "__START__";
    
    /** 'Magic' control code that represents the finish. */
    Course.FINISH = "__FINISH__";
    
    var START = Course.START;
    var FINISH = Course.FINISH;
    
    /**
    * Returns an array of the 'other' classes on this course.
    * @param {SplitsBrowser.Model.AgeClass} ageClass - An age class that should
    *     be on this course,
    * @return {Array} Array of other age classes.
    */
    Course.prototype.getOtherClasses = function (ageClass) {
        var otherClasses = this.classes.filter(function (cls) { return cls !== ageClass; });
        if (otherClasses.length === this.classes.length) {
            // Given class not found.
            throwInvalidData("Course.getOtherClasses: given class is not in this course");
        } else {
            return otherClasses;
        }
    };
    
    /**
    * Returns the number of age classes that use this course.
    * @return {Number} Number of age classes that use this course.
    */
    Course.prototype.getNumClasses = function () {
        return this.classes.length;
    };
    
    /**
    * Returns whether this course has control code data.
    * @return {boolean} true if this course has control codes, false if it does
    *     not.
    */
    Course.prototype.hasControls = function () {
        return (this.controls !== null);
    };
    
    /**
    * Returns the code of the control at the given number.
    *
    * The start is control number 0 and the finish has number one more than the
    * number of controls.  Numbers outside this range are invalid and cause an
    * exception to be thrown.
    *
    * The codes for the start and finish are given by the constants
    * SplitsBrowser.Model.Course.START and SplitsBrowser.Model.Course.FINISH.
    *
    * @param {Number} controlNum - The number of the control.
    * @return {String|null} The code of the control, or one of the
    *     aforementioned constants for the start or finish.
    */
    Course.prototype.getControlCode = function (controlNum) {
        if (controlNum === 0) {
            // The start.
            return START;
        } else if (1 <= controlNum && controlNum <= this.controls.length) {
            return this.controls[controlNum - 1];
        } else if (controlNum === this.controls.length + 1) {
            // The finish.
            return FINISH;
        } else {
            throwInvalidData("Cannot get control code of control " + controlNum + " because it is out of range");
        }
    };
    
    /**
    * Returns whether this course uses the given leg.
    *
    * If this course lacks leg information, it is assumed not to contain any
    * legs and so will return false for every leg.
    *
    * @param {String} startCode - Code for the control at the start of the leg,
    *     or null for the start.
    * @param {String} endCode - Code for the control at the end of the leg, or
    *     null for the finish.
    * @return {boolean} Whether this course uses the given leg.
    */
    Course.prototype.usesLeg = function (startCode, endCode) {
        return this.getLegNumber(startCode, endCode) >= 0;
    };
    
    /**
    * Returns the number of a leg in this course, given the start and end
    * control codes.
    *
    * The number of a leg is the number of the end control (so the leg from
    * control 3 to control 4 is leg number 4.)  The number of the finish
    * control is one more than the number of controls.
    *
    * A negative number is returned if this course does not contain this leg.
    *
    * @param {String} startCode - Code for the control at the start of the leg,
    *     or null for the start.
    * @param {String} endCode - Code for the control at the end of the leg, or
    *     null for the finish.
    * @return {Number} The control number of the leg in this course, or a
    *     negative number if the leg is not part of this course.
    */
    Course.prototype.getLegNumber = function (startCode, endCode) {
        if (this.controls === null) {
            // No controls, so no, it doesn't contain the leg specified.
            return -1;
        }
        
        if (startCode === null && endCode === null) {
            // No controls - straight from the start to the finish.
            // This leg is only present, and is leg 1, if there are no
            // controls.
            return (this.controls.length === 0) ? 1 : -1;
        } else if (startCode === START) {
            // From the start to control 1.
            return (this.controls.length > 0 && this.controls[0] === endCode) ? 1 : -1;
        } else if (endCode === FINISH) {
            return (this.controls.length > 0 && this.controls[this.controls.length - 1] === startCode) ? (this.controls.length + 1) : -1;
        } else {
            for (var controlIdx = 1; controlIdx < this.controls.length; controlIdx += 1) {
                if (this.controls[controlIdx - 1] === startCode && this.controls[controlIdx] === endCode) {
                    return controlIdx + 1;
                }
            }
            
            // If we get here, the given leg is not part of this course.
            return -1;
        }
    };
    
    /**
    * Returns the fastest splits recorded for a given leg of the course.
    *
    * Note that this method should only be called if the course is known to use
    * the given leg.
    *
    * @param {String} startCode - Code for the control at the start of the leg,
    *     or SplitsBrowser.Model.Course.START for the start.
    * @param {String} endCode - Code for the control at the end of the leg, or
    *     SplitsBrowser.Model.Course.FINISH for the finish.
    * @return {Array} Array of fastest splits for each age class using this
    *      course.
    */
    Course.prototype.getFastestSplitsForLeg = function (startCode, endCode) {
        if (this.legs === null) {
            throwInvalidData("Cannot determine fastest splits for a leg because leg information is not available");
        }
        
        var legNumber = this.getLegNumber(startCode, endCode);
        if (legNumber < 0) {
            var legStr = ((startCode === START) ? "start" : startCode) + " to " + ((endCode === FINISH) ? "end" : endCode);
            throwInvalidData("Leg from " +  legStr + " not found in course " + this.name);
        }
        
        var controlNum = legNumber;
        var fastestSplits = [];
        this.classes.forEach(function (ageClass) {
            var classFastest = ageClass.getFastestSplitTo(controlNum);
            if (classFastest !== null) {
                fastestSplits.push({name: classFastest.name, className: ageClass.name, split: classFastest.split});
            }
        });
        
        return fastestSplits;
    };
    
    /**
    * Returns a list of all competitors on this course that visit the control
    * with the given code in the time interval given.
    *
    * Specify SplitsBrowser.Model.Course.START for the start and
    * SplitsBrowser.Model.Course.FINISH for the finish.
    *
    * If the given control is not on this course, an empty list is returned.
    *
    * @param {String} controlCode - Control code of the required control.
    * @param {Number} intervalStart - The start of the interval, as seconds
    *     past midnight.
    * @param {Number} intervalEnd - The end of the interval, as seconds past
    *     midnight.
    * @return  {Array} Array of all competitors visiting the given control
    *     within the given time interval.
    */
    Course.prototype.getCompetitorsAtControlInTimeRange = function (controlCode, intervalStart, intervalEnd) {
        if (this.controls === null) {
            // No controls means don't return any competitors.
            return [];
        } else if (controlCode === START) {
            return this.getCompetitorsAtControlNumInTimeRange(0, intervalStart, intervalEnd);
        } else if (controlCode === FINISH) {
            return this.getCompetitorsAtControlNumInTimeRange(this.controls.length + 1, intervalStart, intervalEnd);
        } else {
            var controlIdx = this.controls.indexOf(controlCode);
            if (controlIdx >= 0) {
                return this.getCompetitorsAtControlNumInTimeRange(controlIdx + 1, intervalStart, intervalEnd);
            } else {
                // Control not in this course.
                return [];
            }
        }
    };
    
    /**
    * Returns a list of all competitors on this course that visit the control
    * with the given number in the time interval given.
    *
    * @param {Number} controlNum - The number of the control (0 = start).
    * @param {Number} intervalStart - The start of the interval, as seconds
    *     past midnight.
    * @param {Number} intervalEnd - The end of the interval, as seconds past
    *     midnight.
    * @return  {Array} Array of all competitors visiting the given control
    *     within the given time interval.
    */
    Course.prototype.getCompetitorsAtControlNumInTimeRange = function (controlNum, intervalStart, intervalEnd) {
        var matchingCompetitors = [];
        this.classes.forEach(function (ageClass) {
            ageClass.getCompetitorsAtControlInTimeRange(controlNum, intervalStart, intervalEnd).forEach(function (comp) {
                matchingCompetitors.push({name: comp.name, time: comp.time, className: ageClass.name});
            });
        });
        
        return matchingCompetitors;
    };
    
    /**
    * Returns whether the course has the given control.
    * @param {String} controlCode - The code of the control.
    * @return {boolean} True if the course has the control, false if the
    *     course doesn't, or doesn't have any controls at all.
    */
    Course.prototype.hasControl = function (controlCode) {
        return this.controls !== null && this.controls.indexOf(controlCode) > -1;
    };
    
    /**
    * Returns the control code(s) of the control(s) after the one with the
    * given code.
    *
    * Controls can appear multiple times in a course.  If a control appears
    * multiple times, there will be multiple next controls.  As a result
    * @param {String} controlCode - The code of the control.
    * @return {Array} The code of the next control
    */
    Course.prototype.getNextControls = function (controlCode) {
        if (this.controls === null) {
            throwInvalidData("Course has no controls");
        } else if (controlCode === FINISH) {
            throwInvalidData("Cannot fetch next control after the finish");
        } else if (controlCode === START) {
            return [this.controls[0]];
        } else {
            var lastControlIdx = -1;
            var nextControls = [];
            do {
                var controlIdx = this.controls.indexOf(controlCode, lastControlIdx + 1);
                if (controlIdx === -1) {
                    break;
                } else if (controlIdx === this.controls.length - 1) {
                    nextControls.push(FINISH);
                } else {
                    nextControls.push(this.controls[controlIdx + 1]);
                }
                
                lastControlIdx = controlIdx;
            } while (true); // Loop exits when broken.
            
            if (nextControls.length === 0) {
                throwInvalidData("Control '" + controlCode + "' not found on course " + this.name);
            } else {
                return nextControls;
            }
        }
    };  
    
    SplitsBrowser.Model.Course = Course;
})();

(function () {
    "use strict";
    
    var Course = SplitsBrowser.Model.Course;
    
    /**
    * Contains all of the data for an event.
    * @param {Array} classes - Array of AgeClass objects representing all of
    *     the classes of competitors.
    * @param {Array} courses - Array of Course objects representing all of the
    *     courses of the event.
    */ 
    var Event = function (classes, courses) {
        this.classes = classes;
        this.courses = courses;
    };
    
    /**
    * Returns the fastest splits for each class on a given leg.
    *
    * The fastest splits are returned as an array of objects, where each object
    * lists the competitors name, the class, and the split time in seconds.
    *
    * @param {String} startCode - Code for the control at the start of the leg,
    *     or null for the start.
    * @param {String} endCode - Code for the control at the end of the leg, or
    *     null for the finish.
    * @return {Array} Array of objects containing fastest splits for that leg.
    */
    Event.prototype.getFastestSplitsForLeg = function (startCode, endCode) {
        var fastestSplits = [];
        this.courses.forEach(function (course) {
            if (course.usesLeg(startCode, endCode)) {
                fastestSplits = fastestSplits.concat(course.getFastestSplitsForLeg(startCode, endCode));
            }
        });
        
        fastestSplits.sort(function (a, b) { return d3.ascending(a.split, b.split); });
        
        return fastestSplits;
    };
    
    /**
    * Returns a list of competitors that visit the control with the given code
    * within the given time interval.
    *
    * The fastest splits are returned as an array of objects, where each object
    * lists the competitors name, the class, and the split time in seconds.
    *
    * @param {String} startCode - Code for the control at the start of the leg,
    *     or null for the start.
    * @param {String} endCode - Code for the control at the end of the leg, or
    *     null for the finish.
    * @return {Array} Array of objects containing fastest splits for that leg.
    */
    Event.prototype.getCompetitorsAtControlInTimeRange = function (controlCode, intervalStart, intervalEnd) {
        var competitors = [];
        this.courses.forEach(function (course) {
            course.getCompetitorsAtControlInTimeRange(controlCode, intervalStart, intervalEnd).forEach(function (comp) {
                competitors.push(comp);
            });
        });
        
        competitors.sort(function (a, b) { return d3.ascending(a.time, b.time); });
        
        return competitors;
    };
    
    /**
    * Returns the list of controls that follow after a given control.
    * @param {String} controlCode - The code for the control.
    * @return {Array} Array of objects for each course using that control,
    *    with each object listing course name and next control.
    */
    Event.prototype.getNextControlsAfter = function (controlCode) {
        var courses = this.courses;
        if (controlCode !== Course.START) {
            courses = courses.filter(function (course) { return course.hasControl(controlCode); });
        }
        
        return courses.map(function (course) { return {course: course, nextControls: course.getNextControls(controlCode)}; });
    };
    
    SplitsBrowser.Model.Event = Event;
})();

(function () {
    
    /**
    * Converts a number of seconds into the corresponding number of minutes.
    * This conversion is as simple as dividing by 60.
    * @param {Number} seconds - The number of seconds to convert.
    * @return {Number} The corresponding number of minutes.
    */
    function secondsToMinutes(seconds) { 
        return (seconds === null) ? null : seconds / 60;
    }

    SplitsBrowser.Model.ChartTypes = {
        SplitsGraph: {
            nameKey: "SplitsGraphChartType",
            dataSelector: function (comp, referenceCumTimes) { return comp.getCumTimesAdjustedToReference(referenceCumTimes).map(secondsToMinutes); },
            skipStart: false,
            yAxisLabelKey: "SplitsGraphYAxisLabel",
            isRaceGraph: false,
            isResultsTable: false,
            minViewableControl: 1
        },
        RaceGraph: {
            nameKey: "RaceGraphChartType",
            dataSelector: function (comp, referenceCumTimes) { return comp.getCumTimesAdjustedToReferenceWithStartAdded(referenceCumTimes).map(secondsToMinutes); },
            skipStart: false,
            yAxisLabelKey: "RaceGraphYAxisLabel",
            isRaceGraph: true,
            isResultsTable: false,
            minViewableControl: 0
        },
        PositionAfterLeg: {
            nameKey:  "PositionAfterLegChartType",
            dataSelector: function (comp) { return comp.cumRanks; },
            skipStart: true,
            yAxisLabelKey: "PositionYAxisLabel",
            isRaceGraph: false,
            isResultsTable: false,
            minViewableControl: 1
        },
        SplitPosition: {
            nameKey: "SplitPositionChartType",
            dataSelector: function (comp) { return comp.splitRanks; },
            skipStart: true,
            yAxisLabelKey: "PositionYAxisLabel",
            isRaceGraph: false,
            isResultsTable: false,
            minViewableControl: 1
        },
        PercentBehind: {
            nameKey: "PercentBehindChartType",
            dataSelector: function (comp, referenceCumTimes) { return comp.getSplitPercentsBehindReferenceCumTimes(referenceCumTimes); },
            skipStart: false,
            yAxisLabelKey: "PercentBehindYAxisLabel",
            isRaceGraph: false,
            isResultsTable: false,
            minViewableControl: 1
        },
        ResultsTable: {
            nameKey: "ResultsTableChartType",
            dataSelector: null,
            skipStart: false,
            yAxisLabelKey: null,
            isRaceGraph: false,
            isResultsTable: true,
            minViewableControl: 1
        }
    };
})();

(function (){
    "use strict";
    
    var NUMBER_TYPE = typeof 0;
    
    var throwInvalidData = SplitsBrowser.throwInvalidData;

    /**
    * Represents the currently-selected competitors, and offers a callback
    * mechanism for when the selection changes.
    * @constructor
    * @param {Number} count - The number of competitors that can be chosen.
    */
    var CompetitorSelection = function (count) {
        if (typeof count !== NUMBER_TYPE) {
            throwInvalidData("Competitor count must be a number");
        } else if (count < 0) {
            throwInvalidData("Competitor count must be a non-negative number");
        }

        this.count = count;
        this.currentIndexes = [];
        this.changeHandlers = [];
    };

    /**
    * Returns whether the competitor at the given index is selected.
    * @param {Number} index - The index of the competitor.
    * @returns {boolean} True if the competitor is selected, false if not.
    */
    CompetitorSelection.prototype.isSelected = function (index) {
        return this.currentIndexes.indexOf(index) > -1;
    };
    
    /**
    * Returns whether the selection consists of exactly one competitor.
    * @returns {boolean} True if precisely one competitor is selected, false if
    *     either no competitors, or two or more competitors, are selected.
    */
    CompetitorSelection.prototype.isSingleRunnerSelected = function () {
        return this.currentIndexes.length === 1;
    };

    /**
    * Given that a single runner is selected, select also all of the runners
    * that 'cross' this runner.
    * @param {Array} competitors - All competitors in the same class.
    */    
    CompetitorSelection.prototype.selectCrossingRunners = function (competitors) {
        if (this.isSingleRunnerSelected()) {
            var refCompetitor = competitors[this.currentIndexes[0]];
            
            competitors.forEach(function (comp, idx) {
                if (comp.crosses(refCompetitor)) {
                    this.currentIndexes.push(idx);
                }
            }, this);
            
            this.currentIndexes.sort(d3.ascending);
            this.fireChangeHandlers();
        }
    };
    
    /**
    * Fires all of the change handlers currently registered.
    */
    CompetitorSelection.prototype.fireChangeHandlers = function () {
        // Call slice(0) to return a copy of the list.
        this.changeHandlers.forEach(function (handler) { handler(this.currentIndexes.slice(0)); }, this);
    };

    /**
    * Select all of the competitors.
    */
    CompetitorSelection.prototype.selectAll = function () {
        this.currentIndexes = d3.range(this.count);
        this.fireChangeHandlers();
    };

    /**
    * Select none of the competitors.
    */
    CompetitorSelection.prototype.selectNone = function () {
        this.currentIndexes = [];
        this.fireChangeHandlers();
    };

    /**
    * Register a handler to be called whenever the list of indexes changes.
    *
    * When a change is made, this function will be called, with the array of
    * indexes being the only argument.  The array of indexes passed will be a
    * copy of that stored internally, so the handler is free to store this
    * array and/or modify it.
    *
    * If the handler has already been registered, nothing happens.
    *
    * @param {function} handler - The handler to register.
    */
    CompetitorSelection.prototype.registerChangeHandler = function (handler) {
        if (this.changeHandlers.indexOf(handler) === -1) {
            this.changeHandlers.push(handler);
        }
    };

    /**
    * Unregister a handler from being called when the list of indexes changes.
    *
    * If the handler given was never registered, nothing happens.
    *
    * @param {function} handler - The handler to register.
    */
    CompetitorSelection.prototype.deregisterChangeHandler = function (handler) {
        var index = this.changeHandlers.indexOf(handler);
        if (index > -1) {
            this.changeHandlers.splice(index, 1);
        }
    };

    /**
    * Toggles whether the competitor at the given index is selected.
    * @param {Number} index - The index of the competitor.
    */
    CompetitorSelection.prototype.toggle = function (index) {
        if (typeof index === NUMBER_TYPE) {
            if (0 <= index && index < this.count) {
                var position = this.currentIndexes.indexOf(index);
                if (position === -1) {
                    this.currentIndexes.push(index);
                    this.currentIndexes.sort(d3.ascending);
                } else {
                    this.currentIndexes.splice(position, 1);
                }

                this.fireChangeHandlers();
            } else {
                throwInvalidData("Index '" + index + "' is out of range");
            }
        } else {
            throwInvalidData("Index is not a number");
        }
    };
    
    /**
    * Migrates the selected competitors from one list to another.
    *
    * After the migration, any competitors in the old list that were selected
    * and are also in the new competitors list remain selected.
    *
    * @param {Array} oldCompetitors - Array of Competitor objects for the old
    *      selection.  The length of this must match the current count of
    *      competitors.
    * @param {Array} newCompetitors - Array of Competitor objects for the new
    *      selection.  This array must not be empty.
    */
    CompetitorSelection.prototype.migrate = function (oldCompetitors, newCompetitors) {
        if (!$.isArray(oldCompetitors)) {
            throwInvalidData("CompetitorSelection.migrate: oldCompetitors not an array");
        } else if (!$.isArray(newCompetitors)) {
            throwInvalidData("CompetitorSelection.migrate: newCompetitors not an array");
        } else if (oldCompetitors.length !== this.count) {
            throwInvalidData("CompetitorSelection.migrate: oldCompetitors list must have the same length as the current count"); 
        } else if (newCompetitors.length === 0) {
            throwInvalidData("CompetitorSelection.migrate: newCompetitors list must not be empty"); 
        }
    
        var selectedCompetitors = this.currentIndexes.map(function (index) { return oldCompetitors[index]; });
        
        this.count = newCompetitors.length;
        this.currentIndexes = [];
        newCompetitors.forEach(function (comp, idx) {
            if (selectedCompetitors.indexOf(comp) >= 0) {
                this.currentIndexes.push(idx);
            }
        }, this);
        
        this.fireChangeHandlers();
    };

    SplitsBrowser.Model.CompetitorSelection = CompetitorSelection;
})();


(function () {
    "use strict";
    
    var isTrue = SplitsBrowser.isTrue;
    var throwInvalidData = SplitsBrowser.throwInvalidData;
    var throwWrongFileFormat = SplitsBrowser.throwWrongFileFormat;
    var parseTime = SplitsBrowser.parseTime;
    var Competitor = SplitsBrowser.Model.Competitor;
    var compareCompetitors = SplitsBrowser.Model.compareCompetitors;
    var AgeClass = SplitsBrowser.Model.AgeClass;
    var Course = SplitsBrowser.Model.Course;
    var Event = SplitsBrowser.Model.Event;

    /**
    * Parse a row of competitor data.
    * @param {Number} index - Index of the competitor line.
    * @param {string} line - The line of competitor data read from a CSV file.
    * @param {Number} controlCount - The number of controls (not including the finish).
    * @return {Object} Competitor object representing the competitor data read in.
    */
    function parseCompetitors(index, line, controlCount) {
        // Expect forename, surname, club, start time then (controlCount + 1) split times in the form MM:SS.
        var parts = line.split(",");
        if (parts.length === controlCount + 5) {
            var forename = parts.shift();
            var surname = parts.shift();
            var club = parts.shift();
			
			var startTime = parts.shift()
			if(startTime.match(/^\d+:\d\d:\d\d$/)){ // support for seconds is start times for CSV format
				startTime = parseTime(startTime);
			}else{
				startTime = parseTime(startTime) * 60;
			}
            var splitTimes = parts.map(parseTime);
            if (splitTimes.indexOf(0) >= 0) {
                throwInvalidData("Zero split times are not permitted - found one or more zero splits for competitor '" + forename + " " + surname + "'");
            }
            return Competitor.fromSplitTimes(index + 1, forename + " " + surname, club, startTime, splitTimes);
        } else {
            throwInvalidData("Expected " + (controlCount + 5) + " items in row for competitor in class with " + controlCount + " controls, got " + (parts.length) + " instead.");
        }
    }

    /**
    * Parse CSV data for a class.
    * @param {string} class - The string containing data for that class.
    * @return {SplitsBrowser.Model.AgeClass} Parsed class data.
    */
    function parseAgeClass (ageClass) {
        var lines = ageClass.split(/\r?\n/).filter(isTrue);
        if (lines.length === 0) {
            throwInvalidData("parseAgeClass got an empty list of lines");
        }

        var firstLineParts = lines.shift().split(",");
        if (firstLineParts.length === 2) {
            var className = firstLineParts.shift();
            var controlCountStr = firstLineParts.shift();
            var controlCount = parseInt(controlCountStr, 10);
            if (isNaN(controlCount)) {
                throwInvalidData("Could not read control count: '" + controlCountStr + "'");
            } else if (controlCount < 0) {
                throwInvalidData("Expected a positive control count, got " + controlCount + " instead");
            } else {
                var competitors = lines.map(function (line, index) { return parseCompetitors(index, line, controlCount); });
                competitors.sort(compareCompetitors);
                return new AgeClass(className, controlCount, competitors);
            }
        } else {
            throwWrongFileFormat("Expected first line to have two parts (class name and number of controls), got " + firstLineParts.length + " part(s) instead");
        }
    }

    /**
    * Parse CSV data for an entire event.
    * @param {string} eventData - String containing the entire event data.
    * @return {SplitsBrowser.Model.Event} All event data read in.
    */
    function parseEventData (eventData) {
        var classSections = eventData.split(/\r?\n\r?\n/).map($.trim).filter(isTrue);
       
        var classes = classSections.map(parseAgeClass);
        
        classes = classes.filter(function (ageClass) { return !ageClass.isEmpty(); });
        
        if (classes.length === 0) {
            throwInvalidData("No competitor data was found");
        }
        
        // Nulls are for the course length, climb and controls, which aren't in
        // the source data files, so we can't do anything about them.
        var courses = classes.map(function (cls) { return new Course(cls.name, [cls], null, null, null); });
        
        for (var i = 0; i < classes.length; i += 1) {
            classes[i].setCourse(courses[i]);
        }
        
        return new Event(classes, courses);
    }
    
    SplitsBrowser.Input.CSV = { parseEventData: parseEventData };
})();


(function () {
    "use strict";
    
    var throwInvalidData = SplitsBrowser.throwInvalidData;
    var throwWrongFileFormat = SplitsBrowser.throwWrongFileFormat;
    var parseCourseLength = SplitsBrowser.parseCourseLength;
    var formatTime = SplitsBrowser.formatTime;
    var parseTime = SplitsBrowser.parseTime;
    var Competitor = SplitsBrowser.Model.Competitor;
    var AgeClass = SplitsBrowser.Model.AgeClass;
    var Course = SplitsBrowser.Model.Course;
    var Event = SplitsBrowser.Model.Event;
    
    // Indexes of the various columns relative to the column for control-1.
    var COLUMN_OFFSETS = {
        TIME: -35,
        CLUB: -31,
        AGE_CLASS: -28,
        COURSE: -7,
        DISTANCE: -6,
        CLIMB: -5,
        CONTROL_COUNT: -4,
        PLACING: -3,
        START: -2
    };
    
    // Minimum control offset.
    var MIN_CONTROLS_OFFSET = 37;
    
    /**
    * Checks that two consecutive cumulative times are in strictly ascending
    * order, and throws an exception if not.  The previous time should not be
    * null, but the next time may, and no exception will be thrown in this
    * case.
    * @param {Number} prevTime - The previous cumulative time, in seconds.
    * @param {Number} nextTime - The next cumulative time, in seconds.
    */
    function verifyCumulativeTimesInOrder(prevTime, nextTime) {
        if (nextTime !== null && nextTime <= prevTime) {
            throwInvalidData("Cumulative times must be strictly ascending: read " +
                    formatTime(prevTime) + " and " + formatTime(nextTime) +
                    " in that order");
        }
    }
    
    /**
    * Constructs an SI-format data reader.
    *
    * NOTE: The reader constructed can only be used to read data in once.
    * @constructor
    * @param {String} data - The SI data to read in.
    */
    var Reader = function (data) {
        this.data = data;
        
        // Map that associates classes to all of the competitors running on
        // that age class.
        this.ageClasses = d3.map();
        
        // Map that associates course names to length and climb values.
        this.courseDetails = d3.map();
        
        // Set of all pairs of classes and courses.
        // (While it is common that one course may have multiple classes, it
        // seems also that one class can be made up of multiple courses, e.g.
        // M21E at BOC 2013.)
        this.classCoursePairs = [];

        // Whether any competitors have been read in at all.  Blank lines are
        // ignored, as are competitors that have no times at all.
        this.anyCompetitors = false;
        
        // The column index that contains the control numbers for control 1.
        // This is used to determine where various columns are.
        this.control1Index = null;
    };

    /**
    * Checks that the data read in contains a header that suggests it is
    * SI-format data.
    */
    Reader.prototype.checkHeader = function() {
        if (this.lines.length <= 1) {
            throwWrongFileFormat("No data found to read");
        }
        
        var headers = this.lines[0].split(";");
        if (headers.length <= 1) {
            throwWrongFileFormat("Data appears not to be in the SI CSV format");
        }
        
        var firstLine = this.lines[1].split(";");
        
        var endPos = firstLine.length - 1;
        while (endPos > 0 && $.trim(firstLine[endPos]) === "") {
            endPos -= 1;
        }
        
        // The last empty item should be the time.
        var controlCodeColumn = endPos - 1;
        var digitsOnly = /^\d+$/;
        while (controlCodeColumn >= 2 && digitsOnly.test(firstLine[controlCodeColumn - 2])) { 
            // There's another control code before this one.
            controlCodeColumn -= 2;
        }
        
        this.control1Index = controlCodeColumn;
        
        var supportedControl1Indexes = [44, 46];
        if (this.control1Index === null) {
            throwInvalidData("Unable to find index of control 1 in SI CSV data");
        } else if (supportedControl1Indexes.indexOf(this.control1Index) < 0) {
            throwInvalidData("Unsupported index of control 1: " + this.control1Index);
        }
    };
    
    /**
    * Returns the number of controls to expect on the given line.
    * @param {Array} row - Array of row data items.
    * @param {Number} lineNumber - The line number of the line.
    * @return {Number} Number of controls read.
    */
    Reader.prototype.getNumControls = function (row, lineNumber) {
        var className = row[this.control1Index + COLUMN_OFFSETS.AGE_CLASS];
        if ($.trim(className) === "") {
            throwInvalidData("Line " + lineNumber + " does not contain a class for the competitor");
        } else if (this.ageClasses.has(className)) {
            return this.ageClasses.get(className).numControls;
        } else {
            return parseInt(row[this.control1Index + COLUMN_OFFSETS.CONTROL_COUNT], 10);
        }    
    };
    
    /**
    * Reads the split times out of a row of competitor data.
    * @param {Array} row - Array of row data items.
    * @param {Number} lineNumber - Line number of the row within the source data.
    * @param {Number} numControls - The number of controls to read.
    */
    Reader.prototype.readCumulativeTimes = function (row, lineNumber, numControls) {
        
        var cumTimes = [0];
        var lastCumTime = 0;
        
        for (var controlIdx = 0; controlIdx < numControls; controlIdx += 1) {
            var cellIndex = this.control1Index + 1 + 2 * controlIdx;
            var cumTime = (cellIndex < row.length) ? parseTime(row[cellIndex]) : null;
                
            verifyCumulativeTimesInOrder(lastCumTime, cumTime);
            
            cumTimes.push(cumTime);
            if (cumTime !== null) {
                lastCumTime = cumTime;
            }
        }
        
        var totalTime = parseTime(row[this.control1Index + COLUMN_OFFSETS.TIME]);
        verifyCumulativeTimesInOrder(lastCumTime, totalTime);
        cumTimes.push(totalTime);
    
        return cumTimes;
    };
    
    /**
    * Checks to see whether the given row contains a new age-class, and if so,
    * creates it.
    * @param {Array} row - Array of row data items.
    * @param {Number} numControls - The number of controls to read.
    */
    Reader.prototype.createAgeClassIfNecessary = function (row, numControls) {
        var className = row[this.control1Index + COLUMN_OFFSETS.AGE_CLASS];
        if (!this.ageClasses.has(className)) {
            this.ageClasses.set(className, { numControls: numControls, competitors: [] });
        }
    };
    
    /**
    * Checks to see whether the given row contains a new course, and if so,
    * creates it.
    * @param {Array} row - Array of row data items.
    * @param {Number} numControls - The number of controls to read.
    */
    Reader.prototype.createCourseIfNecessary = function (row, numControls) {

        var courseName = row[this.control1Index + COLUMN_OFFSETS.COURSE];
        if (!this.courseDetails.has(courseName)) {
            var controlNums = d3.range(0, numControls).map(function (controlIdx) { return row[this.control1Index + 2 * controlIdx]; }, this);
            this.courseDetails.set(courseName, {
                length: parseCourseLength(row[this.control1Index + COLUMN_OFFSETS.DISTANCE]) || null, 
                climb: parseInt(row[this.control1Index + COLUMN_OFFSETS.CLIMB], 10) || null,
                controls: controlNums
            });
        }
    };

    /**
    * Checks to see whether the given row contains a class-course pairing that
    * we haven't seen so far, and adds one if not.
    * @param {Array} row - Array of row data items.
    */
    Reader.prototype.createClassCoursePairIfNecessary = function (row) {
        var className = row[this.control1Index + COLUMN_OFFSETS.AGE_CLASS];
        var courseName = row[this.control1Index + COLUMN_OFFSETS.COURSE];
        
        if (!this.classCoursePairs.some(function (pair) { return pair[0] === className && pair[1] === courseName; })) {
            this.classCoursePairs.push([className, courseName]);
        }
    };
    
    /**
    * Reads in the competitor-specific data from the given row and adds it to
    * the event data read so far.
    * @param {Array} row - Row of items read from a line of the input data.
    * @param {Array} cumTimes - Array of cumulative times for the competitor.
    */
    Reader.prototype.addCompetitor = function (row, cumTimes) {
    
        var className = row[this.control1Index + COLUMN_OFFSETS.AGE_CLASS];
        var placing = row[this.control1Index + COLUMN_OFFSETS.PLACING];
        var club = row[this.control1Index + COLUMN_OFFSETS.CLUB];
        var startTime = parseTime(row[this.control1Index + COLUMN_OFFSETS.START]);

        var isPlacingNonNumeric = (placing !== "" && isNaN(parseInt(placing, 10)));
        
        var name;
        if (this.control1Index === 46) {
            var forename = row[4];
            var surname = row[3];
        
            // Some surnames have their placing appended to them, if their placing
            // isn't a number (e.g. mp, n/c).  If so, remove this.
            if (isPlacingNonNumeric && surname.substring(surname.length - placing.length) === placing) {
                surname = $.trim(surname.substring(0, surname.length - placing.length));
            }
            
            name = forename + " " + surname;
            
        } else if (this.control1Index === 44) {
            name = row[3];
        } else {
            // Reader should have thrown an error elsewhere if this has happened.
            throw new Error("Unrecognised control-1 index: " + this.control1Index);
        }
        
        var order = this.ageClasses.get(className).competitors.length + 1;
        var competitor = Competitor.fromCumTimes(order, name, club, startTime, cumTimes);
        if (isPlacingNonNumeric && competitor.completed()) {
            // Competitor has completed the course but has no placing.
            // Assume that they are non-competitive.
            competitor.setNonCompetitive();
        }

        this.ageClasses.get(className).competitors.push(competitor);
    };
    
    /**
    * Parses the given line and adds it to the event data accumulated so far.
    * @param {String} line - The line to parse.
    * @param {Number} lineNumber - The number of the line (used in error
    *     messages).
    */
    Reader.prototype.readLine = function (line, lineNumber) {
    
        if ($.trim(line) === "") {
            // Skip this blank line.
            return;
        }
    
        var row = line.split(";");
        
        // Check the row is long enough to have all the data besides the
        // controls data.
        if (row.length < MIN_CONTROLS_OFFSET) {
            throwInvalidData("Too few items on line " + lineNumber + " of the input file: expected at least " + MIN_CONTROLS_OFFSET + ", got " + row.length);
        }
        
        var numControls = this.getNumControls(row, lineNumber);
        
        var cumTimes = this.readCumulativeTimes(row, lineNumber, numControls);
        this.anyCompetitors = true;
        
        this.createAgeClassIfNecessary(row, numControls);
        this.createCourseIfNecessary(row, numControls);
        this.createClassCoursePairIfNecessary(row);
        
        this.addCompetitor(row, cumTimes);
    };
    
    /**
    * Creates maps that describe the many-to-many join between the class names
    * and course names. 
    * @return {Object} Object that contains two maps describing the
    *     many-to-many join.
    */    
    Reader.prototype.getMapsBetweenClassesAndCourses = function () {
        
        var classesToCourses = d3.map();
        var coursesToClasses = d3.map();
        
        this.classCoursePairs.forEach(function (pair) {
            var className = pair[0];
            var courseName = pair[1];
            
            if (classesToCourses.has(className)) {
                classesToCourses.get(className).push(courseName);
            } else {
                classesToCourses.set(className, [courseName]);
            }
            
            if (coursesToClasses.has(courseName)) {
                coursesToClasses.get(courseName).push(className);
            } else {
                coursesToClasses.set(courseName, [className]);
            }
        });
        
        return {classesToCourses: classesToCourses, coursesToClasses: coursesToClasses};
    };
    
    /**
    * Creates and return a list of AgeClass objects from all of the data read.
    * @return {Array} Array of AgeClass objects.
    */
    Reader.prototype.createAgeClasses = function () {
        var classNames = this.ageClasses.keys();
        classNames.sort();
        return classNames.map(function (className) {
            var ageClass = this.ageClasses.get(className);
            return new AgeClass(className, ageClass.numControls, ageClass.competitors);
        }, this);
    };
    
    /**
    * Find all of the courses and classes that are related to the given course.
    *
    * It's not always as simple as one course having multiple classes, as there
    * can be multiple courses for one single class, and even multiple courses
    * among multiple classes (e.g. M20E, M18E on courses 3, 3B at BOC 2013.)
    * Essentially, we have a many-to-many join, and we want to pull out of that
    * all of the classes and courses linked to the one course with the given
    * name.
    * 
    * (For the graph theorists among you, imagine the bipartite graph with
    * classes on one side and courses on the other.  We want to find the
    * connected subgraph that this course belongs to.)
    *
    * @param {String} initCourseName - The name of the initial course.
    * @param {Object} manyToManyMaps - Object that contains the two maps that
    *     map between class names and course names.
    * @param {d3.set} doneCourseNames - Set of all course names that have been
    *     'done', i.e. included in a Course object that has been returned from
    *     a call to this method.
    * @param {d3.map} classesMap - Map that maps age-class names to AgeClass
    *     objects.
    * @return {SplitsBrowser.Model.Course} - The created Course object.
    */
    Reader.prototype.createCourseFromLinkedClassesAndCourses = function (initCourseName, manyToManyMaps, doneCourseNames, classesMap) {

        var courseNamesToDo = [initCourseName];
        var classNamesToDo = [];
        var relatedCourseNames = [];
        var relatedClassNames = [];
        
        var courseName;
        var className;
        
        while (courseNamesToDo.length > 0 || classNamesToDo.length > 0) {
            while (courseNamesToDo.length > 0) {
                courseName = courseNamesToDo.shift();
                var classNames = manyToManyMaps.coursesToClasses.get(courseName);
                for (var clsIdx = 0; clsIdx < classNames.length; clsIdx += 1) {
                    className = classNames[clsIdx];
                    if (classNamesToDo.indexOf(className) < 0 && relatedClassNames.indexOf(className) < 0) {
                        classNamesToDo.push(className);
                    }
                }
                
                relatedCourseNames.push(courseName);
            }
            
            while (classNamesToDo.length > 0) {
                className = classNamesToDo.shift();
                var courseNames = manyToManyMaps.classesToCourses.get(className);
                for (var crsIdx = 0; crsIdx < courseNames.length; crsIdx += 1) {
                    courseName = courseNames[crsIdx];
                    if (courseNamesToDo.indexOf(courseName) < 0 && relatedCourseNames.indexOf(courseName) < 0) {
                        courseNamesToDo.push(courseName);
                    }
                }
                
                relatedClassNames.push(className);
            }
        }
        
        // Mark all of the courses that we handled here as done.
        relatedCourseNames.forEach(function (courseName) {
            doneCourseNames.add(courseName);
        });
        
        var courseClasses = relatedClassNames.map(function (className) { return classesMap.get(className); });
        var details = this.courseDetails.get(initCourseName);
        var course = new Course(initCourseName, courseClasses, details.length, details.climb, details.controls);
        
        courseClasses.forEach(function (ageClass) {
            ageClass.setCourse(course);
        });
        
        return course;
    };
    
    /**
    * Sort through the data read in and create Course objects representing each
    * course in the event.
    * @param {Array} classes - Array of AgeClass objects read.
    * @return {Array} Array of course objects.
    */
    Reader.prototype.determineCourses = function (classes) {
        
        var manyToManyMaps = this.getMapsBetweenClassesAndCourses();
        
        // As we work our way through the courses and classes, we may find one
        // class made up from multiple courses (e.g. in BOC2013, class M21E
        // uses course 1A and 1B).  In this set we collect up all of the
        // courses that we have now processed, so that if we later come across
        // one we've already dealt with, we can ignore it.
        var doneCourseNames = d3.set();
        
        var classesMap = d3.map();
        classes.forEach(function (ageClass) {
            classesMap.set(ageClass.name, ageClass);
        });
        
        // List of all Course objects created so far.
        var courses = [];
        manyToManyMaps.coursesToClasses.keys().forEach(function (courseName) {
            if (!doneCourseNames.has(courseName)) {
                var course = this.createCourseFromLinkedClassesAndCourses(courseName, manyToManyMaps, doneCourseNames, classesMap);
                courses.push(course);
            }
        }, this);
        
        return courses;
    };
    
    /**
    * Parses the read-in data and returns it.
    * @return {SplitsBrowser.Model.Event} Event-data read.
    */
    Reader.prototype.parseEventData = function () {
        
        this.lines = this.data.split(/\r?\n/);
        
        this.checkHeader();
        
        // Discard the header row.
        this.lines.shift();
        
        this.lines.forEach(function (line, lineIndex) {
            this.readLine(line, lineIndex + 1);
        }, this);
        
        if (!this.anyCompetitors) {
            throwInvalidData("No competitors' data were found");
        }
        
        var classes = this.createAgeClasses();
        var courses = this.determineCourses(classes);
        return new Event(classes, courses);
    };
    
    SplitsBrowser.Input.SI = {};
    
    /**
    * Parse 'SI' data read from a semicolon-separated data string.
    * @param {String} data - The input data string read.
    * @return {SplitsBrowser.Model.Event} All event data read.
    */
    SplitsBrowser.Input.SI.parseEventData = function (data) {
        var reader = new Reader(data);
        return reader.parseEventData();
    };
})();

(function () {
    "use strict";
    
    var isNotNull = SplitsBrowser.isNotNull;
    var throwInvalidData = SplitsBrowser.throwInvalidData;
    var throwWrongFileFormat = SplitsBrowser.throwWrongFileFormat;
    var parseCourseLength = SplitsBrowser.parseCourseLength;
    var formatTime = SplitsBrowser.formatTime;
    var parseTime = SplitsBrowser.parseTime;
    var Competitor = SplitsBrowser.Model.Competitor;
    var AgeClass = SplitsBrowser.Model.AgeClass;
    var Course = SplitsBrowser.Model.Course;
    var Event = SplitsBrowser.Model.Event;

    // Regexps to help with parsing.
    var HTML_TAG_STRIP_REGEXP = /<[^>]+>/g;
    var DISTANCE_FIND_REGEXP = /([0-9.,]+)\s*(?:Km|km)/;
    var CLIMB_FIND_REGEXP = /(\d+)\s*(?:Cm|Hm|hm|m)/;
    
    /**
    * Returns whether the given string is nonempty.
    * @param {String} string - The string to check.
    * @return True if the string is neither null nor empty, false if it is null
    *     or empty.
    */
    function isNonEmpty(string) {
        return string !== null && string !== "";
    }
    
    /**
    * Returns whether the given string contains a number.  The string is
    * considered to contain a number if, after stripping whitespace, the string
    * is not empty and calling isFinite on it returns true.
    * @param {String} string - The string to test.
    * @return True if the string contains a number, false if not.
    */
    function hasNumber(string) {
        string = $.trim(string);
        // isFinite is not enough on its own: isFinite("") is true.
        return string !== "" && isFinite(string);
    }
    
    /**
    * Splits a line by whitespace.
    * @param {String} line - The line to split.
    * @return {Array} Array of whitespace-separated strings.
    */ 
    function splitByWhitespace (line) {
        return line.split(/\s+/g).filter(isNonEmpty);
    }
    
    /**
    * Strips all HTML tags from a string and returns the remaining string.
    * @param {String} text - The HTML string to strip tags from.
    * @return {String} The input string with HTML tags removed.
    */
    function stripHtml(text) {
        return text.replace(HTML_TAG_STRIP_REGEXP, "");
    }
    
    /**
    * Returns all matches of the given regexp within the given text,
    * after being stripped of HTML.
    *
    * Note that it is recommended to pass this function a new regular
    * expression each time, rather than using a precompiled regexp.
    *
    * @param {RegExp} regexp - The regular expression to find all matches of.
    * @param {String} text - The text to search for matches within.
    * @return {Array} Array of strings representing the HTML-stripped regexp
    *     matches.
    */
    function getHtmlStrippedRegexMatches(regexp, text) {
        var matches = [];
        var match;
        while (true) {
            match = regexp.exec(text);
            if (match === null) {
                break;
            } else {
                matches.push(stripHtml(match[1]));
            }
        }
        
        return matches;
    }

    /**
    * Returns the contents of all <font> ... </font> elements within the given
    * text.  The contents of the <font> elements are stripped of all other HTML
    * tags.
    * @param {String} text - The HTML string containing the <font> elements.
    * @return {Array} Array of strings of text inside <font> elements.
    */
    function getFontBits(text) {
        return getHtmlStrippedRegexMatches(/<font[^>]*>(.*?)<\/font>/g, text);
    }
    
    /**
    * Returns the contents of all <td> ... </td> elements within the given
    * text.  The contents of the <td> elements are stripped of all other HTML
    * tags.
    * @param {String} text - The HTML string containing the <td> elements.
    * @return {Array} Array of strings of text inside <td> elements.
    */
    function getTableDataBits(text) {
        return getHtmlStrippedRegexMatches(/<td[^>]*>(.*?)<\/td>/g, text).map($.trim);
    }
    
    /**
    * Returns the contents of all <td> ... </td> elements within the given
    * text.  The contents of the <td> elements are stripped of all other HTML
    * tags.  Empty matches are removed.
    * @param {String} text - The HTML string containing the <td> elements.
    * @return {Array} Array of strings of text inside <td> elements.
    */
    function getNonEmptyTableDataBits(text) {
        return getTableDataBits(text).filter(function (bit) { return bit !== ""; });
    }
    
    /**
    * Returns the contents of all <th> ... </th> elements within the given
    * text.  The contents of the <th> elements are stripped of all other HTML
    * tags.  Empty matches are removed.
    * @param {String} text - The HTML string containing the <td> elements.
    * @return {Array} Array of strings of text inside <td> elements.
    */
    function getNonEmptyTableHeaderBits(text) {
        var matches = getHtmlStrippedRegexMatches(/<th[^>]*>(.*?)<\/th>/g, text);
        return matches.filter(function (bit) { return bit !== ""; });
    }
    
    /**
    * Attempts to read a course distance from the given string.
    * @param {String} text - The text string to read a course distance from.
    * @return {Number|null} - The parsed course distance, or null if no 
    *     distance could be parsed.
    */
    function tryReadDistance(text) {
        var distanceMatch = DISTANCE_FIND_REGEXP.exec(text);
        if (distanceMatch === null) {
            return null;
        } else {
            return parseCourseLength(distanceMatch[1]);
        }
    }
    
    /**
    * Attempts to read a course climb from the given string.
    * @param {String} text - The text string to read a course climb from.
    * @return {Number|null} - The parsed course climb, or null if no climb
    *     could be parsed.
    */
    function tryReadClimb(text) {
        var climbMatch = CLIMB_FIND_REGEXP.exec(text);
        if (climbMatch === null) {
            return null;
        } else {
            return parseInt(climbMatch[1], 10);
        }
    }
    
    /**
    * Reads control codes from an array of strings.  Each code should be of the
    * form num(code), with the exception of the finish, which, if it appears,
    * should contain no parentheses and must be the last.  The finish is
    * returned as null.
    * @param {Array} labels - Array of string labels.
    * @return {Array} Array of control codes, with null indicating the finish.
    */
    function readControlCodes(labels) {
        var controlCodes = [];
        for (var labelIdx = 0; labelIdx < labels.length; labelIdx += 1) {
            var label = labels[labelIdx];
            var parenPos = label.indexOf("(");
            if (parenPos > -1 && label[label.length - 1] === ")") {
                var controlCode = label.substring(parenPos + 1, label.length - 1);
                controlCodes.push(controlCode);
            } else if (labelIdx + 1 === labels.length) {
                controlCodes.push(null);
            } else {
                throwInvalidData("Unrecognised control header label: '" + label + "'");
            }
        }
    
        return controlCodes;
    }

    /**
    * Removes from the given arrays of cumulative and split times any 'extra'
    * controls.
    *
    * An 'extra' control is a control that a competitor punches without it
    * being a control on their course.  Extra controls are indicated by the
    * split 'time' beginning with an asterisk.
    *
    * This method does not return anything, instead it mutates the arrays
    * given.
    * 
    * @param {Array} cumTimes - Array of cumulative times.
    * @param {Array} splitTimes - Array of split times.
    */
    function removeExtraControls(cumTimes, splitTimes) {
        while (splitTimes.length > 0 && splitTimes[splitTimes.length - 1][0] === "*") {
            splitTimes.splice(splitTimes.length - 1, 1);
            cumTimes.splice(cumTimes.length - 1, 1);
        }
    }

    /**
    * Represents the result of parsing lines of competitor data.  This can
    * represent intermediate data as well as complete data.
    * @constructor
    * @param {String} name - The name of the competitor.
    * @param {String} club - The name of the competitor's club.
    * @param {String} className - The class of the competitor.
    * @param {Number|null} - The total time taken by the competitor, or null
    *     for no total time.
    * @param {Array} cumTimes - Array of cumulative split times.
    * @param {boolean} competitive - Whether the competitor's run is competitive.
    */
    var CompetitorParseRecord = function (name, club, className, totalTime, cumTimes, competitive) {
        this.name = name;
        this.club = club;
        this.className = className;
        this.totalTime = totalTime;
        this.cumTimes = cumTimes;
        this.competitive = competitive;
    };
    
    /**
    * Returns whether this competitor record is a 'continuation' record.
    * A continuation record is one that has no name, club, class name or total
    * time.  Instead it represents the data read from lines of data other than
    * the first two.
    * @return {boolean} True if the record is a continuation record, false if not.
    */
    CompetitorParseRecord.prototype.isContinuation = function () {
        return (this.name === "" && this.club === "" && this.className === null && this.totalTime === "" && !this.competitive);
    };
    
    /**
    * Appends the cumulative split times in another CompetitorParseRecord to
    * this one.  The one given must be a 'continuation' record.
    * @param {CompetitorParseRecord} other - The record whose cumulative times
    *     we wish to append.
    */
    CompetitorParseRecord.prototype.append = function (other) {
        if (other.isContinuation()) {
            this.cumTimes = this.cumTimes.concat(other.cumTimes);
        } else {
            throw new Error("Can only append a continuation CompetitorParseRecord");
        }
    };

    /**
    * Creates a Competitor object from this CompetitorParseRecord object.
    * @param {Number} order - The number of this competitor within their class
    *     (1=first, 2=second, ...).
    * @return {Competitor} Converted competitor object.
    */
    CompetitorParseRecord.prototype.toCompetitor = function (order) {
        var lastCumTime = 0;
        this.cumTimes.forEach(function (cumTime) {
            if (cumTime !== null) {
                if (cumTime <= lastCumTime) {
                    throwInvalidData("Cumulative times must be strictly ascending: read " +
                        formatTime(lastCumTime) + " and " + formatTime(cumTime) +
                        " in that order");
                }

                lastCumTime = cumTime;
            }
        });
        
        // Prepend a zero cumulative time.
        var cumTimes = [0].concat(this.cumTimes);
        
        // The null is for the start time.
        var competitor = Competitor.fromCumTimes(order, this.name, this.club, null, cumTimes);
        if (competitor.completed() && !this.competitive) {
            competitor.setNonCompetitive();
        }
        
        return competitor;
    };

    /*
    * There are two types of HTML format supported by this parser: one that is
    * based on pre-formatted text, and one that uses HTML tables.  The overall
    * strategy when parsing either format is largely the same, but the exact
    * details vary.
    *
    * A 'Recognizer' is used to handle the finer details of the format parsing.
    * A recognizer should contain methods 'isTextOfThisFormat',
    * 'preprocess', 'canIgnoreThisLine', 'isCourseHeaderLine', 
    * 'parseCourseHeaderLine', 'parseControlsLine' and 'parseCompetitor'.
    * See the documentation on the objects below for more information about
    * what these methods do.
    */
    
    /**
    * A Recognizer that handles the 'older' HTML format based on preformatted
    * text.
    * @constructor
    */
    var OldHtmlFormatRecognizer = function () {
        // Intentionally empty.
    };
    
    /**
    * Returns whether this recognizer is likely to recognize the given HTML
    * text and possibly be able to parse it.  If this method returns true, the
    * parser will use this recognizer to attempt to parse the HTML.  If it
    * returns false, the parser will not use this recognizer.  Other methods on
    * this object can therefore assume that this method has returned true.
    *
    * As this recognizer is for recognizing preformatted text, it simply checks
    * for the presence of an HTML &lt;pre&gt; tag.
    *
    * @param {String} text - The entire input text read in.
    * @return {boolean} True if the text contains any pre-formatted HTML, false
    *     otherwise
    */ 
    OldHtmlFormatRecognizer.prototype.isTextOfThisFormat = function (text) {
        return (text.indexOf("<pre>") >= 0);
    };
    
    /**
    * Performs some pre-processing on the text before it is read in.
    *
    * This object strips everything up to and including the opening
    * &lt;pre&gt; tag, and everything from the closing &lt;/pre&gt; tag
    * to the end of the text.
    * 
    * @param {String} text - The HTML text to preprocess.
    * @return {String} The preprocessed text.
    */
    OldHtmlFormatRecognizer.prototype.preprocess = function (text) {
        var prePos = text.indexOf("<pre>");
        if (prePos === -1) {
            throw new Error("Cannot find opening pre tag");
        }
            
        var lineEndPos = text.indexOf("\n", prePos);
        text = text.substring(lineEndPos + 1);
        
        var closePrePos = text.lastIndexOf("</pre>");
        if (closePrePos === -1) {
            throwInvalidData("Found opening <pre> but no closing </pre>");
        }
            
        lineEndPos = text.lastIndexOf("\n", closePrePos);
        text = text.substring(0, lineEndPos);
        return $.trim(text);
    };
    
    /**
    * Returns whether the HTML parser can ignore the given line altogether.
    *
    * The parser will call this method with every line read in, apart from
    * the second line of each pair of competitor data rows.  These are always
    * assumed to be in pairs.  
    *
    * This recognizer ignores only blank lines.
    *
    * @param {String} line - The line to check.
    * @return {boolean} True if the line should be ignored, false if not.
    */
    OldHtmlFormatRecognizer.prototype.canIgnoreThisLine = function (line) {
        return line === "";
    };
    
    /**
    * Returns whether the given line is the first line of a course.
    *
    * If so, it means the parser has finished processing the previous course
    * (if any), and can start a new course.
    *
    * This recognizer treats a line with exactly two
    * &lt;font&gt;...&lt;/font&gt; elements as a course header line, and
    * anything else not.
    *
    * @param {String} line - The line to check.
    * @return {boolean} True if this is the first line of a course, false
    *     otherwise.
    */
    OldHtmlFormatRecognizer.prototype.isCourseHeaderLine = function (line) {
        return (getFontBits(line).length === 2);
    };
    
    /**
    * Parse a course header line and return the course name, distance and
    * climb.
    *
    * This method can assume that the line given is a course header line.
    *
    * @param {String} line - The line to parse course details from.
    * @return {Object} Object containing the parsed course details.
    */
    OldHtmlFormatRecognizer.prototype.parseCourseHeaderLine = function (line) {
        var bits = getFontBits(line);
        if (bits.length !== 2) {
            throw new Error("Course header line should have two parts");
        }
        
        var nameAndControls = bits[0];
        var distanceAndClimb = bits[1];
        
        var openParenPos = nameAndControls.indexOf("(");
        var courseName = (openParenPos > -1) ? nameAndControls.substring(0, openParenPos) : nameAndControls;
        
        var distance = tryReadDistance(distanceAndClimb);
        var climb = tryReadClimb(distanceAndClimb);
        
        return {
            name: $.trim(courseName),
            distance: distance,
            climb: climb
        };
    };
    
    /**
    * Parse control codes from the given line and return a list of them.
    *
    * This method can assume that the previous line was the course header or a
    * previous control line.  It should also return null for the finish, which
    * should have no code.  The finish is assumed to he the last.
    *
    * @param {String} line - The line to parse control codes from.
    * @return {Array} Array of control codes.
    */
    OldHtmlFormatRecognizer.prototype.parseControlsLine = function (line) {
        var lastFontPos = line.lastIndexOf("</font>");
        var controlsText = (lastFontPos === -1) ? line : line.substring(lastFontPos + "</font>".length);

        var controlLabels = splitByWhitespace($.trim(controlsText));
        return readControlCodes(controlLabels);
    };
    
    /**
    * Read either cumulative or split times from the given line of competitor
    * data.
    * (This method is not used by the parser, only elsewhere in the recognizer.)
    * @param {String} line - The line to read the times from.
    * @return {Array} Array of times.
    */
    OldHtmlFormatRecognizer.prototype.readCompetitorSplitDataLine = function (line) {
        for (var i = 0; i < 4; i += 1) {
            var closeFontPos = line.indexOf("</font>");
            line = line.substring(closeFontPos + "</font>".length);
        }
        
        var times = splitByWhitespace(stripHtml(line));
        return times;
    };
    
    /**
    * Parse two lines of competitor data into a CompetitorParseRecord object
    * containing the data.
    * @param {String} firstLine - The first line of competitor data.
    * @param {String} secondLine - The second line of competitor data.
    * @return {CompetitorParseRecord} The parsed competitor.
    */
    OldHtmlFormatRecognizer.prototype.parseCompetitor = function (firstLine, secondLine) {
        var firstLineBits = getFontBits(firstLine);
        var secondLineBits = getFontBits(secondLine);

        var competitive = hasNumber(firstLineBits[0]);
        var name = $.trim(firstLineBits[2]);
        var totalTime = $.trim(firstLineBits[3]);
        var club = $.trim(secondLineBits[2]);
        
        var cumulativeTimes = this.readCompetitorSplitDataLine(firstLine);
        var splitTimes = this.readCompetitorSplitDataLine(secondLine);
        cumulativeTimes = cumulativeTimes.map(parseTime);
        
        var nonZeroCumTimeCount = cumulativeTimes.filter(isNotNull).length;
        if (nonZeroCumTimeCount !== splitTimes.length) {
            throwInvalidData("Cumulative and split times do not have the same length: " + nonZeroCumTimeCount + " cumulative times, " + splitTimes.length + " split times");
        }
        
        var className = null;
        if (name !== null && name !== "") {
            var lastCloseFontPos = -1;
            for (var i = 0; i < 4; i += 1) {
                lastCloseFontPos = firstLine.indexOf("</font>", lastCloseFontPos + 1);
            }
            
            var firstLineUpToFourth = firstLine.substring(0, lastCloseFontPos + "</font>".length);
            var firstLineMinusFonts = firstLineUpToFourth.replace(/<font[^>]*>(.*?)<\/font>/g, "");
            var lineParts = splitByWhitespace(firstLineMinusFonts);
            if (lineParts.length > 0) {
                className = lineParts[0];
            }
        }
        
        removeExtraControls(cumulativeTimes, splitTimes);
        
        return new CompetitorParseRecord(name, club, className, totalTime, cumulativeTimes, competitive);
    };
    
    
    /**
    * Constructs a recognizer for formatting the 'newer' format of SI HTML
    * event results data.
    *
    * Data in this format is given within a number of HTML tables, three per
    * course.
    * @constructor
    */
    var NewHtmlFormatRecognizer = function () {
        this.currentCourseHasClass = false;
    };

    /**
    * Returns whether this recognizer is likely to recognize the given HTML
    * text and possibly be able to parse it.  If this method returns true, the
    * parser will use this recognizer to attempt to parse the HTML.  If it
    * returns false, the parser will not use this recognizer.  Other methods on
    * this object can therefore assume that this method has returned true.
    *
    * As this recognizer is for recognizing HTML formatted in tables, it
    * returns whether the number of HTML &lt;table&gt; tags is at least five.
    * Each course uses three tables, and there are two HTML tables before the
    * courses.
    *
    * @param {String} text - The entire input text read in.
    * @return {boolean} True if the text contains at least five HTML table
    *     tags.
    */ 
    NewHtmlFormatRecognizer.prototype.isTextOfThisFormat = function (text) {
        var tablePos = -1;
        for (var i = 0; i < 5; i += 1) {
            tablePos = text.indexOf("<table", tablePos + 1);
            if (tablePos === -1) {
                // Didn't find another table.
                return false;
            }
        }
        
        return true;
    };
    
    /**
    * Performs some pre-processing on the text before it is read in.
    *
    * This recognizer performs a fair amount of pre-processing, to remove
    * parts of the file we don't care about, and to reshape what there is left
    * so that it is in a more suitable form to be parsed.
    * 
    * @param {String} text - The HTML text to preprocess.
    * @return {String} The preprocessed text.
    */
    NewHtmlFormatRecognizer.prototype.preprocess = function (text) {
        // Remove the first table and end of the <div> it is contained in.
        var tableEndPos = text.indexOf("</table>");
        if (tableEndPos === -1) {
            throwInvalidData("Could not find any closing </table> tags");
        }

        text = text.substring(tableEndPos + "</table>".length);

        var closeDivPos = text.indexOf("</div>");
        var openTablePos = text.indexOf("<table");
        if (closeDivPos > -1 && closeDivPos < openTablePos) {
            text = text.substring(closeDivPos + "</div>".length);
        }

        // Rejig the line endings so that each row of competitor data is on its
        // own line, with table and table-row tags starting on new lines,
        // and closing table and table-row tags at the end of lines.
        text = text.replace(/>\n</g, "><").replace(/><tr>/g, ">\n<tr>").replace(/<\/tr></g, "</tr>\n<")
                   .replace(/><table/g, ">\n<table").replace(/<\/table></g, "</table>\n<");
        
        // Remove all <col> elements.
        text = text.replace(/<\/col[^>]*>/g, "");
        
        // Remove all rows that contain only a single non-breaking space.
        // In the file I have, the &nbsp; entities are missing their
        // semicolons.  However, this could well be fixed in the future.
        text = text.replace(/<tr[^>]*><td[^>]*>(?:<nobr>)?&nbsp;?(?:<\/nobr>)?<\/td><\/tr>/g, "");
        
        // Finally, remove the trailing </body> and </html> elements.
        text = text.replace("</body></html>", "");
        
        return $.trim(text);
    };
    
    /**
    * Returns whether the HTML parser can ignore the given line altogether.
    *
    * The parser will call this method with every line read in, apart from
    * the second line of each pair of competitor data rows.  These are always
    * assumed to be in pairs.  This recognizer takes advantage of this to scan
    * the course header tables to see if class names are included.
    *
    * This recognizer ignores blank lines. It also ignores any that contain
    * opening or closing HTML table tags.  This is not a problem because the
    * preprocessing has ensured that the table data is not in the same line.
    *
    * @param {String} line - The line to check.
    * @return {boolean} True if the line should be ignored, false if not.
    */
    NewHtmlFormatRecognizer.prototype.canIgnoreThisLine = function (line) {
        if (line.indexOf("<th>") > -1) {
            var bits = getNonEmptyTableHeaderBits(line);
            this.currentCourseHasClass = (bits.length === 5);
            return true;
        } else {
            return (line === "" || line.indexOf("<table") > -1 || line.indexOf("</table>") > -1);
        }
    };

    
    /**
    * Returns whether the given line is the first line of a course.
    *
    * If so, it means the parser has finished processing the previous course
    * (if any), and can start a new course.
    *
    * This recognizer treats a line that contains a table-data cell with I
    * "header" as the first line of a course.
    *
    * @param {String} line - The line to check.
    * @return {boolean} True if this is the first line of a course, false
    *     otherwise.
    */
    NewHtmlFormatRecognizer.prototype.isCourseHeaderLine = function (line) {
        return line.indexOf('<td id="header"') > -1;
    };
    
    /**
    * Parse a course header line and return the course name, distance and
    * climb.
    *
    * This method can assume that the line given is a course header line.
    *
    * @param {String} line - The line to parse course details from.
    * @return {Object} Object containing the parsed course details.
    */
    NewHtmlFormatRecognizer.prototype.parseCourseHeaderLine = function (line) {
        var dataBits = getNonEmptyTableDataBits(line);
        if (dataBits.length === 0) {
            throwInvalidData("No parts found in course header line");
        }
            
        var name = dataBits[0];
        var openParenPos = name.indexOf("(");
        if (openParenPos > -1) {
            name = name.substring(0, openParenPos);
        }
            
        name = $.trim(name);
        
        var distance = null;
        var climb = null;
        
        for (var bitIndex = 1; bitIndex < dataBits.length; bitIndex += 1) {
            if (distance === null) {
                distance = tryReadDistance(dataBits[bitIndex]);
            }
                    
            if (climb === null) {
                climb = tryReadClimb(dataBits[bitIndex]);
            }
        }
                    
        return {name: name, distance: distance, climb: climb };
    };

    /**
    * Parse control codes from the given line and return a list of them.
    *
    * This method can assume that the previous line was the course header or a
    * previous control line.  It should also return null for the finish, which
    * should have no code.  The finish is assumed to he the last.
    *
    * @param {String} line - The line to parse control codes from.
    * @return {Array} Array of control codes.
    */
    NewHtmlFormatRecognizer.prototype.parseControlsLine = function (line) {
        var bits = getNonEmptyTableDataBits(line);
        return readControlCodes(bits);
    };
    
    /**
    * Read either cumulative or split times from the given line of competitor
    * data.
    * (This method is not used by the parser, only elsewhere in the recognizer.)
    * @param {String} line - The line to read the times from.
    * @return {Array} Array of times.
    */
    NewHtmlFormatRecognizer.prototype.readCompetitorSplitDataLine = function (line) {
        var bits = getTableDataBits(line);
        
        var startPos = (this.currentCourseHasClass) ? 5 : 4;
        
        // Discard the empty bits at the end.
        var endPos = bits.length;
        while (endPos > 0 && bits[endPos - 1] === "") {
            endPos -= 1;
        }
        
        return bits.slice(startPos, endPos).filter(isNonEmpty);
    };
    
    /**
    * Parse two lines of competitor data into a CompetitorParseRecord object
    * containing the data.
    * @param {String} firstLine - The first line of competitor data.
    * @param {String} secondLine - The second line of competitor data.
    * @return {CompetitorParseRecord} The parsed competitor.
    */
    NewHtmlFormatRecognizer.prototype.parseCompetitor = function (firstLine, secondLine) {
        var firstLineBits = getTableDataBits(firstLine);
        var secondLineBits = getTableDataBits(secondLine);
        
        var competitive = hasNumber(firstLineBits[0]);
        var name = firstLineBits[2];
        var totalTime = firstLineBits[(this.currentCourseHasClass) ? 4 : 3];
        var club = secondLineBits[2];
        
        var className = (this.currentCourseHasClass && name !== "") ? firstLineBits[3] : null;
        
        var cumulativeTimes = this.readCompetitorSplitDataLine(firstLine);
        var splitTimes = this.readCompetitorSplitDataLine(secondLine);
        cumulativeTimes = cumulativeTimes.map(parseTime);
        
        var nonZeroCumTimeCount = cumulativeTimes.filter(isNotNull).length;
        
        if (nonZeroCumTimeCount !== splitTimes.length) {
            throwInvalidData("Cumulative and split times do not have the same length: " + nonZeroCumTimeCount + " cumulative times, " + splitTimes.length + " split times");
        }
        
        removeExtraControls(cumulativeTimes, splitTimes);
        
        return new CompetitorParseRecord(name, club, className, totalTime, cumulativeTimes, competitive);
    };
    

    /**
    * Represents the partial result of parsing a course.
    * @constructor
    * @param {String} name - The name of the course.
    * @param {Number|null} distance - The distance of the course in kilometres,
    *     if known, else null.
    * @param {Number|null} climb - The climb of the course in metres, if known,
    *     else null.
    */ 
    var CourseParseRecord = function (name, distance, climb) {
        this.name = name;
        this.distance = distance;
        this.climb = climb;
        this.controls = [];
        this.competitors = [];
    };
    
    /**
    * Adds the given list of control codes to those built up so far.
    * @param {Array} controls - Array of control codes read.
    */ 
    CourseParseRecord.prototype.addControls = function (controls) {
        this.controls = this.controls.concat(controls);
    };
    
    /**
    * Returns whether the course has all of the controls it needs.
    * The course has all its controls if its last control is the finish, which
    * is indicated by a null control code.
    * @return {boolean} True if the course has all of its controls, including
    *     the finish, false otherwise.
    */
    CourseParseRecord.prototype.hasAllControls = function () {
        return this.controls.length > 0 && this.controls[this.controls.length - 1] === null;
    };

    /**
    * Adds a competitor record to the collection held by this course.
    * @param {CompetitorParseRecord} competitor - The competitor to add.
    */
    CourseParseRecord.prototype.addCompetitor = function (competitor) {
        if (!competitor.competitive && competitor.cumTimes.length === this.controls.length - 1) {
            // Odd quirk of the format: mispunchers may have their finish split
            // missing, i.e. not even '-----'.  If it looks like this has
            // happened, fill the gap by adding a missing time for the finish.
            competitor.cumTimes.push(null);
        }
        
        if (competitor.cumTimes.length === this.controls.length) {
            this.competitors.push(competitor);
        } else {
            throwInvalidData("Competitor '" + competitor.name + "' should have " + this.controls.length + " cumulative times, but has " + competitor.cumTimes.length + " times");
        }
    };

    /**
    * A parser that is capable of parsing event data in a given HTML format.
    * @constructor
    * @param {Object} recognizer - The recognizer to use to parse the HTML.
    */
    var SIHtmlFormatParser = function (recognizer) {
        this.recognizer = recognizer;
        this.courses = [];
        this.currentCourse = null;
        this.lines = null;
        this.linePos = -1;
        this.currentCompetitor = null;
    };
    
    /**
    * Attempts to read the next unread line from the data given.  If the end of
    * the data has been read, null will be returned.
    * @return {String|null} The line read, or null if the end of the data has
    *     been reached.
    */
    SIHtmlFormatParser.prototype.tryGetLine = function () {
        if (this.linePos + 1 < this.lines.length) {
            this.linePos += 1;
            return this.lines[this.linePos];
        } else {
            return null;
        }
    };
    
    /**
    * Adds the current competitor being constructed to the current course, and
    * clear the current competitor.
    * 
    * If there is no current competitor, nothing happens.
    */
    SIHtmlFormatParser.prototype.addCurrentCompetitorIfNecessary = function () {
        if (this.currentCompetitor !== null) {
            this.currentCourse.addCompetitor(this.currentCompetitor);
            this.currentCompetitor = null;
        }
    };
    
    /**
    * Adds the current competitor being constructed to the current course, and
    * the current course being constructed to the list of all courses.
    * 
    * If there is no current competitor nor no current course, nothing happens.
    */
    SIHtmlFormatParser.prototype.addCurrentCompetitorAndCourseIfNecessary = function () {
        this.addCurrentCompetitorIfNecessary();
        if (this.currentCourse !== null) {
            this.courses.push(this.currentCourse);
        }
    };
    
    /**
    * Reads in data for one competitor from two lines of the input data.
    *
    * The first of the two lines will be given; the second will be read.
    * @param {String} firstLine - The first of the two lines to read the
    *     competitor data from.
    */
    SIHtmlFormatParser.prototype.readCompetitorLines = function (firstLine) {
        var secondLine = this.tryGetLine();
        if (secondLine === null) {
            throwInvalidData("Hit end of input data unexpectedly while parsing competitor: first line was '" + firstLine + "'");
        }
            
        var competitorRecord = this.recognizer.parseCompetitor(firstLine, secondLine);
        if (competitorRecord.isContinuation()) {
            if (this.currentCompetitor === null) {
                throwInvalidData("First row of competitor data has no name nor time");
            } else {
                this.currentCompetitor.append(competitorRecord);
            }
        } else {
            this.addCurrentCompetitorIfNecessary();
            this.currentCompetitor = competitorRecord;
        }
    };
    
    /**
    * Returns whether the classes are unique within courses.  If so, they can
    * be used to subdivide courses.  If not, AgeClasses and Courses must be
    * the same.
    * @return {boolean} True if no two competitors in the same class are on
    *     different classes, false otherwise.
    */ 
    SIHtmlFormatParser.prototype.areAgeClassesUniqueWithinCourses = function () {
        var classesToCoursesMap = d3.map();
        for (var courseIndex = 0; courseIndex < this.courses.length; courseIndex += 1) {
            var course = this.courses[courseIndex];
            for (var competitorIndex = 0; competitorIndex < course.competitors.length; competitorIndex += 1) {
                var competitor = course.competitors[competitorIndex];
                if (classesToCoursesMap.has(competitor.className)) {
                    if (classesToCoursesMap.get(competitor.className) !== course.name) {
                        return false;
                    }
                } else {
                    classesToCoursesMap.set(competitor.className, course.name);
                }
            }
        }
        
        return true;
    };
    
    /**
    * Reads through all of the intermediate parse-record data and creates an
    * Event object with all of the courses and classes.
    * @return {Event} Event object containing all of the data.
    */
    SIHtmlFormatParser.prototype.createOverallEventObject = function () {
        // There is a complication here regarding classes.  Sometimes, classes
        // are repeated within multiple courses.  In this case, ignore the age
        // classes given and create an AgeClass for each set.
        var classesUniqueWithinCourses = this.areAgeClassesUniqueWithinCourses();
        
        var newCourses = [];
        var ageClasses = [];
        
        var competitorsHaveClasses = this.courses.every(function (course) {
            return course.competitors.every(function (competitor) { return isNotNull(competitor.className); });
        });
        
        this.courses.forEach(function (course) {
            // Firstly, sort competitors by class.
            var classToCompetitorsMap = d3.map();
            course.competitors.forEach(function (competitor) {
                var className = (competitorsHaveClasses && classesUniqueWithinCourses) ? competitor.className : course.name;
                if (classToCompetitorsMap.has(className)) {
                    classToCompetitorsMap.get(className).push(competitor);
                } else {
                    classToCompetitorsMap.set(className, [competitor]);
                }
            });
            
            var courseClasses = [];
            
            classToCompetitorsMap.keys().forEach(function (className) {
                var numControls = course.controls.length - 1;
                var oldCompetitors = classToCompetitorsMap.get(className);
                var newCompetitors = oldCompetitors.map(function (competitor, index) {
                    return competitor.toCompetitor(index + 1);
                });
                
                var ageClass = new AgeClass(className, numControls, newCompetitors);
                courseClasses.push(ageClass);
                ageClasses.push(ageClass);
            }, this);
            
            var newCourse = new Course(course.name, courseClasses, course.distance, course.climb, course.controls.slice(0, course.controls.length - 1));
            newCourses.push(newCourse);
            courseClasses.forEach(function (ageClass) {
                ageClass.setCourse(newCourse);
            });
        }, this);
        
        return new Event(ageClasses, newCourses);
    };
    
    /**
    * Parses the given HTML text containing results data into an Event object.
    * @param {String} text - The HTML text to parse.
    * @return {Event} Event object containing all the parsed data.
    */
    SIHtmlFormatParser.prototype.parse = function (text) {
        this.lines = text.split("\n");
        while (true) {
            var line = this.tryGetLine();
            if (line === null) {
                break;
            } else if (this.recognizer.canIgnoreThisLine(line)) {
                // Do nothing - recognizer says we can ignore this line.
            } else if (this.recognizer.isCourseHeaderLine(line)) {
                this.addCurrentCompetitorAndCourseIfNecessary();
                var courseObj = this.recognizer.parseCourseHeaderLine(line);
                this.currentCourse = new CourseParseRecord(courseObj.name, courseObj.distance, courseObj.climb);
            } else if (this.currentCourse === null) {
                // Do nothing - still not found the start of the first course.
            } else if (this.currentCourse.hasAllControls()) {
                // Course has all of its controls; read competitor data.
                this.readCompetitorLines(line);
            } else {
                var controls = this.recognizer.parseControlsLine(line);
                this.currentCourse.addControls(controls);
            }
        }
        
        this.addCurrentCompetitorAndCourseIfNecessary();
        
        var eventData = this.createOverallEventObject();
        return eventData;
    };
    
    /**
    * Normalise line-endings within the source data so that lines are ended
    * with LF characters.
    * @param {String} data - The text to normalise.
    * @return {String} The text with normalised line-endings.
    */
    function normaliseLineEndings(data) {
        return data.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
    }
    
    var RECOGNIZER_CLASSES = [OldHtmlFormatRecognizer, NewHtmlFormatRecognizer];
    
    SplitsBrowser.Input.SIHtml = {};
    
    /**
    * Attempts to parse data as one of the supported SI HTML formats.
    *
    * If the data appears not to be SI HTML data, a WrongFileFormat exception
    * is thrown.  If the data appears to be SI HTML data but is invalid in some
    * way, an InvalidData exception is thrown.
    *
    * @param {String} data - The string containing event data.
    */
    SplitsBrowser.Input.SIHtml.parseEventData = function (data) {
        data = normaliseLineEndings(data);
        for (var recognizerIndex = 0; recognizerIndex < RECOGNIZER_CLASSES.length; recognizerIndex += 1) {
            var RecognizerClass = RECOGNIZER_CLASSES[recognizerIndex];
            var recognizer = new RecognizerClass();
            if (recognizer.isTextOfThisFormat(data)) {
                data = recognizer.preprocess(data);
                var parser = new SIHtmlFormatParser(recognizer);
                var parsedEvent = parser.parse(data);
                return parsedEvent;
            }
        }
        
        // If we get here, the format wasn't recognized.
        throwWrongFileFormat("No HTML recognizers recognised this as HTML they could parse");
    };
})();    


(function () {
    "use strict";
    
    // All the parsers for parsing event data that are known about.
    var PARSERS = [
        SplitsBrowser.Input.CSV.parseEventData,
        SplitsBrowser.Input.SI.parseEventData,
        SplitsBrowser.Input.SIHtml.parseEventData
    ];
    
    /**
    * Attempts to parse the given event data, which may be of any of the
    * supported formats, or may be invalid.  This function returns the results
    * as an array of SplitsBrowser.Model.AgeClass objects, or null in the event
    * of failure.
    * @param {String} data - The data read.
    * @return {Event} Event data read in, or null for failure.
    */ 
    SplitsBrowser.Input.parseEventData = function (data) {
        for (var i = 0; i < PARSERS.length; i += 1) {
            var parser = PARSERS[i];
            try {
                return parser(data);
            } catch (e) {
                if (e.name !== "WrongFileFormat") {
                    throw e;
                }
            }
        }
            
        // If we get here, none of the parsers succeeded.
        return null;
    };
})();

(function (){
    "use strict";

    // ID of the competitor list div.
    // Must match that used in styles.css.
    var COMPETITOR_LIST_ID = "competitorList";

    /**
    * Object that controls a list of competitors from which the user can select.
    * @constructor
    * @param {HTMLElement} parent - Parent element to add this listbox to.
    */
    var CompetitorListBox = function (parent) {
        this.parent = parent;
        this.handler = null;
        this.competitorSelection = null;
        this.isEnabled = true;

        this.listDiv = d3.select(parent).append("div")
                                        .attr("id", COMPETITOR_LIST_ID);
    };
    
    /**
    * Sets whether this competitor list-box is enabled.
    * @param {boolean} isEnabled - Whether this list-box is enabled.
    */
    CompetitorListBox.prototype.setEnabled = function (isEnabled) {
        this.isEnabled = isEnabled;
        this.listDiv.selectAll("div.competitor").classed("disabled", !isEnabled);
    };

    /**
    * Returns the width of the listbox, in pixels.
    * @returns {Number} Width of the listbox.
    */
    CompetitorListBox.prototype.width = function () {
        return $(this.listDiv.node()).width();
    };

    /**
    * Handles a change to the selection of competitors, by highlighting all
    * those selected and unhighlighting all those no longer selected.
    */
    CompetitorListBox.prototype.selectionChanged = function () {
        var outerThis = this;
        this.listDiv.selectAll("div.competitor")
                    .data(d3.range(this.competitorSelection.count))
                    .classed("selected", function (comp, index) { return outerThis.competitorSelection.isSelected(index); });
    };

    /**
    * Toggle the selectedness of a competitor.
    */
    CompetitorListBox.prototype.toggleCompetitor = function (index) {
        if (this.isEnabled) {
            this.competitorSelection.toggle(index);
        }
    };

    /**
    * Sets the list of competitors.
    * @param {Array} competitors - Array of competitor data.
    * @param {boolean} hasMultipleClasses - Whether the list of competitors is
    *      made up from those in multiple classes.
    */
    CompetitorListBox.prototype.setCompetitorList = function (competitors, multipleClasses) {
        // Note that we use jQuery's click event handling here instead of d3's,
        // as d3's doesn't seem to work in PhantomJS.
        $("div.competitor").off("click");
        
        var competitorDivs = this.listDiv.selectAll("div.competitor").data(competitors);

        competitorDivs.enter().append("div")
                              .classed("competitor", true);

        competitorDivs.selectAll("span").remove();
        
        if (multipleClasses) {
            competitorDivs.append("span")
                          .classed("competitorClassLabel", true)
                          .text(function (comp) { return comp.className; });
        }
        
        competitorDivs.append("span")
                      .classed("nonfinisher", function (comp) { return !comp.completed(); })
                      .text(function (comp) { return (comp.completed()) ? comp.name : "* " + comp.name; });        

        competitorDivs.exit().remove();
        
        var outerThis = this;
        $("div.competitor").each(function (index, div) {
            $(div).on("click", function () { outerThis.toggleCompetitor(index); });
        });
    };

    /**
    * Sets the competitor selection object.
    * @param {SplitsBrowser.Controls.CompetitorSelection} selection - Competitor selection.
    */
    CompetitorListBox.prototype.setSelection = function (selection) {
        if (this.competitorSelection !== null) {
            this.competitorSelection.deregisterChangeHandler(this.handler);
        }

        var outerThis = this;
        this.competitorSelection = selection;
        this.handler = function (indexes) { outerThis.selectionChanged(indexes); };
        this.competitorSelection.registerChangeHandler(this.handler);
        this.selectionChanged(d3.range(selection.count));
    };
    
    SplitsBrowser.Controls.CompetitorListBox = CompetitorListBox;
})();


(function (){
    "use strict";
    
    var throwInvalidData = SplitsBrowser.throwInvalidData;
    var getMessage = SplitsBrowser.getMessage;

    /**
    * A control that wraps a drop-down list used to choose between classes.
    * @param {HTMLElement} parent - The parent element to add the control to.
    */
    var ClassSelector = function(parent) {
        this.changeHandlers = [];
        this.otherClassesEnabled = true;
        
        var div = d3.select(parent).append("div")
                                   .style("float", "left");
                                   
        div.text(getMessage("ClassSelectorLabel"));
        
        var outerThis = this;
        this.dropDown = div.append("select").node();
        $(this.dropDown).bind("change", function() {
            outerThis.updateOtherClasses();
            outerThis.onSelectionChanged();
        });
        
        this.otherClassesCombiningLabel = div.append("span")
                                             .classed("otherClassCombining", true)
                                             .style("display", "none")
                                             .text(getMessage("AdditionalClassSelectorLabel"));
        
        this.otherClassesSelector = div.append("div")
                                       .classed("otherClassSelector", true)
                                       .style("display", "none");
                                   
        this.otherClassesSpan = this.otherClassesSelector.append("span");
        
        this.otherClassesList = d3.select(parent).append("div")
                                                 .classed("otherClassList", true)
                                                 .style("position", "absolute")
                                                 .style("display", "none");
                                   
        this.otherClassesSelector.on("click", function () { outerThis.showHideClassSelector(); });
         
        this.setClasses([]);
        
        // Indexes of the selected 'other classes'.
        this.selectedOtherClassIndexes = d3.set();
        
        // Ensure that a click outside of the drop-down list or the selector
        // box closes it.
        // Taken from http://stackoverflow.com/questions/1403615 and adjusted.
        $(document).click(function (e) {
            var listDiv = outerThis.otherClassesList.node();
            if (listDiv.style.display !== "none") {
                var container = $("div.otherClassList,div.otherClassSelector");
                if (!container.is(e.target) && container.has(e.target).length === 0) { 
                    listDiv.style.display = "none";
                }
            }
        });
        
        // Close the class selector if Escape is pressed.
        // 27 is the key code for the Escape key.
        $(document).keydown(function (e) {
            if (e.which === 27) {
                outerThis.otherClassesList.style("display", "none");
            }
        });
    };

    /**
    * Sets whether the other-classes selector is enabled, if it is shown at
    * all.
    * @param {boolean} otherClassesEnabled - true to enable the selector, false
    *      to disable it.
    */
    ClassSelector.prototype.setOtherClassesEnabled = function (otherClassesEnabled) {
        this.otherClassesCombiningLabel.classed("disabled", !otherClassesEnabled);
        this.otherClassesSelector.classed("disabled", !otherClassesEnabled);
        this.otherClassesEnabled = otherClassesEnabled;
    };

    /**
    * Sets the list of classes that this selector can choose between.
    * 
    * If there are no classes, a 'dummy' entry is added
    * @param {Array} classes - Array of AgeClass objects containing class data.
    */
    ClassSelector.prototype.setClasses = function(classes) {
        if ($.isArray(classes)) {
            this.classes = classes;
            var options;
            if (classes.length === 0) {
                this.dropDown.disabled = true;
                options = [getMessage("NoClassesLoadedPlaceholder")];
            } else {
                this.dropDown.disabled = false;
                options = classes.map(function(ageClass) { return ageClass.name; });
            }
            
            var optionsList = d3.select(this.dropDown).selectAll("option").data(options);
            optionsList.enter().append("option");
            
            optionsList.attr("value", function(_value, index) { return index.toString(); })
                       .text(function(value) { return value; });
                       
            optionsList.exit().remove();
      
            this.updateOtherClasses();
        } else {
            throwInvalidData("ClassSelector.setClasses: classes is not an array");
        }
    };

    /**
    * Add a change handler to be called whenever the selected class or classes
    * is changed.
    *
    * An array containing the indexes of the newly-selected classes is passed to
    * each handler function.  This array is guaranteed to be non-empty.  The
    * first index in the array is the 'primary' class.
    *
    * @param {Function} handler - Handler function to be called whenever the class
    *                   changes.
    */
    ClassSelector.prototype.registerChangeHandler = function(handler) {
        if (this.changeHandlers.indexOf(handler) === -1) {
            this.changeHandlers.push(handler);
        }    
    };

    /**
    * Handle a change of the selected option in the drop-down list.
    */
    ClassSelector.prototype.onSelectionChanged = function() {
        var indexes = [this.dropDown.selectedIndex];
        this.selectedOtherClassIndexes.forEach(function (index) { indexes.push(parseInt(index, 10)); });
        this.changeHandlers.forEach(function(handler) { handler(indexes); });
    };
    
    /**
    * Updates the text in the other-class box at the top.
    *
    * This text contains either a list of the selected classes, or placeholder
    * text if none are selected.
    */ 
    ClassSelector.prototype.updateOtherClassText = function () {
        var classIdxs = this.selectedOtherClassIndexes.values();
        classIdxs.sort(d3.ascending);
        var text;
        if (classIdxs.length === 0) {
            text = getMessage("NoAdditionalClassesSelectedPlaceholder");
        } else {
            text = classIdxs.map(function (classIdx) { return this.classes[classIdx].name; }, this)
                            .join(", ");
        }
        
        this.otherClassesSpan.text(text);
    };
    
    /**
    * Updates the other-classes selector div following a change of selected
    * 'main' class.
    */
    ClassSelector.prototype.updateOtherClasses = function () {
        this.otherClassesList.style("display", "none");
        this.selectedOtherClassIndexes = d3.set();
        this.updateOtherClassText();
            
        $("div.otherClassItem").off("click");
            
        var outerThis = this;
        var otherClasses;
        if (this.classes.length > 0) {
            var newClass = this.classes[this.dropDown.selectedIndex];
            otherClasses = newClass.course.getOtherClasses(newClass);
        } else {
            otherClasses = [];
        }
        
        var otherClassIndexes = otherClasses.map(function (cls) { return this.classes.indexOf(cls); }, this);
        
        var otherClassesSelection = this.otherClassesList.selectAll("div")
                                                         .data(otherClassIndexes);
        
        otherClassesSelection.enter().append("div")
                                     .classed("otherClassItem", true);
        
        otherClassesSelection.attr("id", function (classIdx) { return "ageClassIdx_" + classIdx; })
                             .classed("selected", false)
                             .text(function (classIdx) { return outerThis.classes[classIdx].name; });
                             
        otherClassesSelection.exit().remove();
        
        if (otherClassIndexes.length > 0) {
            this.otherClassesSelector.style("display", "inline-block");
            this.otherClassesCombiningLabel.style("display", null);
        } else {
            this.otherClassesSelector.style("display", "none");
            this.otherClassesCombiningLabel.style("display", "none");
        }
        
        var offset = $(this.otherClassesSelector.node()).offset();
        var height = $(this.otherClassesSelector.node()).outerHeight();
        this.otherClassesList.style("left", offset.left + "px")
                            .style("top", offset.top + height + "px");
                            
        $("div.otherClassItem").each(function (index, div) {
            $(div).on("click", function () { outerThis.toggleOtherClass(otherClassIndexes[index]); });
        });
    };
    
    /**
    * Shows or hides the other-class selector, if it is enabled.
    */
    ClassSelector.prototype.showHideClassSelector = function () {
        if (this.otherClassesEnabled) {
            this.otherClassesList.style("display", (this.otherClassesList.style("display") === "none") ? null : "none");
        }
    };
    
    /**
    * Toggles the selection of an other class.
    * @param {Number} classIdx - Index of the class among the list of all classes.
    */
    ClassSelector.prototype.toggleOtherClass = function (classIdx) {
        if (this.selectedOtherClassIndexes.has(classIdx)) {
            this.selectedOtherClassIndexes.remove(classIdx);
        } else {
            this.selectedOtherClassIndexes.add(classIdx);
        }
        
        d3.select("div#ageClassIdx_" + classIdx).classed("selected", this.selectedOtherClassIndexes.has(classIdx));
        this.updateOtherClassText();
        this.onSelectionChanged();
    };
    
    SplitsBrowser.Controls.ClassSelector = ClassSelector;
})();


(function (){
    "use strict";
    
    var getMessage = SplitsBrowser.getMessage;
    var getMessageWithFormatting = SplitsBrowser.getMessageWithFormatting;
    
    var ALL_COMPARISON_OPTIONS = [
        {
            nameKey: "CompareWithWinner",
            selector: function (ageClassSet) { return ageClassSet.getWinnerCumTimes(); },
            requiresWinner: true,
            percentage: ""
        },
        {
            nameKey: "CompareWithFastestTime",
            selector: function (ageClassSet) { return ageClassSet.getFastestCumTimes(); },
            requiresWinner: false,
            percentage: ""
        }
    ];
    
    // All 'Fastest time + N %' values (not including zero).
    var FASTEST_PLUS_PERCENTAGES = [5, 25, 50, 100];
    
    FASTEST_PLUS_PERCENTAGES.forEach(function (percent) {
        ALL_COMPARISON_OPTIONS.push({
            nameKey: "CompareWithFastestTimePlusPercentage",
            selector: function (ageClassSet) { return ageClassSet.getFastestCumTimesPlusPercentage(percent); },
            requiresWinner: false, 
            percentage: percent
        });
    });
    
    ALL_COMPARISON_OPTIONS.push({
        nameKey: "CompareWithAnyRunner",
        selector: null,
        requiresWinner: true,
        percentage: ""
    });
    
    // Default selected index of the comparison function.
    var DEFAULT_COMPARISON_INDEX = 1; // 1 = fastest time.
    
    // The id of the comparison selector.
    var COMPARISON_SELECTOR_ID = "comparisonSelector";
    
    // The id of the runner selector
    var RUNNER_SELECTOR_ID = "runnerSelector";

    /**
    * A control that wraps a drop-down list used to choose what to compare
    * times against.
    * @param {HTMLElement} parent - The parent element to add the control to.
    * @param {Function} alerter - Function to call with any messages to show to
    *     the user.
    */
    var ComparisonSelector = function (parent, alerter) {
        this.changeHandlers = [];
        this.classes = null;
        this.currentRunnerIndex = null;
        this.previousCompetitorList = null;
        this.parent = parent;
        this.alerter = alerter;
        this.hasWinner = false;
        this.previousSelectedIndex = -1;
        
        var div = d3.select(parent).append("div")
                                   .attr("id", "comparisonSelectorContainer");
        
        div.append("span")
           .classed("comparisonSelectorLabel", true)
           .text(getMessage("ComparisonSelectorLabel"));

        var outerThis = this;
        this.dropDown = div.append("select")
                           .attr("id", COMPARISON_SELECTOR_ID)
                           .node();
                            
        $(this.dropDown).bind("change", function() { outerThis.onSelectionChanged(); });

        var optionsList = d3.select(this.dropDown).selectAll("option")
                                                  .data(ALL_COMPARISON_OPTIONS);
        optionsList.enter().append("option");
        
        optionsList.attr("value", function (_opt, index) { return index.toString(); })
                   .text(function (opt) { return getMessageWithFormatting(opt.nameKey, {"$$PERCENT$$": opt.percentage}); });
                   
        optionsList.exit().remove();
        
        this.runnerDiv = d3.select(parent).append("div")
                                          .attr("id", "runnerSelectorContainer")
                                          .style("display", "none")
                                          .style("padding-left", "20px");
        
        this.runnerDiv.append("span")
                      .classed("comparisonSelectorLabel", true)
                      .text(getMessage("CompareWithAnyRunnerLabel"));
        
        this.runnerDropDown = this.runnerDiv.append("select")
                                            .attr("id", RUNNER_SELECTOR_ID)
                                            .node();
                                            
        $(this.runnerDropDown).bind("change", function () { outerThis.onSelectionChanged(); });
        
        this.dropDown.selectedIndex = DEFAULT_COMPARISON_INDEX;
        this.previousSelectedIndex = DEFAULT_COMPARISON_INDEX;
    };

    /**
    * Add a change handler to be called whenever the selected class is changed.
    *
    * The function used to return the comparison result is returned.
    *
    * @param {Function} handler - Handler function to be called whenever the class
    *                   changes.
    */
    ComparisonSelector.prototype.registerChangeHandler = function(handler) {
        if (this.changeHandlers.indexOf(handler) === -1) {
            this.changeHandlers.push(handler);
        }    
    };

    /**
    * Returns whether the 'Any Runner...' option is selected.
    * @return Whether the 'Any Runner...' option is selected.
    */
    ComparisonSelector.prototype.isAnyRunnerSelected = function () {
        return this.dropDown.selectedIndex === ALL_COMPARISON_OPTIONS.length - 1;
    };
    
    /**
    * Sets the list of classes.
    * @param {Array} classes - Array of AgeClass objects.
    */
    ComparisonSelector.prototype.setAgeClassSet = function (ageClassSet) {
        this.ageClassSet = ageClassSet;
        this.setRunners();
    };

    /**
    * Populates the drop-down list of runners from an age-class set.
    * @param {SplitsBrowser.Model.AgeClassSet} ageClassSet - Age-class set
    *     containing all of the runners to populate the list from.
    */
    ComparisonSelector.prototype.setRunners = function () {
        var competitors = this.ageClassSet.allCompetitors;
        var completingCompetitorIndexes = d3.range(competitors.length).filter(function (idx) { return competitors[idx].completed(); });
        var completingCompetitors = competitors.filter(function (comp) { return comp.completed(); });
        
        this.hasWinner = (completingCompetitors.length > 0);
        
        var optionsList = d3.select(this.runnerDropDown).selectAll("option")
                                                        .data(completingCompetitors);
        
        optionsList.enter().append("option");
        optionsList.attr("value", function (_comp, complCompIndex) { return completingCompetitorIndexes[complCompIndex].toString(); })
                   .text(function (comp) { return comp.name; });
        optionsList.exit().remove();

        if (this.previousCompetitorList === null) {
            this.currentRunnerIndex = 0;
        } else {
            var oldSelectedRunner = this.previousCompetitorList[this.currentRunnerIndex];
            var newIndex = this.ageClassSet.allCompetitors.indexOf(oldSelectedRunner);
            this.currentRunnerIndex = Math.max(newIndex, 0);
        }
        
        this.runnerDropDown.selectedIndex = this.currentRunnerIndex;
       
        this.previousCompetitorList = this.ageClassSet.allCompetitors;
    };
    
    /**
    * Sets whether the control is enabled.
    * @param {boolean} isEnabled - True if the control is enabled, false if
    *      disabled.
    */
    ComparisonSelector.prototype.setEnabled = function (isEnabled) {
        d3.select(this.parent).selectAll("span.comparisonSelectorLabel")
                              .classed("disabled", !isEnabled);
                              
        this.dropDown.disabled = !isEnabled;
        this.runnerDropDown.disabled = !isEnabled;
    };
    
    /**
    * Returns the function that compares a competitor's splits against some
    * reference data.
    * @return {Function} Comparison function.
    */
    ComparisonSelector.prototype.getComparisonFunction = function () {
        if (this.isAnyRunnerSelected()) {
            var outerThis = this;
            return function (ageClassSet) { return ageClassSet.allCompetitors[outerThis.currentRunnerIndex].getAllCumulativeTimes(); };
        } else {
            return ALL_COMPARISON_OPTIONS[this.dropDown.selectedIndex].selector;
        }
    };
    
    /**
    * Handle a change of the selected option in either drop-down list.
    */
    ComparisonSelector.prototype.onSelectionChanged = function() {
        var runnerDropdownSelectedIndex = Math.max(this.runnerDropDown.selectedIndex, 0);
        var option = ALL_COMPARISON_OPTIONS[this.dropDown.selectedIndex];
        if (!this.hasWinner && option.requiresWinner) {
            // No winner on this course means you can't select this option.
            this.alerter(getMessageWithFormatting("CannotCompareAsNoWinner", {"$$OPTION$$": getMessage(option.nameKey)}));
            this.dropDown.selectedIndex = this.previousSelectedIndex;
        } else {
            this.runnerDiv.style("display", (this.isAnyRunnerSelected()) ? null : "none");
            this.currentRunnerIndex = (this.runnerDropDown.options.length === 0) ? 0 : parseInt(this.runnerDropDown.options[runnerDropdownSelectedIndex].value, 10);
            this.previousSelectedIndex = this.dropDown.selectedIndex;
            this.changeHandlers.forEach(function (handler) { handler(this.getComparisonFunction()); }, this);
        }
    };
    
    SplitsBrowser.Controls.ComparisonSelector = ComparisonSelector;
})();


(function () {
    "use strict";
    
    var getMessage = SplitsBrowser.getMessage;

    // ID of the statistics selector control.
    // Must match that used in styles.css.
    var STATISTIC_SELECTOR_ID = "statisticSelector";

    var LABEL_ID_PREFIX = "statisticCheckbox";

    // Internal names of the statistics.
    var STATISTIC_NAMES = ["TotalTime", "SplitTime", "BehindFastest", "TimeLoss"];

    // Message keys for the labels of the four checkboxes.
    var STATISTIC_NAME_KEYS = ["StatisticsTotalTime", "StatisticsSplitTime", "StatisticsBehindFastest", "StatisticsTimeLoss"];
    
    // Names of statistics that are selected by default when the application
    // starts.
    var DEFAULT_SELECTED_STATISTICS = ["SplitTime", "TimeLoss"];

    /**
    * Control that contains a number of checkboxes for enabling and/or disabling
    * the display of various statistics.
    * @constructor
    * @param {HTMLElement} parent - The parent element.
    */
    var StatisticsSelector = function (parent) {
        this.span = d3.select(parent).append("span")
                                     .attr("id", STATISTIC_SELECTOR_ID);   

        var childSpans = this.span.selectAll("span")
                                  .data(STATISTIC_NAMES)
                                  .enter()
                                  .append("span");
         
        childSpans.append("input")
                  .attr("id", function(name) { return LABEL_ID_PREFIX + name; }) 
                  .attr("type", "checkbox")
                  .attr("checked", function (name) { return (DEFAULT_SELECTED_STATISTICS.indexOf(name) >= 0) ? "checked" : null; });
                  
        childSpans.append("label")
                  .attr("for", function(name) { return LABEL_ID_PREFIX + name; })
                  .classed("statisticsSelectorLabel", true)
                  .text(function (name, index) { return getMessage(STATISTIC_NAME_KEYS[index]); });
        
        var outerThis = this;
        $("input", this.span.node()).bind("change", function () { return outerThis.onCheckboxChanged(); });
                   
        this.handlers = [];
    };
    
    /**
    * Deselects all checkboxes.
    * 
    * This method is intended only for test purposes.
    */
    StatisticsSelector.prototype.clearAll = function () {
        this.span.selectAll("input").attr("checked", null);
    };

    /**
    * Sets whether the statistics selector controls are enabled.
    * @param {boolean} isEnabled - True if the controls are to be enabled,
    *      false if the controls are to be disabled.
    */
    StatisticsSelector.prototype.setEnabled = function (isEnabled) {
        this.span.selectAll("label.statisticsSelectorLabel")
                 .classed("disabled", !isEnabled);
        this.span.selectAll("input")
                 .attr("disabled", (isEnabled) ? null : "disabled");
    };
    
    /**
    * Register a change handler to be called whenever the choice of currently-
    * visible statistics is changed.
    *
    * If the handler was already registered, nothing happens.
    * @param {Function} handler - Function to be called whenever the choice
    *                             changes.
    */
    StatisticsSelector.prototype.registerChangeHandler = function (handler) {
        if (this.handlers.indexOf(handler) === -1) {
            this.handlers.push(handler);
        }
    };
       
    /**
    * Deregister a change handler from being called whenever the choice of
    *  currently-visible statistics is changed.
    *
    * If the handler given was never registered, nothing happens.
    * @param {Function} handler - Function to be called whenever the choice
    *                             changes.
    */
    StatisticsSelector.prototype.deregisterChangeHandler = function (handler) {
        var index = this.handlers.indexOf(handler);
        if (index !== -1) {
            this.handlers.splice(index, 1);
        }
    };

    /**
    * Return the statistics that are currently enabled.
    * @returns {Array} Array of booleans corresponding to enabled statistics.
    */
    StatisticsSelector.prototype.getVisibleStatistics = function () {
        var visibleStats = {};
        this.span.selectAll("input")[0].forEach(function (checkbox, index) {
            visibleStats[STATISTIC_NAMES[index]] = checkbox.checked;
        });
        
        return visibleStats;
    };

    /**
    * Handles the change in state of a checkbox, by firing all of the handlers.
    */
    StatisticsSelector.prototype.onCheckboxChanged = function () {
        var checkedFlags = this.getVisibleStatistics();
        this.handlers.forEach(function (handler) { handler(checkedFlags); });
    };
    
    SplitsBrowser.Controls.StatisticsSelector = StatisticsSelector;
})();


(function (){
    "use strict";
    
    var getMessage = SplitsBrowser.getMessage;
    
    /**
    * A control that wraps a drop-down list used to choose the types of chart to view.
    * @param {HTMLElement} parent - The parent element to add the control to.
    * @param {Array} chartTypes - Array of types of chart to list.
    */
    var ChartTypeSelector = function (parent, chartTypes) {
        this.changeHandlers = [];
        this.chartTypes = chartTypes;
        this.raceGraphDisabledNotifier = null;
        this.lastSelectedIndex = 0;
        
        var div = d3.select(parent).append("div")
                                    .attr("id", "chartTypeSelector");
        div.append("span")
           .text(getMessage("ChartTypeSelectorLabel"));
           
        var outerThis = this;
        this.dropDown = div.append("select").node();
        $(this.dropDown).bind("change", function() { outerThis.onSelectionChanged(); });
        
        var optionsList = d3.select(this.dropDown).selectAll("option").data(chartTypes);
        optionsList.enter().append("option");
        
        optionsList.attr("value", function (_value, index) { return index.toString(); })
                   .text(function (value) { return getMessage(value.nameKey); });
                   
        optionsList.exit().remove();
    };
    
    /**
    * Sets the function used to disable the selection of the race graph.
    *
    * If not null, this will be called whenever an attempt to select the race
    * graph is made, and the selection will revert to what it was before.  If
    * it is null, the race graph can be selected.
    *
    * @param {Function|null} raceGraphDisabledNotifier - Function to call when
    *     the race graph is selected
    */
    ChartTypeSelector.prototype.setRaceGraphDisabledNotifier = function (raceGraphDisabledNotifier) {
        this.raceGraphDisabledNotifier = raceGraphDisabledNotifier;
    };
    
    /**
    * Add a change handler to be called whenever the selected type of chart is changed.
    *
    * The selected type of chart is passed to the handler function.
    *
    * @param {Function} handler - Handler function to be called whenever the
    *                             chart type changes.
    */
    ChartTypeSelector.prototype.registerChangeHandler = function (handler) {
        if (this.changeHandlers.indexOf(handler) === -1) {
            this.changeHandlers.push(handler);
        }    
    };

    /**
    * Returns the currently-selected chart type.
    * @return {Array} The currently-selected chart type.
    */
    ChartTypeSelector.prototype.getChartType = function () {
        return this.chartTypes[Math.max(this.dropDown.selectedIndex, 0)];
    };
    
    /**
    * Handle a change of the selected option in the drop-down list.
    */
    ChartTypeSelector.prototype.onSelectionChanged = function () {
        if (this.raceGraphDisabledNotifier !== null && this.chartTypes[this.dropDown.selectedIndex].isRaceGraph) {
            this.raceGraphDisabledNotifier();
            this.dropDown.selectedIndex = Math.max(this.lastSelectedIndex, 0);
        }
        
        this.changeHandlers.forEach(function(handler) { handler(this.chartTypes[this.dropDown.selectedIndex]); }, this);
        this.lastSelectedIndex = this.dropDown.selectedIndex;
    };
    
    SplitsBrowser.Controls.ChartTypeSelector = ChartTypeSelector;
})();


(function () {
    "use strict";
    
    // The maximum number of fastest splits to show when the popup is open.
    var MAX_FASTEST_SPLITS = 10;

    // Width of the time interval, in seconds, when viewing nearby competitors
    // at a control on the race graph.
    var RACE_GRAPH_COMPETITOR_WINDOW = 240;
    
    var formatTime = SplitsBrowser.formatTime;
    var getMessage = SplitsBrowser.getMessage;
    var getMessageWithFormatting = SplitsBrowser.getMessageWithFormatting;
    
    var Course = SplitsBrowser.Model.Course;
    
    var ChartPopupData = {};
    
    /**
    * Returns the fastest splits to a control.
    * @param {SplitsBrowser.Model.AgeClassSet} ageClassSet - The age-class set
    *     containing the splits data.
    * @param {Number} controlIndex - The index of the control.
    * @return {Array} Array of fastest-split data.
    */
    ChartPopupData.getFastestSplitsPopupData = function (ageClassSet, controlIndex) {
        var data = ageClassSet.getFastestSplitsTo(MAX_FASTEST_SPLITS, controlIndex);
        data = data.map(function (comp) {
            return {time: comp.split, name: comp.name, highlight: false};
        });
        
        return {title: getMessage("SelectedClassesPopupHeader"), data: data, placeholder: getMessage("SelectedClassesPopupPlaceholder")};
    };
    
    /**
    * Returns the fastest splits for the currently-shown leg.  The list
    * returned contains the fastest splits for the current leg for each class.
    * @param {SplitsBrowser.Model.AgeClassSet} ageClassSet - The age-class set
    *     containing the splits data.
    * @param {SplitsBrowser.Model.EventData} eventData - Data for the entire
    *     event.
    * @param {Number} controlIndex - The index of the control.
    * @return {Object} Object that contains the title for the popup and the
    *     array of data to show within it.
    */
    ChartPopupData.getFastestSplitsForLegPopupData = function (ageClassSet, eventData, controlIndex) {
        var course = ageClassSet.getCourse();
        var startCode = course.getControlCode(controlIndex - 1);
        var endCode = course.getControlCode(controlIndex);
        
        var startControl = (startCode === Course.START) ? getMessage("StartName") : startCode;
        var endControl = (endCode === Course.FINISH) ? getMessage("FinishName") : endCode;
        
        var title = getMessageWithFormatting("FastestLegTimePopupHeader", {"$$START$$": startControl, "$$END$$": endControl});
        
        var primaryClass = ageClassSet.getPrimaryClassName();
        var data = eventData.getFastestSplitsForLeg(startCode, endCode)
                            .map(function (row) { return { name: row.name, className: row.className, time: row.split, highlight: (row.className === primaryClass)}; });
        
        return {title: title, data: data, placeholder: null};
    };
    
    /**
    * Returns an array of the competitors visiting a control at a given time.
    * @param {SplitsBrowser.Model.AgeClassSet} ageClassSet - The age-class set
    *     containing the splits data.
    * @param {SplitsBrowser.Model.EventData} eventData - Data for the entire
    *     event.
    * @param {Number} controlIndex - The index of the control.
    * @param {time} The current time, in units of seconds past midnight.
    * @return {Array} Array of competitor data.
    */
    ChartPopupData.getCompetitorsVisitingCurrentControlPopupData = function (ageClassSet, eventData, controlIndex, time) {
        var controlCode = ageClassSet.getCourse().getControlCode(controlIndex);
        var intervalStart = time - RACE_GRAPH_COMPETITOR_WINDOW / 2;
        var intervalEnd = time + RACE_GRAPH_COMPETITOR_WINDOW / 2;
        var competitors = eventData.getCompetitorsAtControlInTimeRange(controlCode, intervalStart, intervalEnd);
            
        var primaryClass = ageClassSet.getPrimaryClassName();
        var competitorData = competitors.map(function (row) { return {name: row.name, className: row.className, time: row.time, highlight: (row.className === primaryClass)}; });
        
        var controlName;
        if (controlCode === Course.START) {
            controlName = getMessage("StartName");
        } else if (controlCode === Course.FINISH) {
            controlName = getMessage("FinishName");
        } else {
            controlName = getMessageWithFormatting("ControlName", {"$$CODE$$": controlCode});
        }
        
        var title = getMessageWithFormatting(
            "NearbyCompetitorsPopupHeader",
            {"$$START$$": formatTime(intervalStart), "$$END$$": formatTime(intervalEnd), "$$CONTROL$$": controlName});
        
        return {title: title, data: competitorData, placeholder: getMessage("NoNearbyCompetitors")};
    };    
        
    /**
    * Compares two course names.
    * @param {String} name1 - One course name to compare.
    * @param {String} name2 - The other course name to compare.
    * @return {Number} Comparison result: -1 if name1 < name2, 1 if
    *     name1 > name2 and 0 if name1 === name2.
    */
    function compareCourseNames(name1, name2) {
        if (name1 === name2) {
            return 0;
        } else if (name1 === "" || name2 === "" || name1[0] !== name2[0]) {
            return (name1 < name2) ? -1 : 1;
        } else {
            // Both courses begin with the same letter.
            var regexResult = /^[^0-9]+/.exec(name1);
            if (regexResult !== null && regexResult.length > 0) {
                // regexResult should be a 1-element array.
                var result = regexResult[0];
                if (0 < result.length && result.length < name1.length && name2.substring(0, result.length) === result) {
                    var num1 = parseInt(name1.substring(result.length), 10);
                    var num2 = parseInt(name2.substring(result.length), 10);
                    if (!isNaN(num1) && !isNaN(num2)) {
                        return num1 - num2;
                    }
                }
            }
            
            return (name1 < name2) ? -1 : 1;
        }
    }
    
    /**
    * Tidy next-control data, by joining up multiple controls into one string,
    * and substituting the display-name of the finish if necessary.
    * @param {Array} nextControls - Array of next-control information objects.
    * @return {String} Next-control information containing joined-up control names.
    */
    function tidyNextControlsList(nextControls) {
        return nextControls.map(function (nextControlRec) {
            var codes = nextControlRec.nextControls.slice(0);
            if (codes[codes.length - 1] === Course.FINISH) {
                codes[codes.length - 1] = getMessage("FinishName");
            }
            
            return {course: nextControlRec.course, nextControls: codes.join(", ")};
        });
    }
    
    /**
    * Returns next-control data to show on the chart popup.
    * @param {SplitsBrowser.Model.Course} course - The course containing the
    *     controls data.
    * @param {SplitsBrowser.Model.EventData} eventData - Data for the entire
    *     event.
    * @param {Number} controlIndex - The index of the control.
    * @return {Array} Array of next-control data.
    */
    ChartPopupData.getNextControlData = function (course, eventData, controlIndex) {
        var controlIdx = Math.min(controlIndex, course.controls.length);
        var controlCode = course.getControlCode(controlIdx);
        var nextControls = eventData.getNextControlsAfter(controlCode);
        nextControls.sort(function (c1, c2) { return compareCourseNames(c1.course.name, c2.course.name); });
        var thisControlName = (controlCode === Course.START) ? getMessage("StartName") : getMessageWithFormatting("ControlName", {"$$CODE$$": controlCode});
        return {thisControl: thisControlName, nextControls: tidyNextControlsList(nextControls) };
    };
    
    SplitsBrowser.Model.ChartPopupData = ChartPopupData;
})();

(function () {
    "use strict";
    
    var formatTime = SplitsBrowser.formatTime;
    
    /**
    * Creates a ChartPopup control.
    * @constructor
    * @param {HTMLElement} Parent HTML element.
    * @param {Object} handlers - Object that maps mouse event names to handlers.
    */
    var ChartPopup = function (parent, handlers) {

        this.shown = false;
        this.mouseIn = false;
        this.popupDiv = d3.select(parent).append("div");
        this.popupDiv.classed("chartPopup", true)
                     .style("display", "none")
                     .style("position", "absolute");
                     
        this.dataHeader = this.popupDiv.append("div")
                                       .classed("chartPopupHeader", true)
                                       .append("span");
                                           
        var tableContainer = this.popupDiv.append("div")
                                              .classed("chartPopupTableContainer", true);
                                                  
                                           
        this.dataTable = tableContainer.append("table");
                                              
        this.popupDiv.selectAll(".nextControls").style("display", "none");

        // At this point we need to pass through mouse events to the parent.
        // This is solely for the benefit of IE < 11, as IE11 and other
        // browsers support pointer-events: none, which means that this div
        // receives no mouse events at all.
        for (var eventName in handlers) {
            if (handlers.hasOwnProperty(eventName)) {
                $(this.popupDiv.node()).on(eventName, handlers[eventName]);
            }
        }
        
        var outerThis = this;
        $(this.popupDiv.node()).mouseenter(function () { outerThis.mouseIn = true; });
        $(this.popupDiv.node()).mouseleave(function () { outerThis.mouseIn = false; });
    };

    /**
    * Returns whether the popup is currently shown.
    * @return {boolean} True if the popup is shown, false otherwise.
    */
    ChartPopup.prototype.isShown = function () {
        return this.shown;
    };
    
    /**
    * Returns whether the mouse is currently over the popup.
    * @return {boolean} True if the mouse is over the popup, false otherwise.
    */
    ChartPopup.prototype.isMouseIn = function () {
        return this.mouseIn;
    };
    
    /**
    * Populates the chart popup with data.
    *
    * 'competitorData' should be an object that contains a 'title', a 'data'
    * and a 'placeholder' property.  The 'title' is a string used as the
    * popup's title.  The 'data' property is an array where each element should
    * be an object that contains the following properties:
    * * time - A time associated with a competitor.  This may be a split time,
    *   cumulative time or the time of day.
    * * className (Optional) - Name of the competitor's class.
    * * name - The name of the competitor.
    * * highlight - A boolean value which indicates whether to highlight the
    *   competitor.
    * The 'placeholder' property is a placeholder string to show if there is no
    * 'data' array is empty.  It can be null to show no such message.
    * @param {Object} competitorData - Array of data to show.
    * @param {boolean} includeClassNames - Whether to include class names.
    */
    ChartPopup.prototype.setData = function (competitorData, includeClassNames) {
        this.dataHeader.text(competitorData.title);
        
        var rows = this.dataTable.selectAll("tr")
                                 .data(competitorData.data);
                                     
        rows.enter().append("tr");
        
        rows.classed("highlighted", function (row) { return row.highlight; });
        
        rows.selectAll("td").remove();
        rows.append("td").text(function (row) { return formatTime(row.time); });
        if (includeClassNames) {
            rows.append("td").text(function (row) { return row.className; });
        }
        rows.append("td").text(function (row) { return row.name; });
        
        rows.exit().remove();
        
        if (competitorData.data.length === 0 && competitorData.placeholder !== null) {
            this.dataTable.append("tr")
                          .append("td")
                          .text(competitorData.placeholder);
        }
    };
    
    /**
    * Sets the next-controls data.
    *
    * The next-controls data should be an object that contains two properties:
    * * thisControl - The 'current' control.
    * * nextControls - Array of objects, each with 'course' and 'nextControl'
    *   properties.
    *
    * @param {Object} nextControlsData - The next-controls data.
    */
    ChartPopup.prototype.setNextControlData = function (nextControlsData) {
        this.dataHeader.text(nextControlsData.thisControl);
        
        var rows = this.dataTable.selectAll("tr")
                                 .data(nextControlsData.nextControls);
        rows.enter().append("tr");
        
        rows.selectAll("td").remove();
        rows.classed("highlighted", false);
        rows.append("td").text(function (nextControlData) { return nextControlData.course.name; });
        rows.append("td").text("-->");
        rows.append("td").text(function (nextControlData) { return nextControlData.nextControls; });
        
        rows.exit().remove();
    };
    
    /**
    * Adjusts the location of the chart popup.
    *
    * The location object should contain "x" and "y" properties.  The two
    * coordinates are in units of pixels from top-left corner of the viewport.
    *
    * @param {Object} location - The location of the chart popup.
    */
    ChartPopup.prototype.setLocation = function (location) {
        this.popupDiv.style("left", location.x + "px")
                     .style("top", location.y + "px");
    };
    
    /**
    * Shows the chart popup.
    *
    * The location object should contain "x" and "y" properties.  The two
    * coordinates are in units of pixels from top-left corner of the viewport.
    *
    * @param {Object} location - The location of the chart popup.
    */
    ChartPopup.prototype.show = function (location) {
        this.popupDiv.style("display", null);
        this.shown = true;
        this.setLocation(location);
    };
    
    /**
    * Hides the chart popup.
    */
    ChartPopup.prototype.hide = function () {
        this.popupDiv.style("display", "none");
        this.shown = false;
    };
    
    /**
    * Returns the height of the popup, in units of pixels.
    * @return {Number} Height of the popup, in pixels.
    */
    ChartPopup.prototype.height = function () {
        return $(this.popupDiv.node()).height();
    };
    
    SplitsBrowser.Controls.ChartPopup = ChartPopup;    
})();

(function (){
    "use strict";

    // ID of the hidden text-size element.
    // Must match that used in styles.css.
    var TEXT_SIZE_ELEMENT_ID = "sb-text-size-element";
    
    // ID of the chart.
    // Must match that used in styles.css
    var CHART_SVG_ID = "chart";
    
    // X-offset in pixels between the mouse and the popup that opens.
    var CHART_POPUP_X_OFFSET = 10;
    
    // Margins on the four sides of the chart.
    var MARGIN = {
        top: 18, // Needs to be high enough not to obscure the upper X-axis.
        right: 0,
        bottom: 18, // Needs to be high enough not to obscure the lower X-axis.
        left: 53 // Needs to be wide enough for times on the race graph.
    };

    var LEGEND_LINE_WIDTH = 10;
    
    // Minimum distance between a Y-axis tick label and a competitor's start
    // time, in pixels.
    var MIN_COMPETITOR_TICK_MARK_DISTANCE = 10;
    
    // The number that identifies the left mouse button in a jQuery event.
    var JQUERY_EVENT_LEFT_BUTTON = 1;
    
    // The number that identifies the right mouse button in a jQuery event.
    var JQUERY_EVENT_RIGHT_BUTTON = 3;

    var SPACER = "\xa0\xa0\xa0\xa0";

    var colours = [
        "#FF0000", "#4444FF", "#00FF00", "#000000", "#CC0066", "#000099",
        "#FFCC00", "#884400", "#9900FF", "#CCCC00", "#888800", "#CC6699",
        "#00DD00", "#3399FF", "#BB00BB", "#00DDDD", "#FF00FF", "#0088BB",
        "#888888", "#FF99FF", "#55BB33"
    ];

    // 'Imports'.
    var isNotNull = SplitsBrowser.isNotNull;
    var formatTime = SplitsBrowser.formatTime;
    var getMessage = SplitsBrowser.getMessage;
    
    var ChartPopupData = SplitsBrowser.Model.ChartPopupData;
    var ChartPopup = SplitsBrowser.Controls.ChartPopup;
    
    /**
    * Format a time and a rank as a string, with the split time in mm:ss or h:mm:ss
    * as appropriate.
    * @param {Number|null} time - The time, in seconds, or null.
    * @param {Number|null} rank - The rank, or null.
    * @returns Time and rank formatted as a string.
    */
    function formatTimeAndRank(time, rank) {
        return SPACER + formatTime(time) + " (" + ((rank === null) ? "-" : rank) + ")";
    }
    
    /**
    * Formats and returns a competitor's name and optional suffix.
    * @param {String} name - The name of the competitor.
    * @param {String} suffix - The optional suffix of the competitor (may be an
    *      empty string to indicate no suffix).
    * @return Competitor name and suffix, formatted.
    */
    function formatNameAndSuffix(name, suffix) {
        return (suffix === "") ? name : name + " (" + suffix + ")";
    }

    /**
    * A chart object in a window.
    * @constructor
    * @param {HTMLElement} parent - The parent object to create the element within.
    */
    var Chart = function (parent) {
        this.parent = parent;

        this.xScale = null;
        this.yScale = null;
        this.overallWidth = -1;
        this.overallHeight = -1;
        this.contentWidth = -1;
        this.contentHeight = -1;
        this.numControls = -1;
        this.selectedIndexes = [];
        this.currentCompetitorData = null;
        this.isPopupOpen = false;
        this.popupUpdateFunc = null;
        this.maxStartTimeLabelWidth = 0;
        this.warningPanel = null;
        
        this.mouseOutTimeout = null;
        
        // Indexes of the currently-selected competitors, in the order that
        // they appear in the list of labels.
        this.selectedIndexesOrderedByLastYValue = [];
        this.referenceCumTimes = [];
        this.fastestCumTimes = [];
        
        this.isMouseIn = false;
        
        // The position the mouse cursor is currently over, or null for not over
        // the charts.  This index is constrained by the minimum control that a
        // chart type specifies.
        this.currentControlIndex = null;
        
        // The position the mouse cursor is currently over, or null for not over
        // the charts.  Unlike this.currentControlIndex, this index is not
        // constrained by the minimum control that a chart type specifies.
        this.actualControlIndex = null;
        
        this.controlLine = null;

        this.svg = d3.select(this.parent).append("svg")
                                         .attr("id", CHART_SVG_ID);

        this.svgGroup = this.svg.append("g");
        this.setLeftMargin(MARGIN.left);

        var outerThis = this;
        var mousemoveHandler = function (event) { outerThis.onMouseMove(event); };
        var mouseupHandler = function (event) { outerThis.onMouseUp(event); };
        var mousedownHandler = function (event) { outerThis.onMouseDown(event); };
        $(this.svg.node()).mouseenter(function (event) { outerThis.onMouseEnter(event); })
                          .mousemove(mousemoveHandler)
                          .mouseleave(function (event) { outerThis.onMouseLeave(event); })
                          .mousedown(mousedownHandler)
                          .mouseup(mouseupHandler);
                          
        // Disable the context menu on the chart, so that it doesn't open when
        // showing the right-click popup.
        $(this.svg.node()).contextmenu(function(e) { e.preventDefault(); });

        // Add an invisible text element used for determining text size.
        this.textSizeElement = this.svg.append("text").attr("fill", "transparent")
                                                      .attr("id", TEXT_SIZE_ELEMENT_ID);
        
        var handlers = {"mousemove": mousemoveHandler, "mousedown": mousedownHandler, "mouseup": mouseupHandler};
        this.popup = new ChartPopup(parent, handlers);
        
        $(document).mouseup(function () { outerThis.popup.hide(); });
    };
    
    /**
    * Hides the chart.
    */
    Chart.prototype.hide = function () {
        // Note that we don't use display: none to hide the chart.
        // While the chart is hidden, the sizes of various text strings are
        // determined.  Firefox gives you an NS_ERROR_FAILURE message if the
        // element you're trying to compute the size of, or an ancestor of it,
        // has display: none.        
        this.svg.style("position", "absolute")
                .style("left", "-9999px");
    };
    
    /**
    * Shows the chart, after it has been hidden.
    */
    Chart.prototype.show = function () {
        this.svg.style("position", null)
                .style("left", null);
    };
    
    /**
    * Sets the left margin of the chart.
    * @param {Number} leftMargin - The left margin of the chart.
    */
    Chart.prototype.setLeftMargin = function (leftMargin) {
        this.currentLeftMargin = leftMargin;
        this.svgGroup.attr("transform", "translate(" + this.currentLeftMargin + "," + MARGIN.top + ")");
    };

    /**
    * Gets the location the chart popup should be at following a mouse-button
    * press or a mouse movement.
    * @param {jQuery.event} event - jQuery mouse-down or mouse-move event.
    */
    Chart.prototype.getPopupLocation = function (event) {
        return {
            x: event.pageX + CHART_POPUP_X_OFFSET,
            y: Math.max(event.pageY - this.popup.height() / 2, 0)
        };
    };
    
    /**
    * Returns the fastest splits to the current control.
    * @return {Array} Array of fastest-split data.
    */
    Chart.prototype.getFastestSplitsPopupData = function () {
        return ChartPopupData.getFastestSplitsPopupData(this.ageClassSet, this.currentControlIndex);
    };
    
    /**
    * Returns the fastest splits for the currently-shown leg.  The list
    * returned contains the fastest splits for the current leg for each class.
    * @return {Object} Object that contains the title for the popup and the
    *     array of data to show within it.
    */
    Chart.prototype.getFastestSplitsForCurrentLegPopupData = function () {
        return ChartPopupData.getFastestSplitsForLegPopupData(this.ageClassSet, this.eventData, this.currentControlIndex);
    };
    
    /**
    * Stores the current time the mouse is at, on the race graph.
    * @param {jQuery.event} event - The mouse-down or mouse-move event.
    */
    Chart.prototype.setCurrentChartTime = function (event) {
        var yOffset = event.pageY - $(this.svg.node()).offset().top - MARGIN.top;
        this.currentChartTime = Math.round(this.yScale.invert(yOffset) * 60) + this.referenceCumTimes[this.currentControlIndex];
    };
    
    /**
    * Returns an array of the competitors visiting the current control at the
    * current time.
    * @return {Array} Array of competitor data.
    */
    Chart.prototype.getCompetitorsVisitingCurrentControlPopupData = function () {
        return ChartPopupData.getCompetitorsVisitingCurrentControlPopupData(this.ageClassSet, this.eventData, this.currentControlIndex, this.currentChartTime);
    };
    
    /**
    * Returns next-control data to show on the chart popup.
    * @return {Array} Array of next-control data.
    */
    Chart.prototype.getNextControlData = function () {
        return ChartPopupData.getNextControlData(this.ageClassSet.getCourse(), this.eventData, this.actualControlIndex);
    };

    /**
    * Handle the mouse entering the chart.
    * @param {jQuery.event} event - jQuery event object.
    */
    Chart.prototype.onMouseEnter = function (event) {
        if (this.warningPanel === null) {
            if (this.mouseOutTimeout !== null) {
                clearTimeout(this.mouseOutTimeout);
                this.mouseOutTimeout = null;
            }
            
            this.isMouseIn = true;
            this.updateControlLineLocation(event);            
        }
    };

    /**
    * Handle a mouse movement.
    * @param {jQuery.event} event - jQuery event object.
    */
    Chart.prototype.onMouseMove = function (event) {
        if (this.isMouseIn && this.xScale !== null && this.warningPanel === null) {
            this.updateControlLineLocation(event);
        }
    };
     
    /**
    * Handle the mouse leaving the chart.
    */
    Chart.prototype.onMouseLeave = function () {
        if (this.warningPanel === null) {
            var outerThis = this;
            // Check that the mouse hasn't entered the popup.
            // It seems that the mouseleave event for the chart is sent before the
            // mouseenter event for the popup, so we use a timeout to check a short
            // time later whether the mouse has left the chart and the popup.
            // This is only necessary for IE9 and IE10; other browsers support
            // "pointer-events: none" in CSS so the popup never gets any mouse
            // events.
            
            // Note that we keep a reference to the 'timeout', so that we can
            // clear it if the mouse subsequently re-enters.  This happens a lot
            // more often than might be expected for a function with a timeout of
            // only a single millisecond.
            this.mouseOutTimeout = setTimeout(function() {
                if (!outerThis.popup.isMouseIn()) {
                    outerThis.isMouseIn = false;
                    outerThis.removeControlLine();
                }
            }, 1);
        }
    };
    
    /**
    * Handles a mouse button being pressed over the chart.
    * @param {jQuery.Event} event - jQuery event object.
    */
    Chart.prototype.onMouseDown = function (event) {
        if (this.warningPanel === null) {
            var outerThis = this;
            // Use a timeout to open the dialog as we require other events
            // (mouseover in particular) to be processed first, and the precise
            // order of these events is not consistent between browsers.
            setTimeout(function () { outerThis.showPopupDialog(event); }, 1);
        }
    };
    
    /**
    * Handles a mouse button being pressed over the chart.
    */
    Chart.prototype.onMouseUp = function (event) {
        if (this.warningPanel === null) {
            this.popup.hide();
            event.preventDefault();
        }
    };
    
    /**
    * Shows the popup window, populating it with data as necessary
    * @param {jQuery event} event - The jQuery onMouseDown event that triggered
    *     the popup.
    */ 
    Chart.prototype.showPopupDialog = function (event) {
        if (this.isMouseIn && this.currentControlIndex !== null) {
            var showPopup = false;
            var outerThis = this;
            if (this.isRaceGraph && (event.which === JQUERY_EVENT_LEFT_BUTTON || event.which === JQUERY_EVENT_RIGHT_BUTTON)) {
                if (this.hasControls) {
                    this.setCurrentChartTime(event);
                    this.popupUpdateFunc = function () { outerThis.popup.setData(outerThis.getCompetitorsVisitingCurrentControlPopupData(), true); };
                    showPopup = true;
                }
            } else if (event.which === JQUERY_EVENT_LEFT_BUTTON) {
                this.popupUpdateFunc = function () { outerThis.popup.setData(outerThis.getFastestSplitsPopupData(), false); };
                showPopup = true;
            } else if (event.which === JQUERY_EVENT_RIGHT_BUTTON) {
                if (this.hasControls) {
                    this.popupUpdateFunc = function () { outerThis.popup.setData(outerThis.getFastestSplitsForCurrentLegPopupData(), true); };
                    showPopup = true;
                }
            }
            
            if (showPopup) {
                this.updatePopupContents(event);
                this.popup.show(this.getPopupLocation(event));
            }
        }
    };
    
    /**
    * Updates the chart popup with the contents it should contain.
    *
    * If the current course has control data, and the cursor is above the top
    * X-axis, control information is shown instead of whatever other data would
    * be being shown.
    *
    * @param {jQuery.event} event - jQuery mouse-move event.
    */
    Chart.prototype.updatePopupContents = function (event) {
        var yOffset = event.pageY - $(this.svg.node()).offset().top;
        var showNextControls = this.hasControls && yOffset < MARGIN.top;
        if (showNextControls) {
            this.updateNextControlInformation();
        } else {
            this.popupUpdateFunc();
        }
    };
    
    /**
    * Updates the next-control information.
    */
    Chart.prototype.updateNextControlInformation = function () {
        if (this.hasControls) {
            this.popup.setNextControlData(this.getNextControlData());
        }
    };

    /**
    * Draw a 'control line'.  This is a vertical line running the entire height of
    * the chart, at one of the controls.
    * @param {Number} controlIndex - The index of the control at which to draw the
    *                                control line.
    */
    Chart.prototype.drawControlLine = function(controlIndex) {
        this.currentControlIndex = controlIndex;
        this.updateCompetitorStatistics();    
        var xPosn = this.xScale(this.referenceCumTimes[controlIndex]);
        this.controlLine = this.svgGroup.append("line")
                                        .attr("x1", xPosn)
                                        .attr("y1", 0)
                                        .attr("x2", xPosn)
                                        .attr("y2", this.contentHeight)
                                        .attr("class", "controlLine")
                                        .node();
    };
    
    /**
    * Updates the location of the control line from the given mouse event.
    * @param {jQuery.event} event - jQuery mousedown or mousemove event.
    */
    Chart.prototype.updateControlLineLocation = function (event) {

        var svgNodeAsJQuery = $(this.svg.node());
        var offset = svgNodeAsJQuery.offset();
        var xOffset = event.pageX - offset.left;
        var yOffset = event.pageY - offset.top;
        
        if (this.currentLeftMargin <= xOffset && xOffset < svgNodeAsJQuery.width() - MARGIN.right && 
            yOffset < svgNodeAsJQuery.height() - MARGIN.bottom) {
            // In the chart.
            // Get the time offset that the mouse is currently over.
            var chartX = this.xScale.invert(xOffset - this.currentLeftMargin);
            var bisectIndex = d3.bisect(this.referenceCumTimes, chartX);
            
            // bisectIndex is the index at which to insert chartX into
            // referenceCumTimes in order to keep the array sorted.  So if
            // this index is N, the mouse is between N - 1 and N.  Find
            // which is nearer.
            var controlIndex;
            if (bisectIndex >= this.referenceCumTimes.length) {
                // Off the right-hand end, use the finish.
                controlIndex = this.numControls + 1;
            } else {
                var diffToNext = Math.abs(this.referenceCumTimes[bisectIndex] - chartX);
                var diffToPrev = Math.abs(chartX - this.referenceCumTimes[bisectIndex - 1]);
                controlIndex = (diffToPrev < diffToNext) ? bisectIndex - 1 : bisectIndex;
            }
            
            if (this.actualControlIndex === null || this.actualControlIndex !== controlIndex) {
                // The control line has appeared for ths first time or has moved, so redraw it.
                this.removeControlLine();
                this.actualControlIndex = controlIndex;
                this.drawControlLine(Math.max(this.minViewableControl, controlIndex));
            }
            
            if (this.popup.isShown() && this.currentControlIndex !== null) {
                if (this.isRaceGraph) {
                    this.setCurrentChartTime(event);
                }
                
                this.updatePopupContents(event);
                this.popup.setLocation(this.getPopupLocation(event));
            }
            
        } else {
            // In the SVG element but outside the chart area.
            this.removeControlLine();
            this.popup.hide();
        }
    };

    /**
    * Remove any previously-drawn control line.  If no such line existed, nothing
    * happens.
    */
    Chart.prototype.removeControlLine = function() {
        this.currentControlIndex = null;
        this.actualControlIndex = null;
        this.updateCompetitorStatistics();
        if (this.controlLine !== null) {
            d3.select(this.controlLine).remove();
            this.controlLine = null;
        }
    };

    /**
    * Returns an array of the the times that the selected competitors are
    * behind the fastest time at the given control.
    * @param {Number} controlIndex - Index of the given control.
    * @param {Array} indexes - Array of indexes of selected competitors.
    * @return {Array} Array of times in seconds that the given competitors are
    *     behind the fastest time.
    */
    Chart.prototype.getTimesBehindFastest = function (controlIndex, indexes) {
        var selectedCompetitors = indexes.map(function (index) { return this.ageClassSet.allCompetitors[index]; }, this);
        var fastestSplit = this.fastestCumTimes[controlIndex] - this.fastestCumTimes[controlIndex - 1];
        var timesBehind = selectedCompetitors.map(function (comp) { var compSplit = comp.getSplitTimeTo(controlIndex); return (compSplit === null) ? null : compSplit - fastestSplit; });
        return timesBehind;
    };

    /**
    * Returns an array of the the time losses of the selected competitors at
    * the given control.
    * @param {Number} controlIndex - Index of the given control.
    * @param {Array} indexes - Array of indexes of selected competitors.
    * @return {Array} Array of times in seconds that the given competitors are
    *     deemed to have lost at the given control.
    */
    Chart.prototype.getTimeLosses = function (controlIndex, indexes) {
        var selectedCompetitors = indexes.map(function (index) { return this.ageClassSet.allCompetitors[index]; }, this);
        var timeLosses = selectedCompetitors.map(function (comp) { return comp.getTimeLossAt(controlIndex); });
        return timeLosses;
    };
    
    /**
    * Updates the statistics text shown after the competitors.
    */
    Chart.prototype.updateCompetitorStatistics = function() {
        var selectedCompetitors = this.selectedIndexesOrderedByLastYValue.map(function (index) { return this.ageClassSet.allCompetitors[index]; }, this);
        var labelTexts = selectedCompetitors.map(function (comp) { return formatNameAndSuffix(comp.name, comp.getSuffix()); });
        
        if (this.currentControlIndex !== null && this.currentControlIndex > 0) {
            if (this.visibleStatistics.TotalTime) {
                var cumTimes = selectedCompetitors.map(function (comp) { return comp.getCumulativeTimeTo(this.currentControlIndex); }, this);
                var cumRanks = selectedCompetitors.map(function (comp) { return comp.getCumulativeRankTo(this.currentControlIndex); }, this);
                labelTexts = d3.zip(labelTexts, cumTimes, cumRanks)
                               .map(function(triple) { return triple[0] + formatTimeAndRank(triple[1], triple[2]); });
            }
                           
            if (this.visibleStatistics.SplitTime) {
                var splitTimes = selectedCompetitors.map(function (comp) { return comp.getSplitTimeTo(this.currentControlIndex); }, this);
                var splitRanks = selectedCompetitors.map(function (comp) { return comp.getSplitRankTo(this.currentControlIndex); }, this);
                labelTexts = d3.zip(labelTexts, splitTimes, splitRanks)
                               .map(function(triple) { return triple[0] + formatTimeAndRank(triple[1], triple[2]); });
            }
             
            if (this.visibleStatistics.BehindFastest) {
                var timesBehind = this.getTimesBehindFastest(this.currentControlIndex, this.selectedIndexesOrderedByLastYValue);
                labelTexts = d3.zip(labelTexts, timesBehind)
                               .map(function(pair) { return pair[0] + SPACER + formatTime(pair[1]); });
            }
             
            if (this.visibleStatistics.TimeLoss) {
                var timeLosses = this.getTimeLosses(this.currentControlIndex, this.selectedIndexesOrderedByLastYValue);
                labelTexts = d3.zip(labelTexts, timeLosses)
                               .map(function(pair) { return pair[0] + SPACER + formatTime(pair[1]); });
            }
        }
        
        // Update the current competitor data.
        this.currentCompetitorData.forEach(function (data, index) { data.label = labelTexts[index]; });
        
        // This data is already joined to the labels; just update the text.
        d3.selectAll("text.competitorLabel").text(function (data) { return data.label; });
    };

    /**
    * Returns a tick-formatting function that formats the label of a tick on the
    * top X-axis.
    *
    * The function returned is suitable for use with the D3 axis.tickFormat method.
    *
    * @returns {function} Tick-formatting function.
    */
    Chart.prototype.getTickFormatter = function () {
        var outerThis = this;
        return function (value, idx) {
            return (idx === 0) ? getMessage("StartNameShort") : ((idx === outerThis.numControls + 1) ? getMessage("FinishNameShort") : idx.toString());
        };
    };

    /**
    * Get the width of a piece of text.
    * @param {string} text - The piece of text to measure the width of.
    * @returns {Number} The width of the piece of text, in pixels. 
    */
    Chart.prototype.getTextWidth = function (text) {
        return this.textSizeElement.text(text).node().getBBox().width;
    };

    /**
    * Gets the height of a piece of text.
    *
    * @param {string} text - The piece of text to measure the height of.
    * @returns {Number} The height of the piece of text, in pixels.
    */
    Chart.prototype.getTextHeight = function (text) {
        return this.textSizeElement.text(text).node().getBBox().height;
    };

    /**
    * Return the maximum width of the end-text shown to the right of the graph.
    *
    * This function considers only the competitors whose indexes are in the
    * list given.  This method returns zero if the list is empty.
    * @returns {Number} Maximum width of text, in pixels.
    */
    Chart.prototype.getMaxGraphEndTextWidth = function () {
        if (this.selectedIndexes.length === 0) {
            // No competitors selected.  Avoid problems caused by trying to
            // find the maximum of an empty array.
            return 0;
        } else {
            var nameWidths = this.selectedIndexes.map(function (index) {
                var comp = this.ageClassSet.allCompetitors[index];
                return this.getTextWidth(formatNameAndSuffix(comp.name, comp.getSuffix()));
            }, this);
            return d3.max(nameWidths) + this.determineMaxStatisticTextWidth();
        }
    };

    /**
    * Return the maximum width of a piece of time and rank text shown to the right
    * of each competitor 
    * @param {string} timeFuncName - Name of the function to call to get the time
                                     data.
    * @param {string} rankFuncName - Name of the function to call to get the rank
                                     data.
    * @returns {Number} Maximum width of split-time and rank text, in pixels.
    */
    Chart.prototype.getMaxTimeAndRankTextWidth = function(timeFuncName, rankFuncName) {
        var maxTime = 0;
        var maxRank = 0;
        
        var selectedCompetitors = this.selectedIndexes.map(function (index) { return this.ageClassSet.allCompetitors[index]; }, this);
        
        d3.range(1, this.numControls + 2).forEach(function (controlIndex) {
            var times = selectedCompetitors.map(function (comp) { return comp[timeFuncName](controlIndex); });
            maxTime = Math.max(maxTime, d3.max(times.filter(isNotNull)));
            
            var ranks = selectedCompetitors.map(function (comp) { return comp[rankFuncName](controlIndex); });
            maxRank = Math.max(maxRank, d3.max(ranks.filter(isNotNull)));
        });
        
        var text = formatTimeAndRank(maxTime, maxRank);
        return this.getTextWidth(text);
    };

    /**
    * Return the maximum width of the split-time and rank text shown to the right
    * of each competitor 
    * @returns {Number} Maximum width of split-time and rank text, in pixels.
    */
    Chart.prototype.getMaxSplitTimeAndRankTextWidth = function() {
        return this.getMaxTimeAndRankTextWidth("getSplitTimeTo", "getSplitRankTo");
    };

    /**
    * Return the maximum width of the cumulative time and cumulative-time rank text
    * shown to the right of each competitor 
    * @returns {Number} Maximum width of cumulative time and cumulative-time rank text, in
    *                   pixels.
    */
    Chart.prototype.getMaxCumulativeTimeAndRankTextWidth = function() {
        return this.getMaxTimeAndRankTextWidth("getCumulativeTimeTo", "getCumulativeRankTo");
    };

    /**
    * Return the maximum width of the behind-fastest time shown to the right of
    * each competitor 
    * @returns {Number} Maximum width of behind-fastest time rank text, in pixels.
    */
    Chart.prototype.getMaxTimeBehindFastestWidth = function() {
        var maxTime = 0;
        
        for (var controlIndex = 1; controlIndex <= this.numControls + 1; controlIndex += 1) {
            var times = this.getTimesBehindFastest(controlIndex, this.selectedIndexes);
            maxTime = Math.max(maxTime, d3.max(times.filter(isNotNull)));
        }
        
        return this.getTextWidth(SPACER + formatTime(maxTime));
    };

    /**
    * Return the maximum width of the behind-fastest time shown to the right of
    * each competitor 
    * @returns {Number} Maximum width of behind-fastest time rank text, in pixels.
    */
    Chart.prototype.getMaxTimeLossWidth = function() {
        var maxTime = 0;
        
        for (var controlIndex = 1; controlIndex <= this.numControls + 1; controlIndex += 1) {
            var times = this.getTimeLosses(controlIndex, this.selectedIndexes);
            maxTime = Math.max(maxTime, d3.max(times.filter(isNotNull)));
        }
        
        return this.getTextWidth(SPACER + formatTime(maxTime));
    };

    /**
    * Determines the maximum width of the statistics text at the end of the competitor.
    * @returns {Number} Maximum width of the statistics text, in pixels.
    */
    Chart.prototype.determineMaxStatisticTextWidth = function() {
        var maxWidth = 0;
        if (this.visibleStatistics.TotalTime) {
            maxWidth += this.getMaxCumulativeTimeAndRankTextWidth();
        }
        if (this.visibleStatistics.SplitTime) {
            maxWidth += this.getMaxSplitTimeAndRankTextWidth();
        }
        if (this.visibleStatistics.BehindFastest) {
            maxWidth += this.getMaxTimeBehindFastestWidth();
        }
        if (this.visibleStatistics.TimeLoss) {
            maxWidth += this.getMaxTimeLossWidth();
        }
        
        return maxWidth;
    };
    
    /**
    * Determines the maximum width of all of the visible start time labels.
    * If none are presently visible, zero is returned.
    * @param {object} chartData - Object containing the chart data.
    * @return {Number} Maximum width of a start time label.
    */
    Chart.prototype.determineMaxStartTimeLabelWidth = function (chartData) {
        var maxWidth;
        if (chartData.competitorNames.length > 0) {
            maxWidth = d3.max(chartData.competitorNames.map(function (name) { return this.getTextWidth("00:00:00 " + name); }, this));
        } else {
            maxWidth = 0;
        }
        
        return maxWidth;
    };

    /**
    * Creates the X and Y scales necessary for the chart and its axes.
    * @param {object} chartData - Chart data object.
    */
    Chart.prototype.createScales = function (chartData) {
        this.xScale = d3.scale.linear().domain(chartData.xExtent).range([0, this.contentWidth]);
        this.yScale = d3.scale.linear().domain(chartData.yExtent).range([0, this.contentHeight]);
        this.xScaleMinutes = d3.scale.linear().domain([chartData.xExtent[0] / 60, chartData.xExtent[1] / 60]).range([0, this.contentWidth]);
    };

    /**
    * Draw the background rectangles that indicate sections of the course
    * between controls.
    */
    Chart.prototype.drawBackgroundRectangles = function () {
        var rects = this.svgGroup.selectAll("rect")
                                 .data(d3.range(this.numControls + 1));

        var outerThis = this;

        rects.enter().append("rect");

        rects.attr("x", function (index) { return outerThis.xScale(outerThis.referenceCumTimes[index]); })
             .attr("y", 0)
             .attr("width", function (index) { return outerThis.xScale(outerThis.referenceCumTimes[index + 1] - outerThis.referenceCumTimes[index]); })
             .attr("height", this.contentHeight)
             .attr("class", function (index) { return (index % 2 === 0) ? "background1" : "background2"; });

        rects.exit().remove();
    };
    
    /**
    * Returns a function used to format tick labels on the Y-axis.
    *
    * If start times are to be shown (i.e. for the race graph), then the Y-axis
    * values are start times.  We format these as times, as long as there isn't
    * a competitor's start time too close to it.
    *
    * For other graph types, this method returns null, which tells d3 to use
    * its default tick formatter.
    * 
    * @param {object} chartData - The chart data to read start times from.
    */
    Chart.prototype.determineYAxisTickFormatter = function (chartData) {
        if (this.isRaceGraph) {
            // Assume column 0 of the data is the start times.
            // However, beware that there might not be any data.
            var startTimes = (chartData.dataColumns.length === 0) ? [] : chartData.dataColumns[0].ys;
            if (startTimes.length === 0) {
                // No start times - draw all tick marks.
                return function (time) { return formatTime(time * 60); };
            } else {
                // Some start times are to be drawn - only draw tick marks if
                // they are far enough away from competitors.
                var yScale = this.yScale;
                return function (time) {
                    var nearestOffset = d3.min(startTimes.map(function (startTime) { return Math.abs(yScale(startTime) - yScale(time)); }));
                    return (nearestOffset >= MIN_COMPETITOR_TICK_MARK_DISTANCE) ? formatTime(Math.round(time * 60)) : "";
                };
            }
        } else {
            // Use the default d3 tick formatter.
            return null;
        }
    };

    /**
    * Draw the chart axes.
    * @param {String} yAxisLabel - The label to use for the Y-axis.
    * @param {object} chartData - The chart data to use.
    */
    Chart.prototype.drawAxes = function (yAxisLabel, chartData) {
    
        var tickFormatter = this.determineYAxisTickFormatter(chartData);
        
        var xAxis = d3.svg.axis()
                          .scale(this.xScale)
                          .orient("top")
                          .tickFormat(this.getTickFormatter())
                          .tickValues(this.referenceCumTimes);

        var yAxis = d3.svg.axis()
                          .scale(this.yScale)
                          .tickFormat(tickFormatter)
                          .orient("left");
                     
        var lowerXAxis = d3.svg.axis()
                               .scale(this.xScaleMinutes)
                               .orient("bottom");

        this.svgGroup.selectAll("g.axis").remove();

        this.svgGroup.append("g")
                     .attr("class", "x axis")
                     .call(xAxis);

        this.svgGroup.append("g")
                     .attr("class", "y axis")
                     .call(yAxis)
                     .append("text")
                     .attr("transform", "rotate(-90)")
                     .attr("x", -(this.contentHeight - 6))
                     .attr("y", 6)
                     .attr("dy", ".71em")
                     .style("text-anchor", "start")
                     .text(yAxisLabel);

        this.svgGroup.append("g")
                     .attr("class", "x axis")
                     .attr("transform", "translate(0," + this.contentHeight + ")")                     
                     .call(lowerXAxis)
                     .append("text")
                     .attr("x", 60)
                     .attr("y", -5)
                     .style("text-anchor", "start")
                     .text(getMessage("LowerXAxisChartLabel"));
    };
    
    /**
    * Draw the lines on the chart.
    * @param {Array} chartData - Array of chart data.
    */
    Chart.prototype.drawChartLines = function (chartData) {
        var outerThis = this;
        var lineFunctionGenerator = function (selCompIdx) {
            if (chartData.dataColumns.every(function (col) { return col.ys[selCompIdx] === null; })) {
                // This competitor's entire row is null, so there's no data to
                // draw.  WebKit will report an error ('Error parsing d=""') if
                // no points on the line are defined, as will happen in this
                // case, so we substitute a single zero point instead.
                return d3.svg.line()
                             .x(0)
                             .y(0)
                             .defined(function (d, i) { return i === 0; });
            }
            else {
                return d3.svg.line()
                             .x(function (d) { return outerThis.xScale(d.x); })
                             .y(function (d) { return outerThis.yScale(d.ys[selCompIdx]); })
                             .defined(function (d) { return d.ys[selCompIdx] !== null; })
                             .interpolate("linear");
            }
        };
        
        var graphLines = this.svgGroup.selectAll("path.graphLine")
                                      .data(d3.range(this.numLines));

        graphLines.enter()
                  .append("path")
                  .append("title");

        graphLines.attr("d", function (selCompIdx) { return lineFunctionGenerator(selCompIdx)(chartData.dataColumns); })
                  .attr("stroke", function (selCompIdx) { return colours[outerThis.selectedIndexes[selCompIdx] % colours.length]; })
                  .attr("class", function (selCompIdx) { return "graphLine competitor" + outerThis.selectedIndexes[selCompIdx]; })
                  .on("mouseenter", function (selCompIdx) { outerThis.highlight(outerThis.selectedIndexes[selCompIdx]); })
                  .on("mouseleave", function () { outerThis.unhighlight(); })
                  .select("title")
                  .text(function (selCompIdx) { return chartData.competitorNames[selCompIdx]; });

        graphLines.exit().remove();
    };

    /**
    * Highlights the competitor with the given index.
    * @param {Number} competitorIdx - The index of the competitor to highlight.
    */
    Chart.prototype.highlight = function (competitorIdx) {
        this.svg.selectAll("path.graphLine.competitor" + competitorIdx).classed("selected", true);
        this.svg.selectAll("line.competitorLegendLine.competitor" + competitorIdx).classed("selected", true);
        this.svg.selectAll("text.competitorLabel.competitor" + competitorIdx).classed("selected", true);
        this.svg.selectAll("text.startLabel.competitor" + competitorIdx).classed("selected", true);
    };

    /**
    * Removes any competitor-specific higlighting.
    */
    Chart.prototype.unhighlight = function () {
        this.svg.selectAll("path.graphLine.selected").classed("selected", false);
        this.svg.selectAll("line.competitorLegendLine.selected").classed("selected", false);
        this.svg.selectAll("text.competitorLabel.selected").classed("selected", false);
        this.svg.selectAll("text.startLabel.selected").classed("selected", false);
    };

    /**
    * Draws the start-time labels for the currently-selected competitors.
    * @param {object} chartData - The chart data that contains the start offsets.
    */ 
    Chart.prototype.drawCompetitorStartTimeLabels = function (chartData) {
        var startColumn = chartData.dataColumns[0];
        var outerThis = this;
        
        var startLabels = this.svgGroup.selectAll("text.startLabel").data(this.selectedIndexes);
        
        startLabels.enter().append("text");
        
        startLabels.attr("x", -7)
                   .attr("y", function (_compIndex, selCompIndex) { return outerThis.yScale(startColumn.ys[selCompIndex]) + outerThis.getTextHeight(chartData.competitorNames[selCompIndex]) / 4; })
                   .attr("class", function (compIndex) { return "startLabel competitor" + compIndex; })
                   .on("mouseenter", function (compIndex) { outerThis.highlight(compIndex); })
                   .on("mouseleave", function () { outerThis.unhighlight(); })
                   .text(function (_compIndex, selCompIndex) { return formatTime(Math.round(startColumn.ys[selCompIndex] * 60)) + " " + chartData.competitorNames[selCompIndex]; });
        
        startLabels.exit().remove();
    };
    
    /**
    * Removes all of the competitor start-time labels from the chart.
    */ 
    Chart.prototype.removeCompetitorStartTimeLabels = function () {
        this.svgGroup.selectAll("text.startLabel").remove();
    };

    /**
    * Adjust the locations of the legend labels downwards so that two labels
    * do not overlap.
    */
    Chart.prototype.adjustCompetitorLegendLabelsDownwardsIfNecessary = function () {
        for (var i = 1; i < this.numLines; i += 1) {
            var prevComp = this.currentCompetitorData[i - 1];
            var thisComp = this.currentCompetitorData[i];
            if (thisComp.y < prevComp.y + prevComp.textHeight) {
                thisComp.y = prevComp.y + prevComp.textHeight;
            }
        }
    };

    /**
    * Adjusts the locations of the legend labels upwards so that as many as
    * possible can fit on the chart.  If all competitor labels are already on
    * the chart, then this method does nothing.
    *
    * This method does not move off the chart any label that is currently on
    * the chart.
    *
    * @param {Number} minLastY - The minimum Y-coordinate of the lowest label.
    */
    Chart.prototype.adjustCompetitorLegendLabelsUpwardsIfNecessary = function (minLastY) {
        if (this.numLines > 0 && this.currentCompetitorData[this.numLines - 1].y > this.contentHeight) {
            // The list of competitors runs off the bottom.
            // Put the last competitor at the bottom, or at its minimum
            // Y-offset, whichever is larger, and move all labels up as
            // much as we can.
            this.currentCompetitorData[this.numLines - 1].y = Math.max(minLastY, this.contentHeight);
            for (var i = this.numLines - 2; i >= 0; i -= 1) {
                var nextComp = this.currentCompetitorData[i + 1];
                var thisComp = this.currentCompetitorData[i];
                if (thisComp.y + thisComp.textHeight > nextComp.y) {
                    thisComp.y = nextComp.y - thisComp.textHeight;
                } else {
                    // No more adjustments need to be made.
                    break;
                }
            }
        }    
    };
    
    /**
    * Draw legend labels to the right of the chart.
    * @param {object} chartData - The chart data that contains the final time offsets.
    */
    Chart.prototype.drawCompetitorLegendLabels = function (chartData) {
        
        var minLastY = 0;
        if (chartData.dataColumns.length === 0) {
            this.currentCompetitorData = [];
        } else {
            var finishColumn = chartData.dataColumns[chartData.dataColumns.length - 1];
            this.currentCompetitorData = d3.range(this.numLines).map(function (i) {
                var competitorIndex = this.selectedIndexes[i];
                var name = this.ageClassSet.allCompetitors[competitorIndex].name;
                var textHeight = this.getTextHeight(name);
                minLastY += textHeight;
                return {
                    label: formatNameAndSuffix(name, this.ageClassSet.allCompetitors[competitorIndex].getSuffix()),
                    textHeight: textHeight,
                    y: (finishColumn.ys[i] === null) ? null : this.yScale(finishColumn.ys[i]),
                    colour: colours[competitorIndex % colours.length],
                    index: competitorIndex
                };
            }, this);
            
            minLastY -= this.currentCompetitorData[this.numLines - 1].textHeight;
            
            // Draw the mispunchers at the bottom of the chart, with the last
            // one of them at the bottom.
            var lastMispuncherY = null;
            for (var selCompIdx = this.numLines - 1; selCompIdx >= 0; selCompIdx -= 1) {
                if (this.currentCompetitorData[selCompIdx].y === null) {
                    this.currentCompetitorData[selCompIdx].y = (lastMispuncherY === null) ? this.contentHeight : lastMispuncherY - this.currentCompetitorData[selCompIdx].textHeight;
                    lastMispuncherY = this.currentCompetitorData[selCompIdx].y;
                }
            }
        }
        
        // Sort by the y-offset values, which doesn't always agree with the end
        // positions of the competitors.
        this.currentCompetitorData.sort(function (a, b) { return a.y - b.y; });
        
        this.selectedIndexesOrderedByLastYValue = this.currentCompetitorData.map(function (comp) { return comp.index; });

        this.adjustCompetitorLegendLabelsDownwardsIfNecessary();
        
        this.adjustCompetitorLegendLabelsUpwardsIfNecessary(minLastY);

        var legendLines = this.svgGroup.selectAll("line.competitorLegendLine").data(this.currentCompetitorData);
        legendLines.enter()
                   .append("line");

        var outerThis = this;
        legendLines.attr("x1", this.contentWidth + 1)
                   .attr("y1", function (data) { return data.y; })
                   .attr("x2", this.contentWidth + LEGEND_LINE_WIDTH + 1)
                   .attr("y2", function (data) { return data.y; })
                   .attr("stroke", function (data) { return data.colour; })
                   .attr("class", function (data) { return "competitorLegendLine competitor" + data.index; })
                   .on("mouseenter", function (data) { outerThis.highlight(data.index); })
                   .on("mouseleave", function () { outerThis.unhighlight(); });

        legendLines.exit().remove();

        var labels = this.svgGroup.selectAll("text.competitorLabel").data(this.currentCompetitorData);
        labels.enter()
              .append("text");

        labels.attr("x", this.contentWidth + LEGEND_LINE_WIDTH + 2)
              .attr("y", function (data) { return data.y + data.textHeight / 4; })
              .attr("class", function (data) { return "competitorLabel competitor" + data.index; })
              .on("mouseenter", function (data) { outerThis.highlight(data.index); })
              .on("mouseleave", function () { outerThis.unhighlight(); })
              .text(function (data) { return data.label; });

        labels.exit().remove();
    };

    /**
    * Adjusts the computed values for the content size of the chart.
    *
    * This method should be called after any of the following occur:
    * (1) the overall size of the chart changes.
    * (2) the currently-selected set of indexes changes
    * (3) the chart data is set.
    * If you find part of the chart is missing sometimes, chances are you've
    * omitted a necessary call to this method.
    */
    Chart.prototype.adjustContentSize = function () {
        // Extra length added to the maximum start-time label width to
        // include the lengths of the Y-axis ticks.
        var EXTRA_MARGIN = 8;
        var maxTextWidth = this.getMaxGraphEndTextWidth();
        this.setLeftMargin(Math.max(this.maxStartTimeLabelWidth + EXTRA_MARGIN, MARGIN.left));
        this.contentWidth = Math.max(this.overallWidth - this.currentLeftMargin - MARGIN.right - maxTextWidth - (LEGEND_LINE_WIDTH + 2), 100);
        this.contentHeight = Math.max(this.overallHeight - MARGIN.top - MARGIN.bottom, 100);
    };

    /**
    * Sets the overall size of the chart control, including margin, axes and legend labels.
    * @param {Number} overallWidth - Overall width
    * @param {Number} overallHeight - Overall height
    */
    Chart.prototype.setSize = function (overallWidth, overallHeight) {
        this.overallWidth = overallWidth;
        this.overallHeight = overallHeight;
        $(this.svg.node()).width(overallWidth).height(overallHeight);
        this.adjustContentSize();
    };

    /**
    * Clears the graph by removing all controls from it.
    */
    Chart.prototype.clearGraph = function () {
        this.svgGroup.selectAll("*").remove();
    };
    
    /**
    * Removes the warning panel, if it is still shown.
    */
    Chart.prototype.clearWarningPanel = function () {
        if (this.warningPanel !== null) {
            this.warningPanel.remove();
            this.warningPanel = null;
        }
    };
    
    /**
    * Shows a warning panel over the chart, with the given message.
    * @param message The message to show.
    */
    Chart.prototype.showWarningPanel = function (message) {
        this.clearWarningPanel();
        this.warningPanel = d3.select(this.parent).append("div")
                                                  .classed("warningPanel", true);
        this.warningPanel.text(message);
        
        var panelWidth = $(this.warningPanel.node()).width();
        var panelHeight = $(this.warningPanel.node()).height();
        this.warningPanel.style("left", (($(this.parent).width() - panelWidth) / 2) + "px")
                         .style("top", ((this.overallHeight - panelHeight) / 2) + "px");
    };
    
    /**
    * Draws the chart.
    * @param {object} data - Object that contains various chart data.  This
    *     must contain the following properties:
    *     * chartData {Object} - the data to plot on the chart
    *     * eventData {SplitsBrowser.Model.Event} - the overall Event object.
    *     * ageClassSet {SplitsBrowser.Model.Event} - the age-class set.
    *     * referenceCumTimes {Array} - Array of cumulative split times of the
    *       'reference'.
    *     * fastestCumTimes {Array} - Array of cumulative times of the
    *       imaginary 'fastest' competitor.
    * @param {Array} selectedIndexes - Array of indexes of selected competitors
    *                (0 in this array means the first competitor is selected, 1
    *                means the second is selected, and so on.)
    * @param {Array} visibleStatistics - Array of boolean flags indicating whether
    *                                    certain statistics are visible.
    * @param {Object} chartType - The type of chart being drawn.
    */
    Chart.prototype.drawChart = function (data, selectedIndexes, visibleStatistics, chartType) {
        var chartData = data.chartData;
        this.numControls = chartData.numControls;
        this.numLines = chartData.competitorNames.length;
        this.selectedIndexes = selectedIndexes;
        this.referenceCumTimes = data.referenceCumTimes;
        this.fastestCumTimes = data.fastestCumTimes;
        this.eventData = data.eventData;
        this.ageClassSet = data.ageClassSet;
        this.hasControls = data.ageClassSet.getCourse().hasControls();
        this.isRaceGraph = chartType.isRaceGraph;
        this.minViewableControl = chartType.minViewableControl;
        this.visibleStatistics = visibleStatistics;
        
        this.maxStatisticTextWidth = this.determineMaxStatisticTextWidth();
        this.maxStartTimeLabelWidth = (this.isRaceGraph) ? this.determineMaxStartTimeLabelWidth(chartData) : 0;
        this.clearWarningPanel();
        this.adjustContentSize();
        this.createScales(chartData);
        this.drawBackgroundRectangles();
        this.drawAxes(getMessage(chartType.yAxisLabelKey), chartData);
        this.drawChartLines(chartData);
        this.drawCompetitorLegendLabels(chartData);
        this.removeControlLine();
        if (this.isRaceGraph) {
            this.drawCompetitorStartTimeLabels(chartData);
        } else {
            this.removeCompetitorStartTimeLabels();
        }
    };
    
    /**
    * Clears the chart and shows a warning message instead.
    * @param {String} message - The text of the warning message to show.
    */
    Chart.prototype.clearAndShowWarning = function (message) {
        this.numControls = 0;
        this.numLines = 0;
        
        var dummyChartData = {
            dataColumns: [],
            competitorNames: [],
            numControls: 0,
            xExtent: [0, 3600],
            yExtent: [0, 1]
        };
        
        this.maxStatisticTextWidth = 0;
        this.maxStartTimeWidth = 0;
        this.clearGraph();
        this.adjustContentSize();
        this.referenceCumTimes = [0];
        this.createScales(dummyChartData);
        this.drawAxes("", dummyChartData);
        this.showWarningPanel(message);
    };
    
    SplitsBrowser.Controls.Chart = Chart;
})();


(function () {
    "use strict";
    
    var formatTime = SplitsBrowser.formatTime;
    var compareCompetitors = SplitsBrowser.Model.compareCompetitors;
    var getMessage = SplitsBrowser.getMessage;
    var getMessageWithFormatting = SplitsBrowser.getMessageWithFormatting;
    
    var NON_BREAKING_SPACE_CHAR = "\u00a0";

    /**
    * A control that shows an entire table of results.
    * @constructor
    * @param {HTMLElement} parent - The parent element to add this control to.
    */
    var ResultsTable = function (parent) {
        this.parent = parent;
        this.ageClass = null;
        this.div = null;
        this.headerSpan = null;
        this.table = null;
        this.buildTable();
    };
    
    /**
    * Build the results table.
    */
    ResultsTable.prototype.buildTable = function () {
        this.div = d3.select(this.parent).append("div")
                                         .attr("id", "resultsTableContainer");
                                         
        this.headerSpan = this.div.append("div")
                                  .append("span")
                                  .classed("resultsTableHeader", true);
                                  
        this.table = this.div.append("table")
                             .classed("resultsTable", true);
                             
        this.table.append("thead")
                  .append("tr");
                  
        this.table.append("tbody");
    };
    
    /**
    * Populates the contents of the table with the age-class data.
    */
    ResultsTable.prototype.populateTable = function () {
        var headerText = this.ageClass.name + ", ";
        if (this.ageClass.numControls === 1) {
            headerText += getMessage("ResultsTableHeaderSingleControl");
        } else {
            headerText += getMessageWithFormatting("ResultsTableHeaderMultipleControls", {"$$NUM$$": this.ageClass.numControls});
        }

        var course = this.ageClass.course;
        if (course.length !== null) {
            headerText += ", " + getMessageWithFormatting("ResultsTableHeaderCourseLength", {"$$DISTANCE$$": course.length.toFixed(1)});
        }
        if (course.climb !== null) {
            headerText += ", " + getMessageWithFormatting("ResultsTableHeaderClimb", {"$$CLIMB$$": course.climb});
        }
        
        this.headerSpan.text(headerText);
        
        var headerCellData = [
            getMessage("ResultsTableHeaderControlNumber"),
            getMessage("ResultsTableHeaderName"),
            getMessage("ResultsTableHeaderTime")
        ];
        
        var controls = this.ageClass.course.controls;
        if (controls === null) {
            headerCellData = headerCellData.concat(d3.range(1, this.ageClass.numControls + 1));
        } else {
            headerCellData = headerCellData.concat(controls.map(function (control, index) {
                return (index + 1) + NON_BREAKING_SPACE_CHAR + "(" + control + ")";
            }));
        }
            
        headerCellData.push(getMessage("FinishName"));
        
        var headerCells = this.table.select("thead tr")
                                    .selectAll("th")
                                    .data(headerCellData);
                                                       
        headerCells.enter().append("th");
        headerCells.text(function (header) { return header; });
        headerCells.exit().remove();
        
        var tableBody = this.table.select("tbody");
        tableBody.selectAll("tr").remove();
        
        function addCell(tableRow, topLine, bottomLine, cssClass) {
            var cell = tableRow.append("td");
            cell.append("span").text(topLine);
            cell.append("br");
            cell.append("span").text(bottomLine);
            if (cssClass) {
                cell.classed(cssClass, true);
            }
        }
        
        var competitors = this.ageClass.competitors.slice(0);
        competitors.sort(compareCompetitors);
        
        var nonCompCount = 0;
        var rank = 0;
        competitors.forEach(function (competitor, index) {
            var tableRow = tableBody.append("tr");
            var numberCell = tableRow.append("td");
            if (competitor.isNonCompetitive) {
                numberCell.text(getMessage("NonCompetitiveShort"));
                nonCompCount += 1;
            } else if (competitor.completed()) {
                if (index === 0 || competitors[index - 1].totalTime !== competitor.totalTime) {
                    rank = index + 1 - nonCompCount;
                }
                
                numberCell.text(rank);
            }
            
            addCell(tableRow, competitor.name, competitor.club);
            addCell(tableRow, (competitor.completed()) ? formatTime(competitor.totalTime) : getMessage("MispunchedShort"), NON_BREAKING_SPACE_CHAR, "time");
            
            d3.range(1, this.ageClass.numControls + 2).forEach(function (controlNum) {
                addCell(tableRow, formatTime(competitor.getCumulativeTimeTo(controlNum)), formatTime(competitor.getSplitTimeTo(controlNum)), "time");
            });
        }, this);
    };
    
    /**
    * Sets the class whose data is displayed.
    * @param {SplitsBrowser.Model.AgeClass} ageClass - The class displayed.
    */
    ResultsTable.prototype.setClass = function (ageClass) {
        this.ageClass = ageClass;
        this.populateTable();
        if (this.div.style("display") !== "none") {
            this.adjustTableCellWidths();
        }
    };
    
    /**
    * Adjust the widths of the time table cells so that they have the same width.
    */
    ResultsTable.prototype.adjustTableCellWidths = function () {
        var lastCellOnFirstRow = d3.select("tbody tr td:last-child").node();
        $("tbody td.time").width($(lastCellOnFirstRow).width());
    };
    
    /**
    * Shows the table of results.
    */
    ResultsTable.prototype.show = function () {
        this.div.style("display", null);
        this.adjustTableCellWidths();
    };
    
    /**
    * Hides the table of results.
    */
    ResultsTable.prototype.hide = function () {
        this.div.style("display", "none");
    };
    
    SplitsBrowser.Controls.ResultsTable = ResultsTable;
})();

(function () {
    "use strict";
    // Delay in milliseconds between a resize event being triggered and the
    // page responding to it.
    // (Resize events tend to come more than one at a time; if a resize event
    // comes in while a previous event is waiting, the previous event is
    // cancelled.)
    var RESIZE_DELAY_MS = 100;

    // ID of the div that contains the competitor list.
    // Must match that used in styles.css.
    var COMPETITOR_LIST_CONTAINER_ID = "competitorListContainer";
    
    var ClassSelector = SplitsBrowser.Controls.ClassSelector;
    var ChartTypeSelector = SplitsBrowser.Controls.ChartTypeSelector;
    var ComparisonSelector = SplitsBrowser.Controls.ComparisonSelector;
    var StatisticsSelector = SplitsBrowser.Controls.StatisticsSelector;
    var CompetitorListBox = SplitsBrowser.Controls.CompetitorListBox;
    var Chart = SplitsBrowser.Controls.Chart;
    var ResultsTable = SplitsBrowser.Controls.ResultsTable;
    var getMessage = SplitsBrowser.getMessage;
    var getMessageWithFormatting = SplitsBrowser.getMessageWithFormatting;
    
    /**
    * Enables or disables a control, by setting or clearing an HTML "disabled"
    * attribute as necessary.
    * @param {d3.selection} control - d3 selection containing the control.
    * @param {boolean} isEnabled - Whether the control is enabled.
    */
    function enableControl(control, isEnabled) {
        control.node().disabled = !isEnabled;
    }
    
    /**
    * The 'overall' viewer object responsible for viewing the splits graph.
    * @constructor
    * @param {String|HTMLElement|undefined} - Optional HTML element that forms
    *     a 'banner' across the top of the page.  This can be specified by a
    *     CSS selector or the HTML element itself.
    */
    var Viewer = function (topDiv) {
    
        this.eventData = null;
        this.classes = null;
        this.currentClasses = [];
        this.currentIndexes = null;
        this.chartData = null;
        this.referenceCumTimes = null;
        this.fastestCumTimes = null;
        this.previousCompetitorList = [];
        this.topDivHeight = (topDiv && $(topDiv).length > 0) ? $(topDiv).height() : 0;
        
        this.isChartEnabled = false;

        this.selection = null;
        this.ageClassSet = null;
        this.classSelector = null;
        this.statisticsSelector = null;
        this.competitorListBox = null;
        this.chart = null;
        this.topPanel = null;
        this.mainPanel = null;
        this.buttonsPanel = null;
        this.competitorListContainer = null;
        
        this.currentResizeTimeout = null;
    };
    
    /**
    * Pops up an alert box informing the user that the race graph cannot be
    * chosen as the start times are missing.
    */ 
    function alertRaceGraphDisabledAsStartTimesMissing() {
        alert(getMessage("RaceGraphDisabledAsStartTimesMissing"));
    }
    
    /**
    * Enables or disables the race graph option in the chart type selector
    * depending on whether all visible competitors have start times.
    */
    Viewer.prototype.enableOrDisableRaceGraph = function () {
        var anyStartTimesMissing = this.ageClassSet.allCompetitors.some(function (competitor) { return competitor.lacksStartTime(); });
        this.chartTypeSelector.setRaceGraphDisabledNotifier((anyStartTimesMissing) ? alertRaceGraphDisabledAsStartTimesMissing : null);
    };
    
    /**
    * Sets the classes that the viewer can view.
    * @param {SplitsBrowser.Model.Event} eventData - All event data loaded.
    */
    Viewer.prototype.setEvent = function (eventData) {
        this.eventData = eventData;
        this.classes = eventData.classes;
        if (this.classSelector !== null) {
            this.classSelector.setClasses(this.classes);
        }
    };

    /**
    * Draws the logo in the top panel.
    */
    Viewer.prototype.drawLogo = function () {
        var logoSvg = this.topPanel.append("svg")
                                   .style("float", "left");

        logoSvg.style("width", "19px")
               .style("height", "19px")
               .style("margin-bottom", "-3px")
               .style("margin-right", "20px");
               
        logoSvg.append("rect")
               .attr("x", "0")
               .attr("y", "0")
               .attr("width", "19")
               .attr("height", "19")
               .attr("fill", "white");
         
        logoSvg.append("polygon")
               .attr("points", "0,19 19,0 19,19")
               .attr("fill", "red");
               
        logoSvg.append("polyline")
               .attr("points", "0.5,0.5 0.5,18.5 18.5,18.5 18.5,0.5 0.5,0.5 0.5,18.5")
               .attr("stroke", "black")
               .attr("fill", "none");
               
        logoSvg.append("polyline")
               .attr("points", "1,12 5,8 8,14 17,11")
               .attr("fill", "none")
               .attr("stroke", "blue")
               .attr("stroke-width", "2");
                                   
        logoSvg.selectAll("*")
               .append("title")
               .text(getMessageWithFormatting("ApplicationVersion", {"$$VERSION$$": SplitsBrowser.Version}));
    };

    /**
    * Adds a spacer between controls on the top row.
    */
    Viewer.prototype.addSpacer = function () {
        this.topPanel.append("div").classed("topRowSpacer", true);    
    };
    
    /**
    * Adds the class selector control to the top panel.
    */
    Viewer.prototype.addClassSelector = function () {
        this.classSelector = new ClassSelector(this.topPanel.node());
        if (this.classes !== null) {
            this.classSelector.setClasses(this.classes);
        }
    };
    
    /**
    * Adds the chart-type selector to the top panel.
    */
    Viewer.prototype.addChartTypeSelector = function () {
        var types = SplitsBrowser.Model.ChartTypes;
        var chartTypes = [types.SplitsGraph, types.RaceGraph, types.PositionAfterLeg,
                          types.SplitPosition, types.PercentBehind, types.ResultsTable];
        
        this.chartTypeSelector = new ChartTypeSelector(this.topPanel.node(), chartTypes);
        
        this.chartType = this.chartTypeSelector.getChartType();    
    };
    
    /**
    * Adds the comparison selector to the top panel.
    */
    Viewer.prototype.addComparisonSelector = function () {
        this.comparisonSelector = new ComparisonSelector(this.topPanel.node(), function (message) { alert(message); });
        if (this.classes !== null) {
            this.comparisonSelector.setClasses(this.classes);
        }
        
        this.comparisonFunction = this.comparisonSelector.getComparisonFunction();    
    };
    
    /**
    * Adds the list of competitors, and the buttons, to the page.
    */
    Viewer.prototype.addCompetitorList = function () {
        this.competitorListContainer = this.mainPanel.append("div")
                                                     .attr("id", COMPETITOR_LIST_CONTAINER_ID);
                                               
        this.buttonsPanel = this.competitorListContainer.append("div");
                           
        var outerThis = this;
        this.allButton = this.buttonsPanel.append("button")
                                          .text(getMessage("SelectAllCompetitors"))
                                          .style("width", "50%")
                                          .on("click", function () { outerThis.selectAll(); });
                        
        this.noneButton = this.buttonsPanel.append("button")
                                           .text(getMessage("SelectNoCompetitors"))
                                           .style("width", "50%")
                                           .on("click", function () { outerThis.selectNone(); });
                        
        this.buttonsPanel.append("br");
                        
        this.crossingRunnersButton = this.buttonsPanel.append("button")
                                                      .text(getMessage("SelectCrossingRunners"))
                                                      .style("width", "100%")
                                                      .on("click", function () { outerThis.selectCrossingRunners(); })
                                                      .style("display", "none");

        this.competitorListBox = new CompetitorListBox(this.competitorListContainer.node());
    };

    /**
    * Construct the UI inside the HTML body.
    */
    Viewer.prototype.buildUi = function () {
        var body = d3.select("body");
        
        this.topPanel = body.append("div");
        
        this.drawLogo();
        this.addClassSelector();
        this.addSpacer();
        this.addChartTypeSelector();
        this.addSpacer();
        this.addComparisonSelector();
        
        this.statisticsSelector = new StatisticsSelector(this.topPanel.node());

        // Add an empty div to clear the floating divs and ensure that the
        // top panel 'contains' all of its children.
        this.topPanel.append("div")
                     .style("clear", "both");
        
        this.mainPanel = body.append("div");
                             
        this.addCompetitorList();
        this.chart = new Chart(this.mainPanel.node());
        
        this.resultsTable = new ResultsTable(body.node());
        this.resultsTable.hide();
        
        var outerThis = this;
        this.classSelector.registerChangeHandler(function (indexes) { outerThis.selectClasses(indexes); });
        this.chartTypeSelector.registerChangeHandler(function (chartType) { outerThis.selectChartType(chartType); });
        this.comparisonSelector.registerChangeHandler(function (comparisonFunc) { outerThis.selectComparison(comparisonFunc); });
           
        $(window).resize(function () { outerThis.handleWindowResize(); });
        
        // Disable text selection anywhere.
        // This is for the benefit of IE9, which doesn't support the
        // -ms-user-select CSS style.  IE10, IE11 do support -ms-user-select
        // and other browsers have their own vendor-specific CSS styles for
        // this, and in these browsers this event handler never gets called.
        $("body").bind("selectstart", function () { return false; });
    };

    /**
    * Select all of the competitors.
    */
    Viewer.prototype.selectAll = function () {
        this.selection.selectAll();
    };

    /**
    * Select none of the competitors.
    */
    Viewer.prototype.selectNone = function () {
        this.selection.selectNone();
    };

    /**
    * Select all of the competitors that cross the unique selected competitor.
    */
    Viewer.prototype.selectCrossingRunners = function () {
        this.selection.selectCrossingRunners(this.ageClassSet.allCompetitors); 
        if (this.selection.isSingleRunnerSelected()) {
            // Only a single runner is still selected, so nobody crossed the
            // selected runner.
            var competitorName = this.ageClassSet.allCompetitors[this.currentIndexes[0]].name;
            alert(getMessageWithFormatting("RaceGraphNoCrossingRunners", {"$$NAME$$": competitorName}));
        }
    };

    /**
     * Handle a resize of the window.
     */
    Viewer.prototype.handleWindowResize = function () {
        if (this.currentResizeTimeout !== null) {
            clearTimeout(this.currentResizeTimeout);
        }

        var outerThis = this;
        this.currentResizeTimeout = setTimeout(function() { outerThis.postResizeHook(); }, RESIZE_DELAY_MS);
    };
    
    /**
    * Resize the chart following a change of size of the chart.
    */
    Viewer.prototype.postResizeHook = function () {
        this.currentResizeTimeout = null;
        this.drawChart();
    };

    /**
    * Adjusts the size of the viewer.
    */
    Viewer.prototype.adjustSize = function () {
        // Margin around the body element.
        var horzMargin = parseInt($("body").css("margin-left"), 10) + parseInt($("body").css("margin-right"), 10);
        var vertMargin = parseInt($("body").css("margin-top"), 10) + parseInt($("body").css("margin-bottom"), 10);
        
        // Extra amount subtracted off of the width of the chart in order to
        // prevent wrapping, in units of pixels.
        // 2 to prevent wrapping when zoomed out to 33% in Chrome.
        var EXTRA_WRAP_PREVENTION_SPACE = 2;
        
        var bodyWidth = $(window).width() - horzMargin;
        var bodyHeight = $(window).height() - vertMargin - this.topDivHeight;

        $("body").width(bodyWidth).height(bodyHeight);
        
        var topPanelHeight = $(this.topPanel.node()).height();

        // Hide the chart before we adjust the width of the competitor list.
        // If the competitor list gets wider, the new competitor list and the
        // old chart may be too wide together, and so the chart wraps onto a
        // new line.  Even after shrinking the chart back down, there still
        // might not be enough horizontal space, because of the vertical
        // scrollbar.  So, hide the chart now, and re-show it later once we
        // know what size it should have.
        this.chart.hide();
        
        this.competitorListBox.setCompetitorList(this.ageClassSet.allCompetitors, (this.currentClasses.length > 1));
        
        var chartWidth = bodyWidth - this.competitorListBox.width() - EXTRA_WRAP_PREVENTION_SPACE;
        var chartHeight = bodyHeight - topPanelHeight;

        this.chart.setSize(chartWidth, chartHeight);
        this.chart.show();
        
        $(this.competitorListContainer.node()).height(bodyHeight - $(this.buttonsPanel.node()).height() - topPanelHeight);    
    };
    
    /**
    * Draw the chart using the current data.
    */
    Viewer.prototype.drawChart = function () {
        if (this.chartType.isResultsTable) {
            return;
        }
        
        this.adjustSize();
        
        this.currentVisibleStatistics = this.statisticsSelector.getVisibleStatistics();
        
        if (this.selectionChangeHandler !== null) {
            this.selection.deregisterChangeHandler(this.selectionChangeHandler);
        }
        
        if (this.statisticsChangeHandler !== null) {
            this.statisticsSelector.deregisterChangeHandler(this.statisticsChangeHandler);
        }
        
        var outerThis = this;
        
        this.selectionChangeHandler = function (indexes) {
            outerThis.currentIndexes = indexes;
            outerThis.enableOrDisableCrossingRunnersButton();
            outerThis.redraw();
        };

        this.selection.registerChangeHandler(this.selectionChangeHandler);
        
        this.statisticsChangeHandler = function (visibleStatistics) {
            outerThis.currentVisibleStatistics = visibleStatistics;
            outerThis.redraw();
        };
        
        this.statisticsSelector.registerChangeHandler(this.statisticsChangeHandler);

        var missedControls = this.ageClassSet.getControlsWithNoSplits();
        this.isChartEnabled = (missedControls.length === 0);
        this.updateControlEnabledness();
        if (this.isChartEnabled) {
            this.referenceCumTimes = this.comparisonFunction(this.ageClassSet);
            this.fastestCumTimes = this.ageClassSet.getFastestCumTimes();
            this.chartData = this.ageClassSet.getChartData(this.referenceCumTimes, this.currentIndexes, this.chartType);
            this.redrawChart();
        } else {
            var showAddendum = (this.ageClassSet.getCourse().getNumClasses() > this.ageClassSet.getNumClasses());
            var message = getMessageWithFormatting((showAddendum) ? "NoSplitsForControlTryOtherClasses" : "NoSplitsForControl", {"$$CONTROL$$": missedControls[0]});
            this.chart.clearAndShowWarning(message);
        }
    };

    /**
    * Redraws the chart using all of the current data.
    */ 
    Viewer.prototype.redrawChart = function () {
        var data = {
            chartData: this.chartData,
            eventData: this.eventData,
            ageClassSet: this.ageClassSet,
            referenceCumTimes: this.referenceCumTimes,
            fastestCumTimes: this.fastestCumTimes
        };
            
        this.chart.drawChart(data, this.currentIndexes, this.currentVisibleStatistics, this.chartType);
    };
    
    /**
    * Redraw the chart, possibly using new data.
    */
    Viewer.prototype.redraw = function () {
        if (!this.chartType.isResultsTable && this.isChartEnabled) {
            this.chartData = this.ageClassSet.getChartData(this.referenceCumTimes, this.currentIndexes, this.chartType);
            this.redrawChart();
        }
    };
    
    /**
    * Change the graph to show the classes with the given indexes.
    * @param {Number} classIndexes - The (zero-based) indexes of the classes.
    */
    Viewer.prototype.selectClasses = function (classIndexes) {
    
        if (this.selection === null) {
            this.selection = new SplitsBrowser.Model.CompetitorSelection(0);
            this.competitorListBox.setSelection(this.selection);
        } else {
            if (classIndexes.length > 0 && this.currentClasses.length > 0 && this.classes[classIndexes[0]] === this.currentClasses[0]) {
                // The 'primary' class hasn't changed, only the 'other' ones.
                // In this case we don't clear the selection.
            } else {
                this.selection.selectNone();
            }
        }
        
        this.currentIndexes = [];
        this.currentClasses = classIndexes.map(function (index) { return this.classes[index]; }, this);
        this.ageClassSet = new SplitsBrowser.Model.AgeClassSet(this.currentClasses);
        this.comparisonSelector.setAgeClassSet(this.ageClassSet);
        this.resultsTable.setClass(this.currentClasses[0]);
        this.drawChart();
        this.selection.migrate(this.previousCompetitorList, this.ageClassSet.allCompetitors);
        this.previousCompetitorList = this.ageClassSet.allCompetitors;
        this.enableOrDisableRaceGraph();
    };
    
    /**
    * Change the graph to compare against a different reference.
    * @param {Function} comparisonFunc - The function that returns the
    *      reference class data from the class data.
    */
    Viewer.prototype.selectComparison = function (comparisonFunc) {
        this.comparisonFunction = comparisonFunc;
        this.drawChart();
    };
    
    /**
    * Change the type of chart shown.
    * @param {Object} chartType - The type of chart to draw.
    */
    Viewer.prototype.selectChartType = function (chartType) {
        this.chartType = chartType;
        if (chartType.isResultsTable) {
            this.mainPanel.style("display", "none");
            this.resultsTable.show();
        } else {
            this.resultsTable.hide();
            this.mainPanel.style("display", null);
        }
        
        this.updateControlEnabledness();
        
        this.crossingRunnersButton.style("display", (chartType.isRaceGraph) ? null : "none");
        
        this.drawChart();
    };
    
    /**
    * Updates whether a number of controls are enabled.
    */
    Viewer.prototype.updateControlEnabledness = function () {
        this.classSelector.setOtherClassesEnabled(!this.chartType.isResultsTable);
        this.comparisonSelector.setEnabled(this.isChartEnabled && !this.chartType.isResultsTable);
        this.statisticsSelector.setEnabled(this.isChartEnabled && !this.chartType.isResultsTable);
        this.competitorListBox.setEnabled(this.isChartEnabled);
        enableControl(this.allButton, this.isChartEnabled);
        enableControl(this.noneButton, this.isChartEnabled);
        this.enableOrDisableCrossingRunnersButton();
    };
    
    /**
    * Enables or disables the crossing-runners button as appropriate.
    */
    Viewer.prototype.enableOrDisableCrossingRunnersButton = function () {
        enableControl(this.crossingRunnersButton, this.isChartEnabled && this.selection.isSingleRunnerSelected());
    };
    
    SplitsBrowser.Viewer = Viewer;

    /**
    * Shows a message that appears if SplitsBrowser is unable to load event
    * data.
    * @param {String} key - The key of the message to show.
    * @param {Object} params - Object mapping parameter names to values.
    */
    function showLoadFailureMessage(key, params) {
        d3.select("body")
          .append("h1")
          .text(getMessage("LoadFailedHeader"));
          
        d3.select("body")
          .append("p")
          .text(getMessageWithFormatting(key, params));
    }
    
    /**
    * Handles an asynchronous callback that fetched event data, by parsing the
    * data and starting SplitsBrowser.
    * @param {String} data - The data returned from the AJAX request.
    * @param {String} status - The status of the request.
    * @param {String|HTMLElement|undefined} - Optional HTML element that forms
    *     a 'banner' across the top of the page.  This can be specified by a
    *     CSS selector or the HTML element itself.
    */
    function readEventData(data, status, topDiv) {
        if (status === "success") {
            var eventData;
            try {
                eventData = SplitsBrowser.Input.parseEventData(data);
            } catch (e) {
                if (e.name === "InvalidData") {
                    showLoadFailureMessage("LoadFailedInvalidData", {"$$MESSAGE$$": e.message});
                    return;
                } else {
                    throw e;
                }
            }
            
            if (eventData === null) {
                showLoadFailureMessage("LoadFailedUnrecognisedData", {});
            } else {
                var viewer = new Viewer(topDiv);
                viewer.buildUi();
                viewer.setEvent(eventData);
                viewer.selectClasses([0]);
            }
        } else {
            showLoadFailureMessage("LoadFailedStatusNotSuccess", {"$$STATUS$$": status});
        }
    }
    
    /**
    * Handles the failure to read an event.
    * @param {jQuery.jqXHR} jqXHR - jQuery jqHXR object.
    * @param {String} textStatus - The text status of the request.
    * @param {String} errorThrown - The error message returned from the server.
    */
    function readEventDataError(jqXHR, textStatus, errorThrown) {
        showLoadFailureMessage("LoadFailedReadError", {"$$ERROR$$": errorThrown});
    }

    /**
    * Loads the event data in the given URL and starts SplitsBrowser.
    * @param {String} eventUrl - The URL that points to the event data to load.
    * @param {String|HTMLElement|undefined} - Optional HTML element that forms
    *     a 'banner' across the top of the page.  This can be specified by a
    *     CSS selector or the HTML element itself.
    */
    SplitsBrowser.loadEvent = function (eventUrl, topDiv) {
        $.ajax({
            url: eventUrl,
            data: "",
            success: function (data, status) { readEventData(data, status, topDiv); },
            dataType: "text",
            error: readEventDataError
        });
    };    
})();
