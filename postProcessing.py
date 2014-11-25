#!/usr/bin/python
__author__ = 'Mayank'
import json,random
import datetime
import time
import csv
import subprocess
from dateutil.parser import parse
from collections import  defaultdict

class PostProcessing():
    resources = "Resources/";
    corrFile = "corr_matrix_";
    static = "static/";
    quarter_files = defaultdict(str);
    exten_txt = ".txt"
    exten_csv = ".csv"

    def read_symbols(self,filename,exten,year):
        symCurr = ''
        symPrev = ''
        yearly_dates=[];
        yearly_dates.append(datetime.date(year,1,1));
        yearly_dates.append(datetime.date(year,4,1));
        yearly_dates.append(datetime.date(year,7,1));
        yearly_dates.append(datetime.date(year,10,1));
        yearly_dates.append(datetime.date(year+1,1,1))
        quarter_number = 1
        output = defaultdict(lambda :defaultdict(list))

        with open(self.resources+filename+exten,'rb') as f:
            reader = csv.reader(f)
            row = reader.next();
            row = reader.next();
            symPrev = row[0]
            day = parse(row[1]).date()
            quarter_number = self.get_quarter(day, yearly_dates);
            output[quarter_number][symPrev].append(row[3])


            for row in reader:
                symCurr = row[0]
                day = parse(row[1]).date()
                if(day>=yearly_dates[quarter_number]):
                    quarter_number+=1

                if symPrev != '' and symCurr != symPrev:
                    symPrev = symCurr
                    quarter_number = self.get_quarter(day,yearly_dates)
                #avgPriceList.append(row[3])
                output[quarter_number][symPrev].append(row[3])

        size_prev = 0;
        size_curr = 0
        size = defaultdict(int);
        count = defaultdict(int);
        for k1 in output:
            count[k1] = len(output[k1])
            for k2 in output[k1]:
                size_curr = len(output[k1][k2])
                if size_prev != 0 and size_prev != size_curr :
                    print "current prev: "+str(size_prev)
                    print "current size: "+str(size_curr)
                    print "Quarter: "+ str(k1)
                    print "Stock name: "+k2
                    output[k1][k2] = []
                    count[k1]-=1;
                else:
                    size_prev = size_curr
            size[k1] = size_prev
            size_prev=0

        outputFileList=defaultdict(file);

        for k1 in output:
            output_filename = filename+"_"+str(k1);
            self.quarter_files[k1] = output_filename
            outputFileList[k1]=open(self.resources+output_filename+self.exten_txt,'w');
            outputFileList[k1].write(str(size[k1])+ " "+str(count[k1])+"\n")
            for k2 in output[k1]:
                if(len(output[k1][k2])!=0):
                    outputFileList[k1].write(k2+" "+(" ".join(output[k1][k2]))+"\n")
            outputFileList[k1].close()

    def get_quarter(self,day, yearly_dates):
        quarter = 1;
        for i in range(0,len(yearly_dates)-1):
                    if(day>=yearly_dates[i+1]):
                        quarter = quarter + 1;
        return quarter;

    def createJson(self,inFile,exten):
        topWrapper = {}
        nodeName = []
        edgesName = [] 
        
        with open(self.resources+inFile+exten,'rb') as f:
            
            line = f.readline()
            while(line.strip() != "END"):
                line = line.split()
                temp = {}
                temp['name'] = line[1];
                temp['group'] = 1#random.randint(1,20);
                nodeName.append(temp)
                line = f.readline()
            topWrapper['nodes'] = nodeName

            line = f.readline()
            while(line.strip() != ""):
                line = line.split()
                temp = {}
                temp['source'] = int(line[0])
                temp['target'] = int(line[1])
                temp['value'] = float(line[2])
                edgesName.append(temp)
                line = f.readline()
            topWrapper['links'] = edgesName
        outFile = self.static+inFile + ".json";
        outF = open(outFile,'w');
        outF.write(json.dumps(topWrapper,sort_keys=True,indent=4, separators=(',', ': ')))
        outF.close()

    def divideIntoParts(self,inputFilename, extension, partitions):
        with open(self.resources+inputFilename+extension,'rb') as f:
            stock_list=[];
            line = f.readline()
            line=line.split();
            num_of_stocks = int(line[1]);
            num_of_days = int(line[0]);
            chunk = num_of_days/partitions;
            outputFileList=[];
            startIndices = [];
            endIndices = [];
            for i in range(0,partitions):
                outputFileList.append(open(self.resources+inputFilename+"_"+str(i+1)+".txt",'w'));
                startIndices.append((i*chunk)+1);
                if(i!=(partitions-1)):
                    endIndices.append(((i+1)*chunk)+1);
                else:
                    endIndices.append(num_of_days+1);
                outputFileList[i].write(str(endIndices[i]-startIndices[i]) +" "+ str(num_of_stocks))
            for k in range(0,num_of_stocks):
                line = f.readline();
                line = line.split();
                stock_list.append(line[0]);
                for j in range(0,partitions):
                    outputFileList[j].write('\n');
                    outputFileList[j].write(line[0]+" ");
                    outputFileList[j].write(" ".join(line[startIndices[j]:endIndices[j]]));
            for m in range(0,partitions):
                outputFileList[i].close();

        f.close();

    def get_correlation(self, inputFileName,extension):
        cmd ="./test.o ";
        cmd = cmd +self.resources+inputFileName+extension+" "+self.resources+self.corrFile+inputFileName+extension;
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print line,
        retval = p.wait()
        if(retval!=1):
            print "incorrect command: "+cmd;

    def main(self):
        inputFile = "y2013";
        exten = ".txt";
        extencsv = ".csv"
        #partitions = 4;
        #self.divideIntoParts(inputFile,exten,partitions);
        #for i in range(0,partitions):
        #    self.get_correlation(inputFile+"_"+str(i+1),exten);
        #    corr_filename = self.corrFile+inputFile+"_"+str(i+1);
        #    self.createJson(corr_filename, exten);
        self.read_symbols(inputFile,extencsv,2013)
        for key in self.quarter_files:
            self.get_correlation(self.quarter_files[key],self.exten_txt)
            self.createJson(self.corrFile+self.quarter_files[key],self.exten_txt)

if __name__ == '__main__':
    pp = PostProcessing()
    pp.main();