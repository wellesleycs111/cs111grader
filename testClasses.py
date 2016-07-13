# testClasses.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# import modules from python standard library
import inspect
import re
import sys
import os

import cStringIO

class ReturnPrint:
    """Datatype returned by a function that also prints"""
    def __init__(self, returnval, printval):
        self.returnval = returnval
        self.printval = printval
    def __eq__(self, other):
        if type(self)==type(other):
            return self.returnval==other.returnval and self.printval==other.printval
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
    def __str__(self):
        return '\nReturned value: '+str(self.returnval)+'\n'+'Printed value:\n'+str(self.printval)


def capturePrint(func, arglist):
    """Redirect print output from func and return it alongwith the actual return value"""
    # adapted from https://wrongsideofmemphis.wordpress.com/2010/03/01/store-standard-output-on-a-variable-in-python/
    old_stdout = sys.stdout
    result = cStringIO.StringIO()
    sys.stdout = result
    returnval = func(*arglist)  # call the function
    printval = result.getvalue().strip('\n')  # strip newlines from ends
    sys.stdout = old_stdout
    return ReturnPrint(returnval, printval)



# Class which models a question in a project.  Note that questions have a
# maximum number of points they are worth, and are composed of a series of
# test cases
class Question(object):

    def raiseNotDefined(self):
        print 'Method not implemented: %s' % inspect.stack()[1][3]
        sys.exit(1)

    def __init__(self, questionDict):
        self.maxPoints = int(questionDict['max_points'])
        self.testCases = []

    def getMaxPoints(self):
        return self.maxPoints

    # Note that 'thunk' must be a function which accepts a single argument,
    # namely a 'grading' object
    def addTestCase(self, testCase, thunk):
        self.testCases.append((testCase, thunk))

    def execute(self, grades):
        self.raiseNotDefined()

# Question in which all test cases must be passed in order to receive credit
class PassAllTestsQuestion(Question):

    def execute(self, grades):
        # TODO: is this the right way to use grades?  The autograder doesn't seem to use it.
        testsFailed = False
        grades.assignZeroCredit()
        for _, f in self.testCases:
            if not f(grades):
                testsFailed = True
        if testsFailed:
            grades.fail("Tests failed.")
        else:
            grades.assignFullCredit()


# Question in which predict credit is given for test cases with a ``points'' property.
# All other tests are mandatory and must be passed.
class HackedPartialCreditQuestion(Question):

    def execute(self, grades):
        # TODO: is this the right way to use grades?  The autograder doesn't seem to use it.
        grades.assignZeroCredit()

        points = 0
        passed = True
        for testCase, f in self.testCases:
            testResult = f(grades)
            if "points" in testCase.testDict:
                if testResult: points += float(testCase.testDict["points"])
            else:
                passed = passed and testResult

        ## FIXME: Below terrible hack to match q3's logic
        if int(points) == self.maxPoints and not passed:
            grades.assignZeroCredit()
        else:
            grades.addPoints(int(points))


class Q6PartialCreditQuestion(Question):
    """Fails any test which returns False, otherwise doesn't effect the grades object.
    Partial credit tests will add the required points."""

    def execute(self, grades):
        grades.assignZeroCredit()

        results = []
        for _, f in self.testCases:
            results.append(f(grades))
        if False in results:
            grades.assignZeroCredit()

class PartialCreditQuestion(Question):
    """Fails any test which returns False, otherwise doesn't effect the grades object.
    Partial credit tests will add the required points."""

    def execute(self, grades):
        grades.assignZeroCredit()

        for _, f in self.testCases:
            if not f(grades):
                grades.assignZeroCredit()
                grades.fail("Tests failed.")
                return False



class NumberPassedQuestion(Question):
    """Grade is the number of test cases passed."""

    def execute(self, grades):
        grades.addPoints([f(grades) for _, f in self.testCases].count(True))

class WeightedCasesQuestion(Question):
    """Grade is sum of weights of test cases passed"""
    def execute(self,grades):
        grades.addPoints(sum([int(case.weight) for case, f in self.testCases if f(grades)==True]))

# Template modeling a generic test case
class TestCase(object):

    def raiseNotDefined(self):
        print 'Method not implemented: %s' % inspect.stack()[1][3]
        sys.exit(1)

    def getPath(self):
        return self.path

    def __init__(self, question, testDict):
        self.question = question
        self.testDict = testDict
        self.path = testDict['path']
        self.weight = testDict['weight']
        self.messages = []

    def __str__(self):
        self.raiseNotDefined()

    def execute(self, grades, moduleDict, solutionDict, showGrades):
        self.raiseNotDefined()

    def writeSolution(self, moduleDict, filePath):
        self.raiseNotDefined()
        return True

    # Tests should call the following messages for grading
    # to ensure a uniform format for test output.
    #
    # TODO: this is hairy, but we need to fix grading.py's interface
    # to get a nice hierarchical project - question - test structure,
    # then these should be moved into Question proper.
    def testPass(self, grades):
        #turns out this func and the next are never called - a func in tutorial test classes is called instead
        grades.addMessage('PASS: %s' % (self.path,))
        #grades.addMessage('    score: %s/%s' % (self.weight,self.weight,))
        for line in self.messages:
            grades.addMessage('    %s' % (line,))
        return True

    def testFail(self, grades):
        grades.addMessage('FAIL: %s' % (self.path,))
        #grades.addMessage('    score: 0/%s' % (self.weight,))
        for line in self.messages:
            grades.addMessage('    %s' % (line,))
        return False

    # This should really be question level?
    #
    def testPartial(self, grades, points, maxPoints):
        grades.addPoints(points)
        extraCredit = max(0, points - maxPoints)
        regularCredit = points - extraCredit

        grades.addMessage('%s: %s (%s of %s points)' % ("PASS" if points >= maxPoints else "FAIL", self.path, regularCredit, maxPoints))
        if extraCredit > 0:
            grades.addMessage('EXTRA CREDIT: %s points' % (extraCredit,))

        for line in self.messages:
            grades.addMessage('    %s' % (line,))

        return True

    def addMessage(self, message):
        self.messages.extend(message.split('\n'))

class EvalTest(TestCase): # moved from tutorialTestClasses

    def __init__(self, question, testDict):
        super(EvalTest, self).__init__(question, testDict)
        self.preamble = compile(testDict.get('preamble', ""), "%s.preamble" % self.getPath(), 'exec')
        self.test = compile(testDict['test'], "%s.test" % self.getPath(), 'eval')
        self.success = testDict['success']
        self.failure = testDict['failure']

    def evalCode(self, moduleDict):
        bindings = dict(moduleDict)
        try:
            exec self.preamble in bindings
            return eval(self.test, bindings)
        except Exception, inst:
            self.inst=inst
            return 'Exception was raised'

    def execute(self, grades, moduleDict, solutionDict, showGrades):
        result = self.evalCode(moduleDict)
        if result=='Exception was raised':
            if showGrades:
                grades.addMessage('FAIL: {0}\n\t{1}\n\tException raised: {2}\n\tExpected result: {3}\n\tscore: {4}'.format(self.path,self.failure,self.inst,solutionDict['result'],'0/'+self.weight))
            else:
                grades.addMessage('FAIL: {0}\n\t{1}\n\tException raised: {2}\n\tExpected result: {3}\n'.format(self.path,self.failure,result[2],solutionDict['result']))
            grades.addErrorHints(self.inst)
            return False
        elif result == solutionDict['result']:
            if showGrades:
                grades.addMessage('PASS: {0}\n\t{1}\n\tscore: {2}'.format(self.path, self.success, self.weight+'/'+self.weight))
            else:
                grades.addMessage('PASS: {0}\n\t{1}\n'.format(self.path, self.success))
            return True
        else:
                if showGrades:
                    grades.addMessage('FAIL: {0}\n\t{1}\n\tstudent result: {2}\n\tcorrect result: {3}\n\tscore: {4}'.format(self.path, self.failure, result, solutionDict['result'],'0/'+self.weight))
                else:
                    grades.addMessage('FAIL: {0}\n\t{1}\n\tstudent result: {2}\n\tcorrect result: {3}\n'.format(self.path, self.failure, result, solutionDict['result']))
        return False

    def writeSolution(self, moduleDict, filePath):
        handle = open(filePath, 'w')
        handle.write('# This is the solution file for %s.\n' % self.path)
        handle.write('# The result of evaluating the test must equal the below when cast to a string.\n')
        handle.write('result: "%s"\n' % self.evalCode(moduleDict))
        handle.close()
        return True

class ImageTest(EvalTest):

    def execute(self,grades,moduleDict,solutionDict,showGrades):
        result = self.evalCode(moduleDict)
        # result will be a cs1graphics Canvas
        userimage = os.path.splitext(os.path.basename(self.path))[0]+'.png'
        result.saveToFile(userimage)
        grades.addMessage('IMAGE,{0},{1},{2}'.format(self.path, solutionDict['result'],userimage))
        return True


class PrintTest(EvalTest):

    def __init__(self,question,testDict):
        testDict['test']='projectTestClasses.capturePrint('+testDict['test'].split('(')[0]+',['+testDict['test'][:-1].split('(')[1]+'])'
        super(PrintTest, self).__init__(question, testDict)
