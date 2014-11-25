#!/usr/bin/python
__author__ = 'Mayank'
import urllib2
import json
import datetime
import time
import httplib
import urllib,urllib2
import csv
from collections import  defaultdict

class DataCollection():

    PUBLIC_API_URL = 'http://query.yahooapis.com/v1/public/yql'
    DATATABLES_URL = 'store://datatables.org/alltableswithkeys'
    HISTORICAL_URL = 'http://ichart.finance.yahoo.com/table.csv?s='
    FINANCE_TABLES = {'quotes': 'yahoo.finance.quotes',
                 'options': 'yahoo.finance.options',
                 'quoteslist': 'yahoo.finance.quoteslist',
                 'sectors': 'yahoo.finance.sectors',
                 'industry': 'yahoo.finance.industry'}

    def executeYQLQuery(self,yql):
        conn = httplib.HTTPConnection('query.yahooapis.com')
        queryString = urllib.urlencode({'q': yql, 'format': 'json', 'env': self.DATATABLES_URL})
        conn.request('GET', self.PUBLIC_API_URL + '?' + queryString)
        return json.loads(conn.getresponse().read())

    def collectHistoricalData(self,symbol):

        yql = 'select Date,High,Low,Close from csv where url=\'%s\'' \
              ' and columns=\"Date,Open,High,Low,Close,Volume,AdjClose\" and Date>="2014-08-14" and Date<= "2014-11-14"' \
               % (self.HISTORICAL_URL + symbol)
        results = self.executeYQLQuery(yql)
        try:
            # delete first row which contains column names
            del results['query']['results']['row'][0]
            return results['query']['results']['row']
        except:
            print "Execption: " + symbol
            pass


    def read_symbols(self,filename):
       symbolList = []
       with open(filename,'rb') as f:
           reader = csv.reader(f)
           for row in reader:
                symbol = row[0]
                symbolList.append(symbol)
       return symbolList

    def get_avgPriceList(self,results):
        avgPriceList = []
        for object in results:
            avg = (float(object['High']) + float(object['Low']))/2.0
            #avgPriceList.append(avg)
            avgPriceList.append(float(object['Close']));
        return avgPriceList

    def percentChangeList(self,avgPriceList):
        changeInValue = []
        for i in range(1,len(avgPriceList)):
            diff = (avgPriceList[i] - avgPriceList[i-1]) / avgPriceList[i-1]
            changeInValue.append(diff*100)
        return changeInValue

    def write_to_file(self,matrix,ouputfile):
        fileString = ""
        fileString += str(len(matrix['ADBE']))
        #print len(matrix['WDC'])
        fileString += " " + str(len(matrix)) + "\n"
        for k in matrix:
            fileString += k
            for item in matrix[k]:
                fileString += (" "+str(item))                    
            fileString += '\n'
        f = open(ouputfile,'w')
        f.write(fileString)
        f.close()

    def main(self,outfile):
        # result = dc.collectHistoricalData('googl')
        # print (result)
        # dc.build_matrix(result)
        # """
        filename = r'/Resources/symbols.csv'
        symbols = dc.read_symbols(filename)
        # print (symbols)

        # symbols = ['GOOGL']
        matrix = defaultdict(list)
        for item in symbols:
            result = self.collectHistoricalData(item)
            if result:
                avgpriceList = self.get_avgPriceList(result)
                # print(avgpriceList)
                #chgInPriceList = self.percentChangeList(avgpriceList)
                # print chgInPriceList
                matrix[item] = avgpriceList

        print str(len(matrix))
        self.write_to_file(matrix,outfile)

if __name__ == '__main__':
    dc = DataCollection()
    outfile = r'/Resources/output.txt'
    dc.main(outfile)
