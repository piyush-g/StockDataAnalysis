__author__ = 'piyush'

import datetime
from dateutil.parser import parse
import csv
from collections import  defaultdict

class Sample:
    resources = "Resources/";
    def read_symbols(self,filename,exten,year):
        #avgPriceList = []
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
            print row;
            row = reader.next();
            print row;
            symPrev = row[0]
            day = parse(row[1]).date()
            quarter_number = self.get_quarter(day, yearly_dates);
            output[quarter_number][symPrev].append(row[3])


            for row in reader:
                print row
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
                print "current prev: "+str(size_prev)
                print "current size: "+str(size_curr)
                if size_prev != 0 and size_prev != size_curr :
                    print "current prev: "+str(size_prev)
                    print "current size: "+str(size_curr)
                    output[k1][k2] = []
                    count[k1]-=1;
                else:
                    size_prev = size_curr
            size[k1] = size_prev
            size_prev=0

        outputFileList=defaultdict(file);

        for k1 in output:
            outputFileList[k1]=open(self.resources+filename+"_"+str(k1)+".txt",'w');
            outputFileList[k1].write(str(size[k1])+ " "+str(count[k1])+"\n")
            for k2 in output[k1]:
                print k2+" : " + str(len(output[k1][k2]))
                if(len(output[k1][k2])!=0):
                    outputFileList[k1].write(k2+" "+(" ".join(output[k1][k2]))+"\n")
            outputFileList[k1].close()

    def get_quarter(self,day, yearly_dates):
        quarter = 1;
        for i in range(0,len(yearly_dates)-1):
                    if(day>=yearly_dates[i+1]):
                        quarter = quarter + 1;
        return quarter;

    def main(self):
        matrix = defaultdict(list)
        self.read_symbols("a",".csv",2013)
        for key in matrix:
            print "key: "+key+" value: "+(" ".join(matrix[key]))

if __name__ == '__main__':
    t = Sample()
    t.main();