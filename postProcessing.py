#!/usr/bin/python
__author__ = 'Mayank'
import json
import datetime
import csv
import subprocess
import os
from dateutil.parser import parse
from collections import defaultdict
from Pycluster import *

class PostProcessing():
    resources = "/Users/sparmar/Documents/Fall2014/DataScience/code/StockDataAnalysis/Resources/"
    corrFile = "corr_matrix_"
    static = "/Users/sparmar/Documents/Fall2014/DataScience/code/StockDataAnalysis/static/"
    quarter_files = defaultdict(str)
    exten_txt = ".txt"
    exten_csv = ".csv"
    # This will be the directory in which result will be generated
    directory = ''

    def read_symbols(self, year, exten, duration):
        filename = 'y' + str(year)
        yearly_dates = self.populateYearlyDates(year, duration)
        output = defaultdict(lambda: defaultdict(list))

        with open(self.resources + filename + exten, 'rb') as f:
            reader = csv.reader(f)
            # Ignore first line - header
            reader.next()

            row = reader.next()
            symPrev = ''
            symCurr = row[0]
            day = parse(row[1]).date()
            bucket_num = self.get_bucket(day, yearly_dates)
            output[bucket_num][symCurr].append(row[3])

            for row in reader:
                symCurr = row[0]
                day = parse(row[1]).date()
                try:
                    if bucket_num+1 < len(yearly_dates) and day >= yearly_dates[bucket_num+1]:
                        bucket_num += 1
                    if symPrev != '' and symCurr != symPrev:
                        # New Symbol - reset the bucket number
                        bucket_num = self.get_bucket(day, yearly_dates)
                    # avgPriceList.append(row[3])
                    output[bucket_num][symCurr].append(row[3])
                    symPrev = symCurr
                except:
                    print row
                    print bucket_num
                    print yearly_dates
                    exit(1)

        size_prev = 0
        size = defaultdict(int)
        count = defaultdict(int)

        for k1 in output:
            count[k1] = len(output[k1])
            for k2 in output[k1]:
                size_curr = len(output[k1][k2])
                if size_prev != 0 and size_prev != size_curr:
                    print "Discarding:"
                    print "\tStock name: " + k2
                    print "\tBucket: " + str(k1)
                    print "\tcurrent prev: " + str(size_prev)
                    print "\tcurrent size: " + str(size_curr)
                    output[k1][k2] = []
                    count[k1] -= 1
                else:
                    size_prev = size_curr
            size[k1] = size_prev
            size_prev = 0

        outputFileList = defaultdict(file)

        for k1 in output:
            output_filename = filename + "_" + str(k1);
            self.quarter_files[k1] = output_filename
            if not os.path.exists(self.resources + self.directory):
                os.makedirs(self.resources + self.directory)
            outputFileList[k1] = open(self.resources + self.directory + output_filename + self.exten_txt, 'w')
            outputFileList[k1].write(str(size[k1]) + " " + str(count[k1]) + "\n")
            for k2 in output[k1]:
                if (len(output[k1][k2]) != 0):
                    outputFileList[k1].write(k2 + " " + (" ".join(output[k1][k2])) + "\n")
            outputFileList[k1].close()

    def populateYearlyDates(self, year, duration):
        # currently supported months = 3,6,12
        yearly_dates = []
        if duration == 3:
            yearly_dates.append(datetime.date(year, 1, 1))
            yearly_dates.append(datetime.date(year, 4, 1))
            yearly_dates.append(datetime.date(year, 7, 1))
            yearly_dates.append(datetime.date(year, 10, 1))
        elif duration == 6:
            yearly_dates.append(datetime.date(year, 1, 1))
            yearly_dates.append(datetime.date(year, 7, 1))
        return yearly_dates

    def get_bucket(self, day, yearly_dates):
        bucket = 0
        for i in range(0, len(yearly_dates) - 1):
            if day >= yearly_dates[i + 1]:
                bucket += 1
        return bucket

    def createJson(self, inFile, exten,clusters):
        topWrapper = {}
        nodeName = []
        edgesName = []
        # For k-medoids
        corrMatrix = []

        with open(self.resources + self.directory + inFile + exten, 'rb') as f:
            line = f.readline()
            while line.strip() != "END":
                line = line.split()
                temp = {}
                temp['name'] = line[1]
                temp['group'] = 1  # random.randint(1,20);
                nodeName.append(temp)
                line = f.readline()
            topWrapper['nodes'] = nodeName

            curIndex = 0
            prevIndex = 0
            curList = []
            line = f.readline()
            while (line.strip() != ""):
                line = line.split()
                temp = {}
                temp['source'] = int(line[0])
                temp['target'] = int(line[1])
                temp['value'] = float(line[2])
                curIndex = temp['source']
                if prevIndex != curIndex:
                    corrMatrix.append(list(curList))
                    del curList[:]
                curList.append(1-temp['value'])
                edgesName.append(temp)
                prevIndex = curIndex
                line = f.readline()
            topWrapper['links'] = edgesName
            corrMatrix.append(curList)

        print "corr matrix len = " + str(len(corrMatrix))
        print "corr matrix0 len = " + str(len(corrMatrix[0]))
        clusterid, error, nfound = kmedoids(corrMatrix, clusters, npass=15, initialid=None)
        print clusterid
        i = 0
        for node in topWrapper['nodes']:
            node['group'] = int(clusterid[i])
            i += 1

        if not os.path.exists(self.static + self.directory):
            os.makedirs(self.static + self.directory)
        outFile = self.static + self.directory + inFile + ".json"
        outF = open(outFile, 'w')
        outF.write(json.dumps(topWrapper, sort_keys=True, indent=4, separators=(',', ': ')))
        outF.close()
        return outFile

        # for mat in corrMatrix:
        #   print " ".join(map(str,mat))
        #  print clusterid
        # print error
        # print nfound
        # print '*' * 10
        #
        # tree = treecluster(data=None, mask=None, weight=None, transpose=0,
        #                method='m', dist='c', distancematrix=corrMatrix)
        # print tree


    def get_correlation(self, inputFileName, extension):
        cmd = "/Users/sparmar/Documents/Fall2014/DataScience/code/StockDataAnalysis/test.o "
        cmd = cmd + self.resources + self.directory + inputFileName + extension + " " \
              + self.resources + self.directory + self.corrFile + inputFileName + extension
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print line,
        retval = p.wait()
        if retval != 1:
            print "incorrect command: " + cmd

    def main(self, inputYear, duration,clusters):

        self.directory = str(inputYear) + '/' + str(duration) + '/'
        # Clean up before you start
        self.remove_files(self.static + self.directory, 'json')
        self.remove_files(self.resources + self.directory, 'txt')

        # Start
        exten = ".txt"
        extencsv = ".csv"
        outfiles = []
        self.read_symbols(inputYear, extencsv, duration)

        if duration == 3:
            assert len(self.quarter_files) == 4
        elif duration == 6:
            assert len(self.quarter_files) == 2
        else:
            assert len(self.quarter_files) == 1

        for key in self.quarter_files:
            print "key = " + str(key)
            self.get_correlation(self.quarter_files[key], self.exten_txt)
            outfile = self.createJson(self.corrFile + self.quarter_files[key], self.exten_txt,clusters)
            outfile = outfile[outfile.find('static')-1:]
            outfiles.append(outfile)
        return outfiles

    @staticmethod
    def remove_files(path, ext):
        for root, dirs, files in os.walk(path):
            for currentFile in files:
                if currentFile.lower().endswith(ext):
                    os.remove(os.path.join(root, currentFile))

if __name__ == '__main__':
    pp = PostProcessing()
    import sys
    inputYear = int(sys.argv[1])
    duration = int(sys.argv[2])
    pp.main(inputYear, duration, 2)
